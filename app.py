import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard Kualitas Udara", layout="wide")

# --- 1. FUNGSI KATEGORI (Logika Bisnis) ---
def get_aqi_category(aqi):
    if aqi <= 50:
        return 'Good', '#00e400'  # Hijau
    elif aqi <= 100:
        return 'Satisfactory', '#ffff00'  # Kuning
    elif aqi <= 200:
        return 'Moderate', '#ff7e00'  # Oranye
    elif aqi <= 300:
        return 'Poor', '#ff0000'  # Merah
    elif aqi <= 400:
        return 'Very Poor', '#8f3f97'  # Ungu
    else:
        return 'Severe', '#7e0023'  # Merah Tua

# --- 2. LOAD DATA ---
@st.cache_data
def load_data():
    # Load data city
    df_city = pd.read_csv('avg_aqi_per_city.csv', sep='\t', names=['City', 'Avg_AQI'])
    # Load data hour
    df_hour = pd.read_csv('avg_aqi_per_hour.csv', sep='\t', names=['Hour', 'Avg_AQI'])
    return df_city, df_hour

df_city, df_hour = load_data()

# --- 3. SIDEBAR & FILTER ---
st.sidebar.header("Filter & Navigasi")

# Filter Kota
city_list = ["Semua Kota"] + sorted(df_city['City'].unique().tolist())
selected_city = st.sidebar.selectbox("Pilih Kota untuk Dianalisis:", city_list)

st.sidebar.divider()
st.sidebar.header("Panduan Kategori AQI")
st.sidebar.info("""
- **0-50 (Good)**: Udara bersih.
- **51-100 (Satisfactory)**: Udara cukup baik.
- **101-200 (Moderate)**: Gejala muncul pada orang sensitif.
- **201-300 (Poor)**: Gangguan pernapasan.
- **301-400 (Very Poor)**: Risiko kesehatan serius.
- **400+ (Severe)**: Dampak buruk bagi semua.
""")

# --- 4. LOGIKA FILTERING ---
if selected_city == "Semua Kota":
    # Data default (Top 10 terburuk)
    display_df = df_city.sort_values(by='Avg_AQI', ascending=False).head(10)
    focus_city_data = display_df.iloc[0] # Ambil yang tertinggi sebagai highlight
    title_suffix = "10 Kota dengan Polusi Tertinggi"
else:
    # Ambil data kota yang dipilih
    city_data = df_city[df_city['City'] == selected_city].iloc[0]
    focus_city_data = city_data
    
    # Untuk grafik, kita tampilkan Top 10 + Kota pilihan (jika tidak ada di top 10)
    top_10 = df_city.sort_values(by='Avg_AQI', ascending=False).head(10)
    if selected_city not in top_10['City'].values:
        display_df = pd.concat([top_10, df_city[df_city['City'] == selected_city]]).sort_values(by='Avg_AQI', ascending=False)
    else:
        display_df = top_10
    title_suffix = f"Posisi {selected_city} dalam Peta Polusi"

# --- 5. HEADER ---
st.title("Monitoring Kualitas Udara (AQI Analysis)")
st.markdown(f"Menganalisis data polusi untuk: **{selected_city}**")

# --- 6. SEKSI 1: ANALISIS KOTA ---
st.header(" Kondisi Udara di Berbagai Kota")
status, color = get_aqi_category(focus_city_data['Avg_AQI'])

col1, col2 = st.columns([2, 1])
with col1:
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    # Buat warna custom: Highlight kota terpilih
    colors = ['#FFD700' if c == selected_city else '#4682B4' for c in display_df['City']]
    
    sns.barplot(x='Avg_AQI', y='City', data=display_df, palette=colors, ax=ax1)
    ax1.set_title(title_suffix, fontsize=14)
    st.pyplot(fig1)

with col2:
    st.subheader("Detail Fokus")
    st.write(f"Kota: **{focus_city_data['City']}**")
    st.metric(label="Rata-rata AQI", value=f"{focus_city_data['Avg_AQI']:.2f}")
    st.markdown(f"Status: <span style='color:{color}; font-weight:bold; font-size:24px;'>{status}</span>", unsafe_allow_html=True)
    
    if selected_city == "Semua Kota":
        st.write("Menampilkan kota dengan tingkat polusi paling kritis secara nasional.")
    else:
        rank = df_city.sort_values(by='Avg_AQI', ascending=False)['City'].tolist().index(selected_city) + 1
        st.write(f"Kota ini berada di peringkat ke-**{rank}** dari {len(df_city)} kota terpantau.")

