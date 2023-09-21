import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Menambahkan Fungsi Create Dataframe
def create_customer_byHour(df):
    customer_byHour_df = pd.DataFrame(df.groupby(by=['hr']).agg({
        "casual": 'sum',
        "registered": 'sum',
        "cnt": 'sum'
    }))
    customer_byHour_df = customer_byHour_df.sort_values(by='cnt', ascending=False)
    customer_byHour_df.reset_index(inplace=True)

    return customer_byHour_df

def create_customer_byYear(df):
    customer_byYear = df.groupby('yr').agg({
        "casual": 'sum',
        "registered": 'sum'
    }).reset_index()

    customer_byYear_df = pd.DataFrame({
        'yr': [2011, 2012],
        'casual': customer_byYear['casual'],
        'registered': customer_byYear['registered']
    })

    return customer_byYear_df

def create_customer_byType(df):
    # Melt the DataFrame
    customer_byType_df = df.melt(id_vars='yr', var_name='tipe_pelanggan', value_name='jumlah_customer')

    # Rename the columns
    customer_byType_df.rename(columns={'yr': 'year'}, inplace=True)

    # Sort the DataFrame by year
    customer_byType_df.sort_values(by='year', inplace=True)

    # Reset the index
    customer_byType_df.reset_index(drop=True, inplace=True)

    customer_byType_df['year'] = customer_byType_df['year'].astype('category')
    customer_byType_df['tipe_pelanggan'] = customer_byType_df['tipe_pelanggan'].astype('category')

    return customer_byType_df

def create_customer_byWorkingday(df):
    customer_byWorkingday_df = df.groupby(by='workingday').agg({
        'cnt': 'sum'
    }).reset_index()

    customer_byWorkingday_df = pd.DataFrame({
        'Week': ['Holiday/Weekend', 'Workingday'],
        'Jumlah_Customer': customer_byWorkingday_df['cnt']
    })

    return customer_byWorkingday_df

def create_customer_bySeason(df):
    count_customer_bySeason = df.groupby(by=['yr', 'season']).agg({
        'cnt': 'sum'
    }).reset_index()

    def check_season(season):
        if season == 1:
            return 'Springer'
        elif season == 2:
            return 'Summer'
        elif season == 3:
            return 'Fall'
        elif season == 4:
            return 'Winter'

    count_customer_bySeason_df = pd.DataFrame({
        'yr': count_customer_bySeason.yr.apply(lambda x: 2011 if x == 0 else 2012),
        'season': count_customer_bySeason.season.apply(lambda x: check_season(x)),
        'cnt': count_customer_bySeason['cnt']
    })

    count_customer_bySeason_df['yr'] = count_customer_bySeason_df['yr'].astype(str)

    return count_customer_bySeason_df

def create_customer_byWeather(df):
    count_customer_byWeather = df.groupby(by=['yr', 'weathersit']).agg({
        'cnt': 'sum'
    }).reset_index()

    count_customer_byWeather_df = pd.DataFrame({
        'yr': count_customer_byWeather.yr.apply(lambda x: 2011 if x == 0 else 2012),
        'weathersit': count_customer_byWeather['weathersit'],
        'cnt': count_customer_byWeather['cnt']
    })

    count_customer_byWeather_df['yr'] = count_customer_byWeather_df['yr'].astype(str)

    return count_customer_byWeather_df

main_df = pd.read_csv('https://raw.githubusercontent.com/IhlasulMufti/Bike-Sharing-Analytic/main/dashboard/main_data.csv')

main_df['dteday'] = pd.to_datetime(main_df['dteday'])

# Membuat Komponen Filter
min_date = main_df["dteday"].min()
max_date = main_df["dteday"].max()

