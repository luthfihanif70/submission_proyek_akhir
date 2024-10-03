# import seluruh library yang dibutuhkan
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# helper function yang akan digunakan
def count_by_day_df(day_df):
    specific_day_df = day_df.query(str('dteday >= "2011-01-01" and dteday <= "2012-12-31"'))
    return specific_day_df

def total_registered_user_df(day_df):
    req_user_df = day_df.groupby(by="dteday").agg({
                    "registered": "sum"
                })
    req_user_df = req_user_df.reset_index()
    req_user_df.rename(columns={
        "registered": "registered_user"
    }, inplace=True)
    return req_user_df

def total_casual_user_df(day_df):
    cas_user_df = day_df.groupby(by="dteday").agg({
                    "casual": ["sum"]
                })
    cas_user_df = cas_user_df.reset_index()
    cas_user_df.rename(columns={
        "casual": "casual_user"
    }, inplace=True)
    return cas_user_df

def group_by_season_df(day_df): 
    by_season_df = day_df.groupby(by="season", observed=False).agg({
                    "cnt": ["sum", "max", "min", "mean"]
                }).sort_values(by=("cnt", "sum"), ascending=False).reset_index().rename(columns={
                    ("season"): "Season",
                    ("cnt"): "Count",
                    ("sum"): "Total",
                    ("max"): "Max_per_Day",
                    ("min"): "Min_per_Day",
                    ("mean"): "Mean_per_Day"
                })
    return by_season_df

def group_by_workingday_df(day_df):
    by_workingday_df = day_df.groupby(by="workingday").agg({
                        "registered": ["sum", "mean"],
                        "casual": ["sum", "mean"]
                    }).reset_index().rename(columns={
                        ("workingday"): "is_Working_Day",
                        ("registered"): "Registered_User",
                        ("casual"): "Casual_User",
                        ("sum"): "Total",
                        ("mean"): "Mean_per_Day"
                    }).replace({
                        0: "No", 1: "Yes"
                    })
    return by_workingday_df

def group_by_weathersit_df(day_df):
    by_weathersit_df = day_df.groupby(by="weathersit", observed=False).agg({
                        "cnt": ["mean"]
                    }).reset_index().rename(columns={
                        "weathersit": "Weather_Situation",
                        "cnt": "Count",
                        "mean": "Mean_per_Day"
                    })
    return by_weathersit_df

def group_by_hour_df(hour_df):
    by_hour_df = hour_df.groupby(by="hr").agg({
                    "cnt": ["sum", "mean"]
                }).reset_index().rename(columns={
                    "hr": "Hours",
                    "cnt": "Count",
                    "sum": "Total",
                    "mean": "Mean"
                })
    return by_hour_df

# load berkas yang akan digunakan sebagai DataFrame
day_cleaned_df = pd.read_csv("https://raw.githubusercontent.com/luthfihanif70/submission_proyek_akhir/refs/heads/main/dashboard/day_cleaned.csv")
hour_cleaned_df = pd.read_csv("https://raw.githubusercontent.com/luthfihanif70/submission_proyek_akhir/refs/heads/main/dashboard/hour_cleaned.csv")

# Mengurutkan DataFrame berdasarkan dteday dan memastikan kolom bertipe datetime
datetime_columns = ["dteday"]

day_cleaned_df.sort_values(by="dteday", inplace=True)
day_cleaned_df.reset_index(inplace=True)

hour_cleaned_df.sort_values(by="dteday", inplace=True)
hour_cleaned_df.reset_index(inplace=True)

for column in datetime_columns:
    day_cleaned_df[column] = pd.to_datetime(day_cleaned_df[column])
    hour_cleaned_df[column] = pd.to_datetime(hour_cleaned_df[column])

# Membuat komponen filter dengan widget date input serta menambahkan logo
min_date_day = day_cleaned_df["dteday"].min()
max_date_day = day_cleaned_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo
    st.image("https://raw.githubusercontent.com/luthfihanif70/submission_proyek_akhir/refs/heads/main/dashboard/logo.jpg") # source = https://www.vecteezy.com/vector-art/19030974-bike-rental-logo-with-a-bicycle-and-label-combination-for-any-business
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
                                label='Rentang Waktu',
                                min_value=min_date_day,
                                max_value=max_date_day,
                                value=[min_date_day, max_date_day])

# Melakukan filter terhadap DataFrame    
main_df_day = day_cleaned_df[(day_cleaned_df["dteday"] >= str(start_date)) & 
                            (day_cleaned_df["dteday"] <= str(end_date))]

main_df_hour = hour_cleaned_df[(hour_cleaned_df["dteday"] >= str(start_date)) & 
                            (hour_cleaned_df["dteday"] <= str(end_date))]