# --- 7. SEKSI 2: TREN WAKTU (GLOBAL) ---
st.divider()
st.header("Kapan Polusi Paling Berbahaya? (Rata-rata Nasional)")
df_hour = df_hour.sort_values(by='Hour')
worst_hour = df_hour.loc[df_hour['Avg_AQI'].idxmax()]
h_status, h_color = get_aqi_category(worst_hour['Avg_AQI'])

col3, col4 = st.columns([1, 2])
with col3:
    st.subheader("Analisis Waktu")
    st.write(f"Secara umum, polusi memuncak pada pukul **{int(worst_hour['Hour'])}:00**.")
    st.warning(f"Saran: Batasi aktivitas luar ruangan pada jam tersebut.")
    st.info("Data ini merupakan pola waktu agregat dari seluruh kota yang terpantau.")

with col4:
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.lineplot(x='Hour', y='Avg_AQI', data=df_hour, marker='o', color='darkred', ax=ax2)
    ax2.set_xticks(range(0, 24))
    ax2.set_ylabel("Rata-rata AQI Nasional")
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

# --- 8. SEKSI 3: DISTRIBUSI KATEGORI ---
st.divider()
st.header("Distribusi Kualitas Udara Seluruh Wilayah")
col5, col6 = st.columns([2, 1])

with col5:
    df_city['Category'] = df_city['Avg_AQI'].apply(lambda x: get_aqi_category(x)[0])
    cat_order = ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe']
    category_counts = df_city['Category'].value_counts().reindex(cat_order).fillna(0).reset_index()
    
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    # Gunakan warna sesuai standar kategori AQI
    cat_colors = ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97', '#7e0023']
    sns.barplot(x='count', y='Category', data=category_counts, palette=cat_colors, ax=ax3)
    ax3.set_title("Jumlah Kota Berdasarkan Kategori")
    st.pyplot(fig3)

with col6:
    st.subheader("Ringkasan Sebaran")
    total_cities = len(df_city)
    good_cities = category_counts[category_counts['Category'] == 'Good']['count'].values[0]
    st.write(f"Dari total **{total_cities}** kota, hanya **{int(good_cities)}** kota yang memiliki kategori 'Good'.")
    
    # Metrik Polusi Ekstrem
    threshold = 200
    extreme_count = (df_city['Avg_AQI'] > threshold).sum()
    st.metric(
        label="Kota dengan Polusi Tinggi (>200 AQI)", 
        value=f"{extreme_count} Kota",
        delta=f"{(extreme_count/total_cities)*100:.1f}% dari total",
        delta_color="inverse"
    )

# --- 7. SEKSI 4: SIANG VS MALAM (BARU) ---
st.divider()
st.header(" Perbandingan Polusi Siang vs Malam")
def time_group(hour):
    return 'Siang (06:00-18:00)' if 6 <= hour <= 18 else 'Malam (18:00-06:00)'

df_hour['Waktu'] = df_hour['Hour'].apply(time_group)
time_avg = df_hour.groupby('Waktu')['Avg_AQI'].mean().reset_index()

col7, col8 = st.columns(2)
with col7:
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    sns.barplot(x='Waktu', y='Avg_AQI', data=time_avg, palette='coolwarm', ax=ax4)
    ax4.set_title("Rata-rata AQI: Siang vs Malam")
    st.pyplot(fig4)

with col8:
    st.subheader("Insight Waktu")
    st.write("""
    Perbandingan ini sangat krusial bagi warga yang aktif berolahraga. 
    
    * **Siang**: Biasanya dipengaruhi asap kendaraan dan aktivitas industri.
    * **Malam**: Dipengaruhi oleh kondisi atmosfer (Inversi suhu) yang membuat udara kotor tidak bisa naik ke atas.
    """)
    # Metrik Polusi Ekstrem
    threshold = 200
    extreme_count = (df_city['Avg_AQI'] > threshold).sum()
    st.metric(
        label="Jumlah Kota dengan Polusi Sangat Tinggi (>200 AQI)", 
        value=f"{extreme_count} Kota",
        delta=f"{(extreme_count/len(df_city))*100:.1f}% dari total kota",
        delta_color="inverse"
    )
    
st.divider()
st.caption("Dashboard dikembangkan menggunakan Streamlit & Hadoop untuk Monitoring Lingkungan.")