import time
import pulp
import plotly.express as px 
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

# -----------------------CONFIG-----------------------------
st.set_page_config(
    page_title="Dashboard Informasi Harga Sayur",
    page_icon="🥕", 
    layout="wide",
    initial_sidebar_state="collapsed",
)

## Read Data
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    spreadsheet=st.secrets.gsheet_lbb["spreadsheet"],
    worksheet=st.secrets.gsheet_lbb["worksheet"]
)

## Simple data cleanup
# Drop unnecessary columns
# df.drop(columns=['No', 'Nama Toko'], inplace=True)
df = df.drop(columns='Nama Toko')

# Drop rows with specific substrings in 'Nama Barang' and reset index
# pattern = 'Pete Kupas|Pete Papan'
# df = df[~df['Nama Barang'].str.contains(pattern, case=False, na=False)].reset_index(drop=True)

# Set the index to start from 1
df.index = df.index + 1

# Convert columns to numeric, coerce errors to NaN
numeric_columns = ['Ratio Harga per 100 Gram', 'Berat (Gram)', 'Harga']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')


# ------------------------ Judul Dashboard-------------------

st.markdown("<h1 style='text-align:center;'> Informasi Harga Sayur🥗 </h1>",
            unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center;'>
        <h6>Rekap harga beberapa produk pertanian yang dirangkum pada rentang tahun 2021 sampai 2022.</h6>
    </div>
    """, unsafe_allow_html=True)

st.write("![](https://fam-stumabo.com/wp-content/uploads/header-images_vegetables.jpg)")
st.markdown("---")

# membuat layout dengan 2 kolom
col1, col2 = st.columns(2)

# mengisi pada setiap kolom
with col1:
    st.markdown("**Table Harga Sayuran**")
    st.write(df)

with col2:
    st.markdown("**Plot Top 10 Rasio Harga Sayuran per 100 Gram**")
    # Create the dot chart using Plotly Express
    fig = px.scatter(df.head(10), x='Nama Barang', y='Ratio Harga per 100 Gram', text='Nama Barang', size='Ratio Harga per 100 Gram', color='Nama Barang')
    # Customize the chart (optional)
    fig.update_traces(textposition='top center')
    fig.update_layout(xaxis_title='Nama Barang', yaxis_title='Harga per 100 Gram')

    # Display the chart in Streamlit
    st.plotly_chart(fig)


# Simple Machine Learning
st.title("Product Composition Optimization")
st.markdown("""
    Mencari komposisi pembelian yang terbaik berdasarkan kapasitas(dalam kg) yang dapat dibawa.
""")

# User input for maximum weight
max_weight = st.slider('Select the maximum weight you can carry (grams):', min_value=100, max_value=10000, step=100, value=2000)

# User input for weight of importance between weight and price
weight_importance = st.slider('Select the importance of weight (1-10):', min_value=1, max_value=10, value=5)
price_importance = 10 - weight_importance

# Add checkboxes for each product to exclude
st.markdown("### Exclude Products")

# Initialize session state for checkboxes
if 'checked' not in st.session_state:
    st.session_state.checked = {product: True for product in df['Nama Barang'].unique()}

# Button to reset checkboxes
if st.button('Reset All Checkboxes'):
    st.session_state.checked = {product: True for product in df['Nama Barang'].unique()}
    st.experimental_rerun()  # Force rerun to update checkboxes

# Sort product names alphabetically
sorted_products = sorted(df['Nama Barang'].unique())
columns = st.columns(6)  # Create 6 columns for checkboxes
excluded_products = []

for i, product in enumerate(sorted_products):
    col = columns[i % 6]  # Distribute checkboxes across columns
    st.session_state.checked[product] = col.checkbox(product, value=st.session_state.checked[product])
    if not st.session_state.checked[product]:
        excluded_products.append(product)

# Filter out the excluded products
df_filtered = df[~df['Nama Barang'].isin(excluded_products)]

# Define the problem
problem = pulp.LpProblem("Maximize_Product_Carry", pulp.LpMaximize)

# Define decision variables
quantities = pulp.LpVariable.dicts("quantity", df_filtered.index, lowBound=0, cat='Integer')

# Define the objective function: maximize the total value (weight + price weighted by importance)
problem += pulp.lpSum([
    quantities[i] * (weight_importance * df_filtered.loc[i, 'Berat (Gram)'] + price_importance * df_filtered.loc[i, 'Harga'])
    for i in df_filtered.index
])

# Define the constraint: total weight must be less than or equal to max_weight
problem += pulp.lpSum([quantities[i] * df_filtered.loc[i, 'Berat (Gram)'] for i in df_filtered.index]) <= max_weight

# Solve the problem
problem.solve()

# Display the results
st.markdown(f"### Optimal Product Composition for Maximum Weight of {max_weight} grams:")
if pulp.LpStatus[problem.status] == 'Optimal':
    results = []
    for i in df_filtered.index:
        if quantities[i].varValue > 0:
            results.append({
                'Nama Barang': df_filtered.loc[i, 'Nama Barang'],
                'Optimal Units': quantities[i].varValue,
                'Total Weight': quantities[i].varValue * df_filtered.loc[i, 'Berat (Gram)'],
                'Total Price': quantities[i].varValue * df_filtered.loc[i, 'Harga']
            })
    results_df = pd.DataFrame(results)
    st.write(results_df)
    
    # Display total weight and total price
    total_weight = results_df['Total Weight'].sum()
    total_price = results_df['Total Price'].sum()
    
    st.markdown(f"**Total Weight:** {total_weight:.0f} grams")
    st.markdown(f"**Total Price:** {total_price:,.0f}")

    # Conclusion
    st.write(f"Kesimpulan: Dengan kombinasi kapasitas angkut sebesar {total_weight:.0f} kg dan revenue sebesar {total_price:,.0f} rupiah, baik pembeli maupun penjual mendapatkan hasil transaksi yang paling optimal.")
else:
    st.markdown("No optimal solution found.")

#  ------- SIDEBAR
with st.sidebar:
    st.subheader("Sayur Analytic")
    st.markdown("Menemukan kombinasi optimal pembelian sayuran terhadap berat maupun revenue.")
    st.markdown("---")
    st.markdown("""
*YData-profiling is a leading tool in the data understanding step of the data science workflow as a pioneering Python package.*
<br><br>
&nbsp;&nbsp;&nbsp;ydata-profiling is a leading package for data profiling, that automates and standardizes the generation of detailed reports, complete with statistics and visualizations.
""", unsafe_allow_html=True)


#---- buat Button
if st.sidebar.button("Start Profiling Data"):
    
    st.markdown("---")
    st.subheader("Report from YData_Profiling")


    ## Generate Report
    #---- ydata profiling
    pr = ProfileReport(df)

    #display to streamlit
    st_profile_report(pr)
    
else:
    st.info('''Click "Start Profiling Data" button in the left sidebar to generate data report''')

# Add cached function and download button
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

csv = convert_df(df)

st.sidebar.download_button(
    label="Download raw data as CSV",
    data=csv,
    file_name="nyayur.csv",
    mime="text/csv",
)