# Membuat style center
st.markdown("""
    <style>
        .centered {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/IhlasulMufti/assets/raw/main/638061.jpg")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    st.markdown("""
                <p class='centered'>Karena Analisis yang digunakan membandingkan tahun 2011 dan 2012
                jadi silahkan pilih rentang waktu yang mencakup kedua tahun tersebut</p>
    """, unsafe_allow_html=True)

#--------------------------------------------------------
# Mempersiapkan Dataset

temp_df = main_df[(main_df["dteday"] >= str(start_date)) &
                (main_df["dteday"] <= str(end_date))]

customer_byHour_df = create_customer_byHour(temp_df)
customer_byYear_df = create_customer_byYear(temp_df)
customer_byType_df = create_customer_byType(customer_byYear_df)
customer_byWorkingday_df = create_customer_byWorkingday(temp_df)
customer_bySeason_df = create_customer_bySeason(temp_df)
customer_byWeather_df = create_customer_byWeather(temp_df)

# -------------------------------------------------------
# Melengkapi Dashboard dengan Berbagai Visualisasi Data

st.markdown("<h1 class='centered'>Bike Sharing Analytic</h1>", unsafe_allow_html=True)

# Pertanyaan 1: Bagaimana Demografi Customer?

# -------------------------------------------------------
# Customer by Type
with st.container():
    st.subheader('Count Customer By Type')

    fig, ax = plt.subplots(figsize=(35, 15))

    sns.barplot(y="jumlah_customer", x="year", hue="tipe_pelanggan", data=customer_byType_df)
    ax.set_ylabel(None)
    ax.set_xlabel("Year", fontsize=30)
    ax.set_title("Jumlah Customer Berdasarkan Tipe", loc="center", fontsize=50)
    ax.tick_params(axis='y', labelsize=35)
    ax.tick_params(axis='x', labelsize=30)

    legend = ax.legend(title="Customer Type", fontsize=25)
    legend.get_title().set_fontsize(25)

    st.pyplot(fig)

    with st.expander("Penjelasan"):
        st.write("""
            Terlihat jelas bahwa jumlah customer yang terdaftar lebih banyak jika dibandingkan dengan
            yang casual. Dari gambar juga kita dapat menarik kesimpulan bahwa dalam setahun customer
            yang terdaftar jumlahnya meningkat cukup pesat.
        """)

        st.caption("Jika anda memilih rentang secara manual, penjelasan diatas diabaikan")

# -------------------------------------------------------
# Customer by Hour
with st.container():
    st.subheader('Count Customer By Hour')

    custom_order = customer_byHour_df['hr']
    fig, ax = plt.subplots(figsize=(35, 15))

    sns.barplot(
        y="registered",
        x="hr",
        data=customer_byHour_df,
        color='orange',
        label='Registered Customer',
        order=custom_order,
        bottom=customer_byHour_df['casual']
    )

    sns.barplot(
        y="casual",
        x="hr",
        data=customer_byHour_df,
        color='blue',
        label='Casual Customer',
        order=custom_order,
    )

    ax.set_title("Jumlah Customer berdasarkan Hour", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel("Hour", fontsize=30)
    ax.tick_params(axis='x', labelsize=30)
    ax.tick_params(axis='y', labelsize=35)

    legend = ax.legend(title="Customer Type", fontsize=25)
    legend.get_title().set_fontsize(25)

    st.pyplot(fig)

    with st.expander("Penjelasan"):
        st.write("""
            Dalam gambar yang ada kita dapat melihat bahwa pada pukul 17:00 - 18:00 jumlah pengguna sepeda
            cukup banyak. Hal ini bisa saja terjadi karena pada waktu tersebut banyak orang yang melakukan
            perjalanan pulang ke rumah mereka. Dan pada pukul 00:00 - 04:00 pengguna sangat sedikit karena
            waktu tersebut adalah malam hari.
        """)

# -------------------------------------------------------
# Customer by Workingday
with st.container():
    st.subheader('Count Customer By Workingday')

    fig, ax = plt.subplots(figsize=(30, 15))

    sns.barplot(y="Jumlah_Customer", x="Week", data=customer_byWorkingday_df)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.set_title("Jumlah Customer Berdasarkan Workingday", loc="center", fontsize=50)
    ax.tick_params(axis='y', labelsize=35)
    ax.tick_params(axis='x', labelsize=35)

    st.pyplot(fig)

    with st.expander("Penjelasan"):
        st.write("""
            Berdasarkan gambar terlihat bahwa traffic pengguna pada hari kerja memang lebih banyak.
            Hal ini karena banyaknya pengguna yang berangkat ke kantor, sekolah, dll. Hal ini juga
            berhubungan dengan traffic pengguna yang padat pada pukul 17:00, 18:00, dan 08:00.
        """)

# -------------------------------------------------------
# Pertanyaan 2: Kapan Kondisi Terbaik Customer Meminjam Sepeda?
with st.container():
    st.subheader('Count Customer Melihat Kondisi Lingkungan')
    col1, col2 = st.columns(2)

    # -------------------------------------------------------
    # Customer by Season
    with col1:
        fig, ax = plt.subplots(figsize=(15, 10))

        sns.barplot(
            y="cnt",
            x="season",
            hue="yr",
            data=customer_bySeason_df.sort_values(by='cnt', ascending=False),
        )

        ax.set_title("Berdasarkan Musim", loc="center", fontsize=40)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis='x', labelsize=30)
        ax.tick_params(axis='y', labelsize=30)

        legend = ax.legend(fontsize=20)

        st.pyplot(fig)

    # -------------------------------------------------------
    # Customer by Weather
    with col2:
        fig, ax = plt.subplots(figsize=(15, 10))

        sns.barplot(
            y="cnt",
            x="weathersit",
            hue="yr",
            data=customer_byWeather_df.sort_values(by='cnt', ascending=False),
        )

        ax.set_title("Berdasarkan Cuaca", loc="center", fontsize=40)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis='x', labelsize=30)
        ax.tick_params(axis='y', labelsize=30)

        legend = ax.legend(fontsize=20)

        st.pyplot(fig)

    with st.expander("Penjelasan"):
        st.markdown("""
            Keterangan Kondisi Cuaca
            - 1: Clear, Few clouds, Partly cloudy, Partly cloudy
            - 2: Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist
            - 3: Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds
            - 4: Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog
        """)

        st.write("""
            Jika dilihat dari dua gambar diatas, kita dapat menyimpulkan bahwa penggunaan sepeda
            lebih mendukung dalam kondisi cuaca yang cerah berawan serta sedang dalam musim gugur.
            Sedangkan Kondisi terburuk adalah saat terjadi badai salju ataupun hujan. Jika dilihat
            dari tahun ke tahun polanya juga tetap sama.
        """)

        st.caption("Jika anda memilih rentang secara manual, penjelasan diatas diabaikan")

st.caption('Copyright (c) IhlasulMufti 2023')
