import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="European Bank Customer Churn Analytics",
    page_icon="🏦",
    layout="wide"
)

# -----------------------------
# Load Data
# -----------------------------
FILE_NAME = "European_Bank_Customer_Segmentation.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_NAME, sheet_name="Raw_Data")

    # Create required segments if they are not already present
    if "Age Group" not in df.columns:
        df["Age Group"] = pd.cut(
            df["Age"],
            bins=[0, 29, 45, 60, float("inf")],
            labels=["<30", "30-45", "46-60", "60+"]
        )

    if "Credit Score Band" not in df.columns:
        df["Credit Score Band"] = pd.cut(
            df["CreditScore"],
            bins=[-float("inf"), 579, 669, float("inf")],
            labels=["Low", "Medium", "High"]
        )

    if "Tenure Group" not in df.columns:
        df["Tenure Group"] = pd.cut(
            df["Tenure"],
            bins=[-1, 3, 6, float("inf")],
            labels=["New", "Mid-term", "Long-term"]
        )

    if "Balance Segment" not in df.columns:
        df["Balance Segment"] = df["Balance"].apply(
            lambda x: "Zero-balance"
            if x == 0
            else ("Low-balance" if x <= 97198.54 else "High-balance")
        )

    return df


df = load_data()

# -----------------------------
# Title
# -----------------------------
st.title("🏦 European Bank Customer Churn Analytics")
st.markdown(
    "### Customer Segmentation & Churn Pattern Analysis"
)

st.write(
    "This dashboard analyzes customer churn across geography, age, "
    "credit score, tenure, balance, engagement and product usage."
)

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔎 Customer Filters")

geography = st.sidebar.multiselect(
    "Geography",
    sorted(df["Geography"].dropna().unique()),
    default=sorted(df["Geography"].dropna().unique())
)

gender = st.sidebar.multiselect(
    "Gender",
    sorted(df["Gender"].dropna().unique()),
    default=sorted(df["Gender"].dropna().unique())
)

age_group = st.sidebar.multiselect(
    "Age Group",
    df["Age Group"].dropna().astype(str).unique().tolist(),
    default=df["Age Group"].dropna().astype(str).unique().tolist()
)

df_filtered = df[
    (df["Geography"].isin(geography)) &
    (df["Gender"].isin(gender)) &
    (df["Age Group"].astype(str).isin(age_group))
].copy()

# -----------------------------
# KPI Calculations
# -----------------------------
total_customers = len(df_filtered)
churned_customers = int(df_filtered["Exited"].sum())

if total_customers > 0:
    churn_rate = churned_customers / total_customers
else:
    churn_rate = 0

active_df = df_filtered[df_filtered["IsActiveMember"] == 1]
inactive_df = df_filtered[df_filtered["IsActiveMember"] == 0]

active_churn = (
    active_df["Exited"].mean()
    if len(active_df) > 0 else 0
)

inactive_churn = (
    inactive_df["Exited"].mean()
    if len(inactive_df) > 0 else 0
)

high_value_disengaged = df_filtered[
    (df_filtered["Balance"] >= 97198.54) &
    (df_filtered["IsActiveMember"] == 0)
]

high_value_churn = (
    high_value_disengaged["Exited"].mean()
    if len(high_value_disengaged) > 0 else 0
)

# -----------------------------
# KPI Cards
# -----------------------------
st.subheader("📊 Key Performance Indicators")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Customers",
    f"{total_customers:,}"
)

c2.metric(
    "Churned Customers",
    f"{churned_customers:,}"
)

c3.metric(
    "Overall Churn Rate",
    f"{churn_rate:.2%}"
)

c4.metric(
    "Inactive Churn",
    f"{inactive_churn:.2%}"
)

c5.metric(
    "High-Value Disengaged Churn",
    f"{high_value_churn:.2%}"
)

st.divider()

# -----------------------------
# Geography Analysis
# -----------------------------
st.subheader("🌍 Geography-wise Churn")

geo = (
    df_filtered.groupby("Geography")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum")
    )
    .reset_index()
)

geo["Churn Rate"] = geo["Churned"] / geo["Customers"]

fig_geo = px.bar(
    geo,
    x="Geography",
    y="Churn Rate",
    text=geo["Churn Rate"].map(lambda x: f"{x:.2%}"),
    title="Customer Churn Rate by Geography"
)

fig_geo.update_yaxes(tickformat=".0%")
st.plotly_chart(fig_geo, use_container_width=True)

# -----------------------------
# Age & Tenure
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("👥 Age Group Churn")

    age = (
        df_filtered.groupby("Age Group", observed=False)
        .agg(
            Customers=("CustomerId", "count"),
            Churned=("Exited", "sum")
        )
        .reset_index()
    )

    age["Churn Rate"] = age["Churned"] / age["Customers"]

    fig_age = px.bar(
        age,
        x="Age Group",
        y="Churn Rate",
        text=age["Churn Rate"].map(lambda x: f"{x:.2%}"),
        title="Churn Rate by Age Group"
    )

    fig_age.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_age, use_container_width=True)

