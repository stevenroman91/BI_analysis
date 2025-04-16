import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

@st.cache_data
def load_data(_conn):
    dim_customer = pd.read_excel("./Data/DimCustomer.xlsx")
    dim_price = pd.read_excel("./Data/DimPrice.xlsx")
    dim_categ = pd.read_excel("./Data/DimCateg.xlsx")
    fact_volumes = pd.read_excel("./Data/FactVolumes.xlsx")

    # Suppression des valeurs manquantes dans la dimension catégorie si nécessaire
    dim_categ.dropna(inplace=True)
    
    # Conversion de la colonne Date en datetime
    fact_volumes["Date"] = pd.to_datetime(fact_volumes["Date"])
    
    # Chargement des données dans SQLite
    dim_customer.to_sql("DimCustomer", _conn, index=False, if_exists="replace")
    dim_price.to_sql("DimPrice", _conn, index=False, if_exists="replace")
    dim_categ.to_sql("DimCateg", _conn, index=False, if_exists="replace")
    fact_volumes.to_sql("FactVolumes", _conn, index=False, if_exists="replace")

conn = get_connection()
load_data(conn)

st.title("Trend Analysis par Client")

# Récupérer la liste des clients depuis la table DimCustomer
customers = pd.read_sql_query("SELECT DISTINCT Client FROM DimCustomer", conn)
selected_customer = st.selectbox("Select a client", customers["Client"])

# Graphique 1 : Tendance du volume (tous les scénarios)
query_volume = """
SELECT f.Date, f.Scenario, SUM(f.Volume) as TotalVolume
FROM FactVolumes f
JOIN DimCustomer dc ON f.ID_CUSTO = dc.ID_Client
WHERE dc.Client = ?
GROUP BY f.Date, f.Scenario
ORDER BY f.Date;
"""
df_volume = pd.read_sql_query(query_volume, conn, params=(selected_customer,))

fig_volume = px.line(df_volume, x="Date", y="TotalVolume", color="Scenario",
              title=f"Tendance du Volume pour le client {selected_customer} (tous les scénarios)")
st.plotly_chart(fig_volume)

# Graphique 2 : Tendance du chiffre d'affaires (en €)
# On utilise la table DimPrice pour convertir le volume en euros avec la colonne "NOS/KG"
query_revenue = """
SELECT f.Date, f.Scenario, SUM(f.Volume * dp."NOS/KG") as TotalRevenue
FROM FactVolumes f
JOIN DimCustomer dc ON f.ID_CUSTO = dc.ID_Client
JOIN DimPrice dp ON f.SKU = dp.SKU
WHERE dc.Client = ?
GROUP BY f.Date, f.Scenario
ORDER BY f.Date;
"""
df_revenue = pd.read_sql_query(query_revenue, conn, params=(selected_customer,))

fig_revenue = px.line(df_revenue, x="Date", y="TotalRevenue", color="Scenario",
              title=f"Tendance du Chiffre d'Affaires en € pour le client {selected_customer}")
st.plotly_chart(fig_revenue)
