import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

@st.cache_resource
def get_connection():
    return sqlite3.connect(':memory:', check_same_thread=False)

@st.cache_data
def load_data(_conn):
    dim_customer = pd.read_excel("./Data/DimCustomer.xlsx")
    dim_price = pd.read_excel("./Data/DimPrice.xlsx")
    dim_categ = pd.read_excel("./Data/DimCateg.xlsx")
    fact_volumes = pd.read_excel("./Data/FactVolumes.xlsx")

    # On nettoie éventuellement la dimension catégorie
    dim_categ.dropna(inplace=True)
    
    # Conversion de la colonne Date au format datetime
    fact_volumes["Date"] = pd.to_datetime(fact_volumes["Date"])
    
    # Insertion des tables dans SQLite
    dim_customer.to_sql("DimCustomer", _conn, index=False, if_exists="replace")
    dim_price.to_sql("DimPrice", _conn, index=False, if_exists="replace")
    dim_categ.to_sql("DimCateg", _conn, index=False, if_exists="replace")
    fact_volumes.to_sql("FactVolumes", _conn, index=False, if_exists="replace")

conn = get_connection()
load_data(conn)

st.title("Bridge Analysis: Forecast Base vs Revised")

# Récupération de la liste des clients depuis DimCustomer
customers = pd.read_sql_query("SELECT DISTINCT Client FROM DimCustomer", conn)
selected_customer = st.selectbox("Select a client", customers["Client"])

# Extraction dynamique des scénarios disponibles dans FactVolumes
scenarios = pd.read_sql_query("SELECT DISTINCT Scenario FROM FactVolumes", conn)["Scenario"].tolist()

# Sélection du scénario de base et du scénario révisé
base_scenario = "Base"
revised_scenario = "Revised"

# Requête SQL avec un pivot sur la colonne Scenario grâce à CASE WHEN
query = """
SELECT dcat.Categorie,
       SUM(CASE WHEN f.Scenario = ? THEN f.Volume ELSE 0 END) as Forecast_Base,
       SUM(CASE WHEN f.Scenario = ? THEN f.Volume ELSE 0 END) as Forecast_Revised
FROM FactVolumes f
JOIN DimCustomer dc ON f.ID_CUSTO = dc.ID_Client
JOIN DimCateg dcat ON f.ID_CATEG = dcat.ID
WHERE dc.Client = ?
GROUP BY dcat.Categorie;
"""
df_bridge = pd.read_sql_query(query, conn, params=(base_scenario, revised_scenario, selected_customer))
df_bridge["Impact"] = df_bridge["Forecast_Revised"] - df_bridge["Forecast_Base"]

# Calculer les totaux globaux
base_total = df_bridge["Forecast_Base"].sum()
revised_total = df_bridge["Forecast_Revised"].sum()

# Préparer les données pour le graphique en waterfall
# On affiche la valeur de base, puis l'impact par catégorie, puis la valeur finale
x_values = ["Forecast " + base_scenario] + df_bridge["Categorie"].tolist() + ["Forecast " + revised_scenario]
y_values = [base_total] + df_bridge["Impact"].tolist() + [revised_total]
measures = ["absolute"] + ["relative"] * len(df_bridge) + ["total"]

fig = go.Figure(go.Waterfall(
    name="Bridge Analysis",
    orientation="v",
    measure=measures,
    x=x_values,
    y=y_values,
    connector={"line": {"color": "rgb(63, 63, 63)"}}
))
fig.update_layout(title=f"Bridge Analysis for {selected_customer}: {base_scenario} → {revised_scenario}", waterfallgap=0.3)
st.plotly_chart(fig)