with col2:
    st.subheader("📅 Tenure Churn")

    tenure = (
        df_filtered.groupby("Tenure Group", observed=False)
        .agg(
            Customers=("CustomerId", "count"),
            Churned=("Exited", "sum")
        )
        .reset_index()
    )

    tenure["Churn Rate"] = tenure["Churned"] / tenure["Customers"]

    fig_tenure = px.bar(
        tenure,
        x="Tenure Group",
        y="Churn Rate",
        text=tenure["Churn Rate"].map(lambda x: f"{x:.2%}"),
        title="Churn Rate by Tenure"
    )

    fig_tenure.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_tenure, use_container_width=True)

# -----------------------------
# Balance Analysis
# -----------------------------
st.subheader("💰 Balance Segment Churn")

balance = (
    df_filtered.groupby("Balance Segment")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum")
    )
    .reset_index()
)

balance["Churn Rate"] = balance["Churned"] / balance["Customers"]

fig_balance = px.bar(
    balance,
    x="Balance Segment",
    y="Churn Rate",
    text=balance["Churn Rate"].map(lambda x: f"{x:.2%}"),
    title="Customer Churn Rate by Balance Segment"
)

fig_balance.update_yaxes(tickformat=".0%")
st.plotly_chart(fig_balance, use_container_width=True)

# -----------------------------
# Credit Score
# -----------------------------
st.subheader("📈 Credit Score Analysis")

credit = (
    df_filtered.groupby("Credit Score Band", observed=False)
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum")
    )
    .reset_index()
)

credit["Churn Rate"] = credit["Churned"] / credit["Customers"]

fig_credit = px.bar(
    credit,
    x="Credit Score Band",
    y="Churn Rate",
    text=credit["Churn Rate"].map(lambda x: f"{x:.2%}"),
    title="Customer Churn Rate by Credit Score"
)

fig_credit.update_yaxes(tickformat=".0%")
st.plotly_chart(fig_credit, use_container_width=True)

# -----------------------------
# Engagement & Product Count
# -----------------------------
st.subheader("📦 Engagement & Product Churn")

engagement = (
    df_filtered.groupby(["IsActiveMember", "NumOfProducts"])
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum")
    )
    .reset_index()
)

engagement["Churn Rate"] = (
    engagement["Churned"] / engagement["Customers"]
)

engagement["Engagement"] = engagement["IsActiveMember"].map(
    {0: "Inactive", 1: "Active"}
)

fig_engagement = px.bar(
    engagement,
    x="NumOfProducts",
    y="Churn Rate",
    color="Engagement",
    barmode="group",
    text=engagement["Churn Rate"].map(lambda x: f"{x:.2%}"),
    title="Customer Churn Rate by Engagement and Product Count"
)

fig_engagement.update_yaxes(tickformat=".0%")
st.plotly_chart(fig_engagement, use_container_width=True)

# -----------------------------
# High-Value Disengaged Customers
# -----------------------------
st.subheader("💎 High-Value Disengaged Customer Explorer")

hv = df_filtered[
    (df_filtered["Balance"] >= 97198.54) &
    (df_filtered["IsActiveMember"] == 0)
].copy()

hv_total = len(hv)
hv_churned = int(hv["Exited"].sum())

h1, h2, h3 = st.columns(3)

h1.metric("High-Value Disengaged Customers", f"{hv_total:,}")
h2.metric("Churned", f"{hv_churned:,}")
h3.metric(
    "Churn Rate",
    f"{(hv_churned / hv_total):.2%}" if hv_total else "0.00%"
)

if hv_total > 0:
    st.dataframe(
        hv[
            [
                "CustomerId",
                "Geography",
                "Gender",
                "Age",
                "Balance",
                "NumOfProducts",
                "IsActiveMember",
                "Exited"
            ]
        ].head(100),
        use_container_width=True
    )

# -----------------------------
# Summary
# -----------------------------
st.divider()

st.subheader("📌 Executive Summary")

st.write(
    f"""
    - The filtered customer base contains **{total_customers:,} customers**.
    - The observed churn rate is **{churn_rate:.2%}**.
    - Inactive customers show a churn rate of **{inactive_churn:.2%}**.
    - High-value disengaged customers show a churn rate of **{high_value_churn:.2%}**.
    - The dashboard allows customer segments to be explored dynamically using the sidebar filters.
    """
)

st.caption(
    "Note: These results describe observed patterns in the European Bank dataset "
    "and should not be interpreted as causal relationships."
)
