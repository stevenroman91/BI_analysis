import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Création d'une connexion SQLite en mémoire
@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

# Fonction de chargement des données (tables des faits et dimensions)
@st.cache_data
def load_data(_conn):
    dim_customer = pd.read_excel("./Data/DimCustomer.xlsx")
    dim_price    = pd.read_excel("./Data/DimPrice.xlsx")
    dim_categ    = pd.read_excel("./Data/DimCateg.xlsx")
    fact_volumes = pd.read_excel("./Data/FactVolumes.xlsx")
    
    # Nettoyage éventuel de DimCateg
    dim_categ.dropna(inplace=True)
    
    # Conversion de la date
    fact_volumes["Date"] = pd.to_datetime(fact_volumes["Date"])
    
    # Insertion des tables dans SQLite
    dim_customer.to_sql("DimCustomer", _conn, index=False, if_exists="replace")
    dim_price.to_sql("DimPrice", _conn, index=False, if_exists="replace")
    dim_categ.to_sql("DimCateg", _conn, index=False, if_exists="replace")
    fact_volumes.to_sql("FactVolumes", _conn, index=False, if_exists="replace")

# Initialisation de la connexion et chargement des données
conn = get_connection()
load_data(conn)

st.title("Revenue and Gross Profit Impact of Reallocation")

# Requête SQL pour calculer revenue et gross profit pour le scénario Base et Revised par client  
query = """
SELECT dc.Client,
       SUM(CASE WHEN f.Scenario = 'Base' THEN f.Volume * dp."NOS/KG" ELSE 0 END) AS Revenue_Base,
       SUM(CASE WHEN f.Scenario = 'Revised' THEN f.Volume * dp."NOS/KG" ELSE 0 END) AS Revenue_Revised,
       SUM(CASE WHEN f.Scenario = 'Base' THEN f.Volume * dp."GP/KG" ELSE 0 END) AS GP_Base,
       SUM(CASE WHEN f.Scenario = 'Revised' THEN f.Volume * dp."GP/KG" ELSE 0 END) AS GP_Revised
FROM FactVolumes f
JOIN DimCustomer dc ON f.ID_CUSTO = dc.ID_Client
JOIN DimPrice dp ON f.SKU = dp.SKU
GROUP BY dc.Client;
"""

df_impact = pd.read_sql_query(query, conn)

# Calcul des impacts
df_impact["Revenue_Impact"] = df_impact["Revenue_Revised"] - df_impact["Revenue_Base"]
df_impact["GP_Impact"] = df_impact["GP_Revised"] - df_impact["GP_Base"]

st.subheader("Impact by Client")
st.dataframe(df_impact)

# Graphique en barres pour l'impact sur le chiffre d'affaires
fig_rev = px.bar(
    df_impact,
    x="Client",
    y="Revenue_Impact",
    title="Revenue Impact by Client",
    labels={"Revenue_Impact": "Revenue Impact (€)"}
)
st.plotly_chart(fig_rev)

# Graphique en barres pour l'impact sur la marge brute
fig_gp = px.bar(
    df_impact,
    x="Client",
    y="GP_Impact",
    title="Gross Profit Impact by Client",
    labels={"GP_Impact": "Gross Profit Impact (€)"}
)
st.plotly_chart(fig_gp)
