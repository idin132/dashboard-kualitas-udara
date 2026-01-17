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
    # Pastikan file .csv berada di folder yang sama dengan skrip ini
    df_city = pd.read_csv('avg_aqi_per_city.csv', sep='\t', names=['City', 'Avg_AQI'])
    df_hour = pd.read_csv('avg_aqi_per_hour.csv', sep='\t', names=['Hour', 'Avg_AQI'])
    return df_city, df_hour

df_city, df_hour = load_data()

# --- 3. HEADER & SIDEBAR ---
st.title("📊 Monitoring Kualitas Udara (AQI Analysis)")
st.markdown("""
Dashboard ini menyajikan analisis kualitas udara berdasarkan data yang diolah menggunakan ekosistem **Hadoop**. 
Tujuannya adalah mengidentifikasi titik polusi tertinggi dan memahami pola polusi berdasarkan waktu.
""")

with st.sidebar:
    st.header("📖 Panduan Kategori AQI")
    st.info("""
    - **0-50 (Good)**: Udara bersih.
    - **51-100 (Satisfactory)**: Udara cukup baik.
    - **101-200 (Moderate)**: Gejala muncul pada orang sensitif.
    - **201-300 (Poor)**: Gangguan pernapasan bagi masyarakat umum.
    - **301-400 (Very Poor)**: Risiko kesehatan serius.
    - **400+ (Severe)**: Dampak buruk bagi semua orang.
    """)

# --- 4. SEKSI 1: PERBANDINGAN KOTA (EKSISTING) ---
st.header("📍 Kondisi Udara di Berbagai Kota")
top_10 = df_city.sort_values(by='Avg_AQI', ascending=False).head(10)
worst_city = top_10.iloc[0]
status, color = get_aqi_category(worst_city['Avg_AQI'])

col1, col2 = st.columns([2, 1])
with col1:
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(x='Avg_AQI', y='City', data=top_10, palette='flare', ax=ax1)
    ax1.set_title('10 Kota dengan Polusi Tertinggi', fontsize=14)
    st.pyplot(fig1)

with col2:
    st.subheader("Wawasan Kota")
    st.write(f"Kota dengan polusi terburuk: **{worst_city['City']}**")
    st.metric(label="Rata-rata AQI", value=f"{worst_city['Avg_AQI']:.2f}")
    st.markdown(f"Status: <span style='color:{color}; font-weight:bold; font-size:24px;'>{status}</span>", unsafe_allow_html=True)
    st.write("Grafik ini menunjukkan kota-kota yang memerlukan tindakan mitigasi polusi segera.")

# --- 5. SEKSI 2: TREN WAKTU (EKSISTING) ---
st.divider()
st.header("⏰ Kapan Polusi Paling Berbahaya?")
df_hour = df_hour.sort_values(by='Hour')
worst_hour = df_hour.loc[df_hour['Avg_AQI'].idxmax()]
h_status, h_color = get_aqi_category(worst_hour['Avg_AQI'])

col3, col4 = st.columns([1, 2])
with col3:
    st.subheader("Analisis Waktu")
    st.write(f"Polusi memuncak pada pukul **{int(worst_hour['Hour'])}:00**.")
    st.warning(f"Saran: Batasi aktivitas luar ruangan pada jam tersebut karena udara masuk kategori **{h_status}**.")
    st.write("Biasanya polusi meningkat di malam hari karena suhu udara yang mendingin memerangkap polutan di permukaan.")

with col4:
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.lineplot(x='Hour', y='Avg_AQI', data=df_hour, marker='o', color='darkred', ax=ax2)
    ax2.set_xticks(range(0, 24))
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

# --- 6. SEKSI 3: DISTRIBUSI KATEGORI (BARU) ---
st.divider()
st.header("📊 Distribusi Kualitas Udara (Cakupan Kota)")
col5, col6 = st.columns([2, 1])

with col5:
    # Mengelompokkan semua kota berdasarkan kategorinya
    df_city['Category'] = df_city['Avg_AQI'].apply(lambda x: get_aqi_category(x)[0])
    cat_order = ['Good', 'Satisfactory', 'Moderate', 'Poor', 'Very Poor', 'Severe']
    category_counts = df_city['Category'].value_counts().reindex(cat_order).fillna(0).reset_index()
    
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.barplot(x='count', y='Category', data=category_counts, palette='viridis', ax=ax3)
    ax3.set_title("Jumlah Kota di Setiap Kategori")
    st.pyplot(fig3)

with col6:
    st.subheader("Seberapa Sehat Kota Kita?")
    st.write("""
    Visualisasi ini memberikan gambaran besar: Apakah mayoritas kota yang kita pantau dalam kondisi aman? 
    
    Jika batang **'Moderate'** atau **'Poor'** lebih panjang dari **'Good'**, ini menunjukkan masalah polusi udara bersifat sistemik di banyak wilayah, bukan hanya di satu kota.
    """)

# --- 7. SEKSI 4: SIANG VS MALAM (BARU) ---
st.divider()
st.header("🌙 Perbandingan Polusi Siang vs Malam")
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