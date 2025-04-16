import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

@st.cache_data
def load_data(_conn):
    # Chargement des fichiers Excel
    dim_customer = pd.read_excel("./Data/DimCustomer.xlsx")
    dim_price    = pd.read_excel("./Data/DimPrice.xlsx")
    dim_categ    = pd.read_excel("./Data/DimCateg.xlsx")
    fact_volumes = pd.read_excel("./Data/FactVolumes.xlsx")
    
    # Nettoyage éventuel, par exemple pour DimCateg
    dim_categ.dropna(inplace=True)
    
    # Conversion de la colonne Date
    fact_volumes["Date"] = pd.to_datetime(fact_volumes["Date"])
    
    # Insertion dans SQLite
    dim_customer.to_sql("DimCustomer", _conn, index=False, if_exists="replace")
    dim_price.to_sql("DimPrice", _conn, index=False, if_exists="replace")
    dim_categ.to_sql("DimCateg", _conn, index=False, if_exists="replace")
    fact_volumes.to_sql("FactVolumes", _conn, index=False, if_exists="replace")

conn = get_connection()
load_data(conn)

st.title("Static Bridge Analysis: Client & Category")

##############################
# Bridge Analysis by Client
##############################
st.subheader("Bridge Analysis by Client (Impact relatif)")

query_client = """
SELECT dc.Client,
       SUM(CASE WHEN f.Scenario = 'Base' THEN f.Volume ELSE 0 END) as Forecast_Base,
       SUM(CASE WHEN f.Scenario = 'Revised' THEN f.Volume ELSE 0 END) as Forecast_Revised
FROM FactVolumes f
JOIN DimCustomer dc ON f.ID_CUSTO = dc.ID_Client
GROUP BY dc.Client;
"""
df_client = pd.read_sql_query(query_client, conn)
df_client["Impact"] = df_client["Forecast_Revised"] - df_client["Forecast_Base"]

# Totaux globaux sur tous les clients
total_base_client = df_client["Forecast_Base"].sum()
total_revised_client = df_client["Forecast_Revised"].sum()
global_impact = total_revised_client - total_base_client

client_labels = df_client["Client"].tolist()

# Pour un affichage relatif, la première barre (Forecast Base global) sera représentée comme zéro.
# Chaque client montre alors sa contribution (l’impact) et la dernière barre correspond au total des impacts.
rel_x_values_client = ["Forecast Base"] + client_labels + ["Forecast Revised"]
rel_y_values_client = [0] + df_client["Impact"].tolist() + [global_impact]
measures_client = ["absolute"] + ["relative"] * len(df_client) + ["total"]

fig_client_rel = go.Figure(go.Waterfall(
    x=rel_x_values_client,
    y=rel_y_values_client,
    measure=measures_client,
    connector={"line": {"color": "rgb(63,63,63)"}}
))
fig_client_rel.update_layout(
    title="Bridge Analysis by Client (Impacts relatifs)",
    waterfallgap=0.3,
    yaxis_title="Impact (Forecast Revised - Forecast Base)"
)
st.plotly_chart(fig_client_rel)



##############################
# Bridge Analysis by Category
##############################
st.subheader("Bridge Analysis by Category")

query_category = """
SELECT dcat.Categorie,
       SUM(CASE WHEN f.Scenario = 'Base' THEN f.Volume ELSE 0 END) as Forecast_Base,
       SUM(CASE WHEN f.Scenario = 'Revised' THEN f.Volume ELSE 0 END) as Forecast_Revised
FROM FactVolumes f
JOIN DimCateg dcat ON f.ID_CATEG = dcat.ID
GROUP BY dcat.Categorie;
"""
df_category = pd.read_sql_query(query_category, conn)
df_category["Impact"] = df_category["Forecast_Revised"] - df_category["Forecast_Base"]

total_base_category = df_category["Forecast_Base"].sum()
total_revised_category = df_category["Forecast_Revised"].sum()
category_labels = df_category["Categorie"].tolist()

x_values_category = ["Forecast Base"] + category_labels + ["Forecast Revised"]
y_values_category = [total_base_category] + df_category["Impact"].tolist() + [total_revised_category]
measures_category = ["absolute"] + ["relative"] * len(df_category) + ["total"]

fig_category = go.Figure(go.Waterfall(
    x=x_values_category,
    y=y_values_category,
    measure=measures_category,
    connector={"line": {"color": "rgb(63, 63, 63)"}}
))
# Si vous souhaitez également fixer l'axe Y ici, vous pouvez le faire de la même manière :
# max_val_category = max(y_values_category) if y_values_category else 100e6
# fig_category.update_yaxes(range=[80e6, max_val_category * 1.1])
fig_category.update_layout(title="Bridge Analysis by Category: Base → Revised", waterfallgap=0.3)
st.plotly_chart(fig_category)
