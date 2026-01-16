import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime

st.title("Hive Five")
st.write("Hive Five est une application de gestion de réservation de machines")

# Chargement des données
df = pd.read_csv("data_clean/reservations_clean.csv")

# Conversion des dates
df['start_date'] = pd.to_datetime(df['start_date'])
df['end_date'] = pd.to_datetime(df['end_date'])

# Conversion de la durée en minutes pour les calculs
def duration_to_minutes(duration_str):
    try:
        if pd.isna(duration_str):
            return 0
        parts = str(duration_str).split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 60 + minutes + seconds / 60
        return 0
    except:
        return 0

df['duration_minutes'] = df['duration'].apply(duration_to_minutes)

# Sidebar pour les filtres
st.sidebar.header("Filtres")
teams = st.sidebar.multiselect("Sélectionner les équipes", options=sorted(df['name'].unique()), default=sorted(df['name'].unique()))
date_range = st.sidebar.date_input("Période", value=[df['start_date'].min().date(), df['start_date'].max().date()])

# Application des filtres
df_filtered = df[df['name'].isin(teams)]
if len(date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered['start_date'].dt.date >= date_range[0]) & 
        (df_filtered['start_date'].dt.date <= date_range[1])
    ]

st.header("📊 Statistiques des réservations")

# Métriques principales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total réservations", len(df_filtered))
col2.metric("Équipes actives", df_filtered['name'].nunique())
col3.metric("Machines utilisées", df_filtered['name_device'].nunique())
col4.metric("Durée totale (heures)", f"{df_filtered['duration_minutes'].sum() / 60:.1f}")

st.divider()

# Graphique 1: Nombre de machines utilisées par équipe
st.subheader("🔧 Nombre de machines uniques utilisées par équipe")
machines_par_equipe = df_filtered.groupby('name')['name_device'].nunique().reset_index()
machines_par_equipe.columns = ['Équipe', 'Nombre de machines']
machines_par_equipe = machines_par_equipe.sort_values('Nombre de machines', ascending=False)

fig1 = px.bar(
    machines_par_equipe, 
    x='Équipe', 
    y='Nombre de machines',
    color='Nombre de machines',
    color_continuous_scale='Blues',
    title="Nombre de machines différentes utilisées par chaque équipe"
)
fig1.update_layout(xaxis_tickangle=-45, height=400)
st.plotly_chart(fig1, use_container_width=True)

# Graphique 2: Nombre de réservations par équipe
st.subheader("📈 Nombre de réservations par équipe")
reservations_par_equipe = df_filtered.groupby('name').size().reset_index(name='Nombre de réservations')
reservations_par_equipe = reservations_par_equipe.sort_values('Nombre de réservations', ascending=False)

fig2 = px.bar(
    reservations_par_equipe,
    x='name',
    y='Nombre de réservations',
    color='Nombre de réservations',
    color_continuous_scale='Greens',
    title="Nombre total de réservations par équipe"
)
fig2.update_layout(xaxis_tickangle=-45, height=400)
st.plotly_chart(fig2, use_container_width=True)

# Graphique 3: Top 15 machines les plus utilisées
st.subheader("🏆 Top 15 machines les plus utilisées")
machines_populaires = df_filtered.groupby('name_device').size().reset_index(name='Nombre d\'utilisations')
machines_populaires = machines_populaires.sort_values('Nombre d\'utilisations', ascending=False).head(15)
machines_populaires = machines_populaires.sort_values('Nombre d\'utilisations', ascending=True)  # Inverser pour avoir le plus en haut

fig3 = px.bar(
    machines_populaires,
    x='Nombre d\'utilisations',
    y='name_device',
    orientation='h',
    color='Nombre d\'utilisations',
    color_continuous_scale='Reds',
    title="Les 15 machines les plus réservées"
)
fig3.update_layout(height=500)
st.plotly_chart(fig3, use_container_width=True)

# Graphique 4: Répartition par localisation
st.subheader("📍 Répartition des réservations par localisation")
location_dist = df_filtered.groupby('name_location').size().reset_index(name='Nombre de réservations')
location_dist = location_dist.sort_values('Nombre de réservations', ascending=False)

fig4 = px.pie(
    location_dist,
    values='Nombre de réservations',
    names='name_location',
    title="Répartition des réservations par salle/location"
)
st.plotly_chart(fig4, use_container_width=True)

# Graphique 5: Évolution temporelle des réservations
st.subheader("📅 Évolution temporelle des réservations")
df_filtered['date'] = df_filtered['start_date'].dt.date
reservations_temporelles = df_filtered.groupby('date').size().reset_index(name='Nombre de réservations')
reservations_temporelles = reservations_temporelles.sort_values('date')

fig5 = px.bar(
    reservations_temporelles,
    x='date',
    y='Nombre de réservations',
    title="Nombre de réservations par jour",
    color='Nombre de réservations',
    color_continuous_scale='Viridis'
)
fig5.update_layout(height=400, xaxis_tickangle=-45)
st.plotly_chart(fig5, use_container_width=True)

# Graphique 6: Durée moyenne d'utilisation par équipe
st.subheader("⏱️ Durée moyenne d'utilisation par équipe (en heures)")
duree_par_equipe = df_filtered.groupby('name')['duration_minutes'].mean().reset_index()
duree_par_equipe['Durée moyenne (heures)'] = duree_par_equipe['duration_minutes'] / 60
duree_par_equipe = duree_par_equipe.sort_values('Durée moyenne (heures)', ascending=False)

fig6 = px.bar(
    duree_par_equipe,
    x='name',
    y='Durée moyenne (heures)',
    color='Durée moyenne (heures)',
    color_continuous_scale='Purples',
    title="Durée moyenne d'utilisation des machines par équipe"
)
fig6.update_layout(xaxis_tickangle=-45, height=400)
st.plotly_chart(fig6, use_container_width=True)

# Graphique 7: Répartition par type d'équipe (startup, IPGG, etc.)
st.subheader("🏢 Répartition par type d'organisation")
type_counts = {
    'Startup': df_filtered['is_startup'].sum(),
    'IPGG': df_filtered['is_ipgg'].sum(),
    'ESPCI': df_filtered['is_espci'].sum(),
    'PCUP': df_filtered['is_pcup'].sum()
}
type_df = pd.DataFrame(list(type_counts.items()), columns=['Type', 'Nombre de réservations'])

fig7 = px.bar(
    type_df,
    x='Type',
    y='Nombre de réservations',
    color='Type',
    title="Nombre de réservations par type d'organisation"
)
st.plotly_chart(fig7, use_container_width=True)

# Graphique 8: Utilisation des machines par équipe (graphique en barres groupées)
st.subheader("🔥 Utilisation des machines par équipe")
heatmap_data = df_filtered.groupby(['name', 'name_device']).size().reset_index(name='Nombre')

# Limiter aux top machines pour la lisibilité
top_machines = df_filtered.groupby('name_device').size().nlargest(10).index
heatmap_data_filtered = heatmap_data[heatmap_data['name_device'].isin(top_machines)]

fig8 = px.bar(
    heatmap_data_filtered,
    x='name_device',
    y='Nombre',
    color='name',
    title="Top 10 machines les plus utilisées par équipe",
    labels={'name_device': 'Machine', 'Nombre': 'Nombre de réservations', 'name': 'Équipe'},
    barmode='group'
)
fig8.update_layout(height=500, xaxis_tickangle=-45)
st.plotly_chart(fig8, use_container_width=True)

st.divider()
st.subheader("📋 Données brutes")
st.dataframe(df_filtered, use_container_width=True)

