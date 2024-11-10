import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px 

conn = None
try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="airflow",
        user="airflow",
        password="airflow"
    )
    st.success("Connexion réussie !")
except psycopg2.OperationalError as e:
    st.error(f"Erreur opérationnelle : {e}")

def query_database(sql_query):
    with conn.cursor() as cur:
        cur.execute(sql_query)
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    return pd.DataFrame(data, columns=columns)

st.title("MasterCard vs Visa : Tableau de bord des insights")

st.sidebar.header("Options de requêtes")

table_name = st.sidebar.text_input("Entrez le nom de la table", "MVR")
limit = st.sidebar.number_input("Limite des résultats", min_value=1, max_value=1000, value=100, step=10)

if conn:
    query = f"SELECT * FROM \"{table_name}\" LIMIT {limit};"
    df = query_database(query)
    
    st.write("Aperçu des données", df)
    
    columns_to_display = st.multiselect("Sélectionnez les colonnes à afficher", options=df.columns, default=df.columns)
    filtered_df = df[columns_to_display]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Insights sur les prix")
        st.subheader("MasterCard vs Visa : Prix de clôture")
        fig = px.line(filtered_df, x='Date', y=['Close_M', 'Close_V'], 
                      labels={'Date': 'Date', 'value': 'Prix'}, 
                      title='Prix de clôture de MasterCard et Visa')
        st.plotly_chart(fig)

        st.subheader("Changement de prix")
        fig_pct_change = px.line(filtered_df, x='Date', y=['Pct_Change_M', 'Pct_Change_V'],
                                 labels={'Date': 'Date', 'value': 'Changement en pourcentage'},
                                 title='Changement en pourcentage des prix au fil du temps')
        st.plotly_chart(fig_pct_change)

        st.header("Insights sur le risque et la volatilité")
        st.subheader("Volatilité des prix au fil du temps")
        fig_volatility = px.line(filtered_df, x='Date', y=['Volatility_M', 'Volatility_V'],
                                 labels={'Date': 'Date', 'value': 'Volatilité'},
                                 title='Volatilité des prix pour MasterCard et Visa')
        st.plotly_chart(fig_volatility)

    with col2:
        st.header("Insights sur le volume")
        st.subheader("Volumes des transactions")
        fig_volumes = px.bar(filtered_df, x='Date', y=['Volume_M', 'Volume_V'],
                             title="Volumes des transactions pour MasterCard et Visa")
        st.plotly_chart(fig_volumes)

        st.subheader("Moyennes mobiles des prix et des volumes")
        fig_moving_avg = px.line(filtered_df, x='Date', y=['MA7_Close_M', 'MA7_Close_V', 'MA30_Close_M', 'MA30_Close_V'],
                                  title='Moyennes mobiles sur 7 jours et 30 jours des prix de clôture')
        st.plotly_chart(fig_moving_avg)

        st.subheader("Moyennes mobiles des volumes")
        fig_volume_ma = px.line(filtered_df, x='Date', y=['Volume_MA7_M', 'Volume_MA7_V'],
                                title="Moyenne mobile sur 7 jours des volumes")
        st.plotly_chart(fig_volume_ma)

    st.header("Insights avancés")
    st.subheader("Ratio volume / prix")
    fig_vol_price_ratio = px.line(filtered_df, x='Date', y='Volume_Ratio_MV',
                                  title="Ratio volume / prix pour MasterCard et Visa")
    st.plotly_chart(fig_vol_price_ratio)

    st.header("Sentiment du marché et prise de décision")
    st.subheader("Changement de prix vs volume pour le sentiment du marché")
    fig_sentiment = px.scatter(filtered_df, x='Pct_Change_M', y='Volume_Ratio_MV', color='Date',
                               labels={'Pct_Change_M': 'Changement de prix', 'Volume_Ratio_MV': 'Ratio volume / prix'},
                               title='Sentiment du marché : Changement de prix vs Volume')
    st.plotly_chart(fig_sentiment)

    st.header("Répartition du volume")
    total_volume_mc = filtered_df['Volume_M'].sum()
    total_volume_v = filtered_df['Volume_V'].sum()

    pie_data = pd.DataFrame({
        'Carte': ['MasterCard', 'Visa'],
        'Volume': [total_volume_mc, total_volume_v]
    })

    pie_fig = px.pie(pie_data, names='Carte', values='Volume', title='Répartition du volume : MasterCard vs Visa')
    st.plotly_chart(pie_fig)

else:
    st.warning("Connexion à la base de données impossible.")
