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

