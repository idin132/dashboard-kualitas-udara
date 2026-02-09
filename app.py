import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard AQI Nasional", layout="wide")

# ==============================
# FUNGSI KATEGORI AQI
# ==============================
def get_aqi_category(aqi):
    if aqi <= 50:
        return 'Good', '#00e400'
    elif aqi <= 100:
        return 'Satisfactory', '#ffff00'
    elif aqi <= 200:
        return 'Moderate', '#ff7e00'
    elif aqi <= 300:
        return 'Poor', '#ff0000'
    elif aqi <= 400:
        return 'Very Poor', '#8f3f97'
    else:
        return 'Severe', '#7e0023'

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    df_city = pd.read_csv('avg_aqi_per_city.csv', sep='\t', names=['City', 'Avg_AQI'])
    df_hour = pd.read_csv('avg_aqi_per_hour.csv', sep='\t', names=['Hour', 'Avg_AQI'])
    return df_city, df_hour

df_city, df_hour = load_data()

# ==============================
# SIDEBAR MENU
# ==============================
st.sidebar.title("🌫️ Dashboard AQI")

menu = st.sidebar.radio(
    "Navigasi",
    [
        "🏠 Ringkasan",
        "📊 Analisis Kota",
        "⏰ Tren Waktu",
        "🌍 Distribusi",
        "🌙 Siang vs Malam"
    ]
)

st.sidebar.divider()

city_list = ["Semua Kota"] + sorted(df_city['City'].unique().tolist())
selected_city = st.sidebar.selectbox("Pilih Kota", city_list)

# ==============================
# FILTER LOGIC
# ==============================
if selected_city == "Semua Kota":
    display_df = df_city.sort_values(by='Avg_AQI', ascending=False).head(10)
    focus_city_data = display_df.iloc[0]
else:
    focus_city_data = df_city[df_city['City']==selected_city].iloc[0]
    display_df = df_city.sort_values(by='Avg_AQI', ascending=False).head(10)

# ==============================
# HALAMAN 1: RINGKASAN
# ==============================
if menu == "🏠 Ringkasan":

    st.title("🌫️ Dashboard Monitoring Kualitas Udara")

    avg_nasional = df_city['Avg_AQI'].mean()
    worst_city = df_city.sort_values(by='Avg_AQI', ascending=False).iloc[0]
    best_city = df_city.sort_values(by='Avg_AQI').iloc[0]

    col1,col2,col3 = st.columns(3)

    col1.metric("Rata-rata AQI Nasional", f"{avg_nasional:.1f}")
    col2.metric("Kota Terburuk", worst_city['City'])
    col3.metric("Kota Terbaik", best_city['City'])

    st.info("""
    Dashboard ini menampilkan kondisi kualitas udara berdasarkan data AQI.
    Tujuan analisis adalah mengidentifikasi:
    - Kota dengan polusi tertinggi
    - Waktu paling berbahaya
    - Pola distribusi polusi
    """)

# ==============================
# HALAMAN 2: ANALISIS KOTA
# ==============================
elif menu == "📊 Analisis Kota":

    st.title("📊 Perbandingan AQI Antar Kota")

    status, color = get_aqi_category(focus_city_data['Avg_AQI'])

    col1, col2 = st.columns([2,1])

    with col1:
        fig, ax = plt.subplots(figsize=(10,6))
        colors = ['#FFD700' if c == selected_city else '#4682B4' for c in display_df['City']]
        sns.barplot(x='Avg_AQI', y='City', data=display_df, palette=colors, ax=ax)
        ax.set_title("Top 10 Kota dengan Polusi Tertinggi")
        st.pyplot(fig)

    with col2:
        st.metric("AQI Kota Fokus", f"{focus_city_data['Avg_AQI']:.2f}")
        st.markdown(f"<h2 style='color:{color}'>{status}</h2>", unsafe_allow_html=True)

    st.success("""
    **Insight:**  
    Grafik ini menunjukkan kota dengan tingkat polusi tertinggi.  
    Kota dengan AQI tertinggi perlu menjadi prioritas kebijakan lingkungan.  
    """)

# ==============================
# HALAMAN 3: TREN WAKTU
# ==============================
elif menu == "⏰ Tren Waktu":

    st.title("⏰ Tren AQI Berdasarkan Jam")

    df_hour = df_hour.sort_values(by='Hour')
    worst_hour = df_hour.loc[df_hour['Avg_AQI'].idxmax()]

    st.warning(f"Polusi tertinggi terjadi pukul {int(worst_hour['Hour'])}:00")

    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(x='Hour', y='Avg_AQI', data=df_hour, marker='o', ax=ax)
    ax.set_xticks(range(0,24))
    st.pyplot(fig)

    st.info("""
    **Insight:**  
    Polusi biasanya meningkat pada jam sibuk kendaraan.  
    Waktu ini berisiko tinggi bagi:
    - Anak-anak
    - Lansia
    - Penderita asma  
    """)

# ==============================
# HALAMAN 4: DISTRIBUSI
# ==============================
elif menu == "🌍 Distribusi":

    st.title("🌍 Distribusi Kategori AQI")

    df_city['Category'] = df_city['Avg_AQI'].apply(lambda x: get_aqi_category(x)[0])

    cat_order = ['Good','Satisfactory','Moderate','Poor','Very Poor','Severe']
    category_counts = df_city['Category'].value_counts().reindex(cat_order).fillna(0).reset_index()

    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(x='count', y='Category', data=category_counts, ax=ax)
    st.pyplot(fig)

    total = len(df_city)
    extreme = (df_city['Avg_AQI']>200).sum()

    st.metric("Kota AQI > 200", extreme, f"{extreme/total*100:.1f}%")

    st.info("""
    **Insight:**  
    Distribusi ini menunjukkan mayoritas kota berada pada kategori tertentu.  
    Jika banyak kota berada di kategori Poor atau Very Poor,
    maka kondisi udara nasional perlu perhatian serius.
    """)

# ==============================
# HALAMAN 5: SIANG VS MALAM
# ==============================
elif menu == "🌙 Siang vs Malam":

    st.title("🌙 Perbandingan Polusi Siang vs Malam")

    def time_group(hour):
        return 'Siang' if 6 <= hour <= 18 else 'Malam'

    df_hour['Waktu'] = df_hour['Hour'].apply(time_group)
    time_avg = df_hour.groupby('Waktu')['Avg_AQI'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(x='Waktu', y='Avg_AQI', data=time_avg, ax=ax)
    st.pyplot(fig)

    st.info("""
    **Insight:**  
    Malam hari sering memiliki polusi tinggi karena fenomena inversi suhu.  
    Udara kotor terjebak di permukaan dan tidak naik ke atmosfer.
    """)
