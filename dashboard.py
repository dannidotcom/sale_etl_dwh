import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard des Ventes", layout="wide")
st.markdown("<style>" + open("styles.css").read() + "</style>", unsafe_allow_html=True)

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("./data/cleaned/cleaned_sales.csv", parse_dates=["sale_date"])
    return df

df = load_data()

# Sidebar - Filtres
st.sidebar.header("Filtres")
start_date = st.sidebar.date_input("Date de début", df["sale_date"].min())
end_date = st.sidebar.date_input("Date de fin", df["sale_date"].max())
df_filtered = df[(df["sale_date"] >= pd.to_datetime(start_date)) & (df["sale_date"] <= pd.to_datetime(end_date))]

# KPIs
total_revenue = df_filtered["revenue"].sum()
total_profit = df_filtered["profit_margin"].sum()
avg_margin = df_filtered["profit_margin"].mean()
top_product = df_filtered.groupby("product_id")["revenue"].sum().idxmax()

# KPI layout
st.title("Tableau de bord décisionnel des ventes")
st.markdown("Analyse visuelle des performances commerciales.")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Revenu total</div>
            <div class="kpi-value">{total_revenue:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Marge totale</div>
            <div class="kpi-value">{total_profit:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Marge moyenne (%)</div>
            <div class="kpi-value">{avg_margin:.2f}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Produit Top</div>
            <div class="kpi-value">ID {top_product}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Graphiques
with st.container():
    col1, col2 = st.columns(2)

    # Bar Chart - Profit par produit avec couleurs différentes
    with col1:
        st.subheader("Profit par produit")
        product_profit = df_filtered.groupby("product_id")["profit_margin"].sum().reset_index()
        fig1 = px.bar(product_profit, x="product_id", y="profit_margin", 
                      title="Profit par produit",
                      color="product_id", 
                      color_discrete_sequence=px.colors.qualitative.Set2)  # Palette de couleurs vives
        st.plotly_chart(fig1, use_container_width=True)

    # Line Chart - Évolution des revenus dans le temps
    with col2:
        st.subheader("Évolution des revenus")
        fig2 = px.line(df_filtered, x="sale_date", y="revenue", 
                       title="Revenu par date", 
                       labels={"sale_date": "Date", "revenue": "Revenu"}, 
                       line_shape="linear", 
                       color_discrete_sequence=["#0A75AD"])  # Couleur de la ligne
        st.plotly_chart(fig2, use_container_width=True)

# Graphique supplémentaire
st.subheader("Répartition des revenus par produit (Pie Chart)")
fig3 = px.pie(df_filtered.groupby("product_id")["revenue"].sum().reset_index(), 
              names="product_id", 
              values="revenue", 
              title="Répartition des revenus", 
              color_discrete_sequence=px.colors.sequential.Plasma)  # Palette Plasma
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.header("📊 Analyses dynamiques en temps réel")

real_time_col1, real_time_col2 = st.columns(2)

# === TOP 5 PRODUITS VENDUS (7 DERNIERS JOURS) ===
with real_time_col1:
    st.subheader("🛒 Top 5 produits (7 derniers jours)")

    today = pd.Timestamp.today().normalize()
    last_week = today - pd.Timedelta(days=7)

    df_last_7_days = df_filtered[df_filtered["sale_date"].between(last_week, today)]
    top_products_7_days = (
        df_last_7_days.groupby("product_id")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    fig_top_7 = px.bar(
        top_products_7_days,
        x="product_id",
        y="quantity",
        title="Produits les plus vendus",
        color="product_id",
        labels={"product_id": "Produit", "quantity": "Quantité"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    st.plotly_chart(fig_top_7, use_container_width=True)

# === TOP 5 CLIENTS FIDÈLES (MOIS EN COURS) ===
with real_time_col2:
    st.subheader("🤝 Top 5 clients fidèles (mois en cours)")

    now = pd.Timestamp.today()
    start_of_month = pd.Timestamp(year=now.year, month=now.month, day=1)

    df_month = df_filtered[df_filtered["sale_date"].between(start_of_month, now)]

    top_clients_month = (
        df_month.groupby("customer_id")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )

    fig_clients = px.bar(
        top_clients_month,
        x="customer_id",
        y="revenue",
        title="Clients générant le plus de revenus",
        color="customer_id",
        labels={"customer_id": "Client", "revenue": "Revenu"},
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    st.plotly_chart(fig_clients, use_container_width=True)