# Memanggil helper function yang telah dibuat sebelumnya
result_count_by_day_df = count_by_day_df(main_df_day)
result_total_reg_df = total_registered_user_df(main_df_day)
result_total_cas_df = total_casual_user_df(main_df_day)
result_group_by_season_df = group_by_season_df(main_df_day)
result_group_by_workingday_df = group_by_workingday_df(main_df_day)
result_group_by_weathersit_df = group_by_weathersit_df(main_df_day)
result_group_by_hour_df = group_by_hour_df(main_df_hour)

# Melengkapi dashboard dengan berbagai visualisasi data
st.header('Bike Sharing Dashboard')

# subheader "Summary Data"
st.subheader('Summary Data')

col1, col2, col3 = st.columns(3)
 
with col1:
    total_sum = result_count_by_day_df.cnt.sum()
    st.metric("Total Sharing Bike", value=total_sum)

with col2:
    total_sum = result_total_reg_df.registered_user.sum()
    st.metric("Total Registered User", value=total_sum)

with col3:
    total_sum = result_total_cas_df.casual_user.sum()
    st.metric("Total Casual User", value=total_sum)

# subheader "Pengaruh Season(Musim) terhadap Jumlah Penyewaan Sepeda"
st.subheader("Pengaruh Season(Musim) terhadap Jumlah Penyewaan Sepeda")

fig, axes = plt.subplots(1, 2, figsize=(15, 5))

sns.barplot(data=result_group_by_season_df, x="Season", y=("Count", "Total"), hue="Season", palette="flare", ax=axes[0], legend=False)
axes[0].set_title("Rental per Season")
axes[0].set_xlabel("Season")
axes[0].set_ylabel("Total")
axes[0].tick_params(axis='x', rotation=45)

axes[1].plot(result_group_by_season_df["Season"], result_group_by_season_df[("Count", "Max_per_Day")], marker="o", label="Max per Day", color="red")
axes[1].plot(result_group_by_season_df["Season"], result_group_by_season_df[("Count", "Min_per_Day")], marker="o", label="Min per Day", color="blue")
axes[1].plot(result_group_by_season_df["Season"], result_group_by_season_df[("Count", "Mean_per_Day")], marker="o", label="Mean per Day", color="green")

axes[1].set_title("Max, Min, and Mean Rentals per Day")
axes[1].set_xlabel("Season")
axes[1].set_ylabel("Total")
axes[1].tick_params(axis='x', rotation=45)
axes[1].legend(loc="right")

plt.tight_layout()
st.pyplot(fig)

# subheader "Perbandingan Registered dengan Casual User pada Kondisi Working Day dan Bukan"
st.subheader("Perbandingan Registered dengan Casual User pada Kondisi Working Day dan Bukan")

fig, axes = plt.subplots(1, 2, figsize=(10, 5))

no_working_day_data = result_group_by_workingday_df[result_group_by_workingday_df["is_Working_Day"] == "No"]
yes_working_day_data = result_group_by_workingday_df[result_group_by_workingday_df["is_Working_Day"] == "Yes"]
labels = ["Registered Users", "Casual Users"]
colors = ["#72BCD4", "#D3D3D3"]

# Pie Chart for Non-Working Day
axes[0].pie([no_working_day_data[("Registered_User", "Mean_per_Day")].values[0], 
             no_working_day_data[("Casual_User", "Mean_per_Day")].values[0]],
            labels=labels, 
            autopct='%1.1f%%', 
            colors=colors)
axes[0].set_title("Non-Working Day")

# Pie Chart for Working Day
axes[1].pie([yes_working_day_data[("Registered_User", "Mean_per_Day")].values[0], 
             yes_working_day_data[("Casual_User", "Mean_per_Day")].values[0]],
            labels=labels, 
            autopct='%1.1f%%', 
            colors=colors)
axes[1].set_title("Working Day")

plt.tight_layout()
st.pyplot(fig)

# subheader "Pengaruh Cuaca terhadap Jumlah Penyewaan Sepeda Harian"
st.subheader("Pengaruh Cuaca terhadap Jumlah Penyewaan Sepeda Harian")

fig, ax = plt.subplots(figsize=(5, 5))

sns.barplot(data=result_group_by_weathersit_df, x="Weather_Situation", y=("Count", "Mean_per_Day"), hue="Weather_Situation", palette="flare", ax=ax, legend=False)
ax.set_title("Average per Day")
ax.set_xlabel("Weather Situation")
ax.set_ylabel("Total")
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
st.pyplot(fig)

# subheader "Rata-Rata Penyewaan Sepeda per Jam"
st.subheader("Rata-Rata Penyewaan Sepeda per Jam")

fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(result_group_by_hour_df["Hours"], result_group_by_hour_df[("Count", "Mean")], marker="o", label="Average per Hour", color="#72BCD4")
ax.set_xticks(range(24))
ax.set_xticklabels(range(24))
ax.set_xlim(0, 23)

ax.set_title("Average Bike Rental each Hour")
ax.set_xlabel("Hours")
ax.set_ylabel("Total Average")
ax.legend(loc="upper right")

plt.tight_layout()
st.pyplot(fig)

st.caption('Copyright (c) Luthfi Hanif 2024')