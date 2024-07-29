import streamlit as st
from streamlit_gsheets import GSheetsConnection

# ydata profiling
import pandas as pd
from ydata_profiling import ProfileReport

#Streamlit juga butuh library untuk spesifik menampilkan hasil data yprofiling sehingga ini dibawah adalah library report untuk streamlit
from streamlit_pandas_profiling import st_profile_report

# -----------------------CONFIG-----------------------------
st.set_page_config(
    page_title="Data Profile Dashboard",
    page_icon="🌹", #Or else, check Windows + . (Dot button)
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------ Judul Dashboard-------------------

# st.title("Data Profiler")
st.markdown("<h1 style='text-align:center;'> Data Profiler App </h1>",
            unsafe_allow_html=True)
st.markdown("---")

#  ------- Sidebar
with st.sidebar:
    st.subheader("Promotion Data")
    st.markdown("---")


#---- buat Button
if st.sidebar.button("Start Profiling Data"):

    ## Read Data
    conn = st.connection("gsheets", type = GSheetsConnection)

    df = conn.read(
        spreadsheet = st.secrets.gsheet_promotion["spreadsheet"],
        worksheet = st.secrets.gsheet_promotion["worksheet"]
    )

    ## Generate Report
    #---- ydata profiling
    pr = ProfileReport(df)

    #display to streamlit
    st_profile_report(pr)

    st.write("Report")

else:
    st.info("Click button in the left sidebar to generate data report")

