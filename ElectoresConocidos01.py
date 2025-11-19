import streamlit as st
import pandas as pd
import plotly.express as px

def elecotes_conocidos(df):

  # ===============================================================
  # 1️⃣ PRIMER GRÁFICO  
  # True o False (tienen info) vs None (no hay información)
  # ===============================================================

  df["tiene_informacion"] = df["voto"].apply(lambda x: "Con información" if x in [True, False] else "Sin información")

  conteo_info = df["tiene_informacion"].value_counts().reset_index()
  conteo_info.columns = ["categoria", "cantidad"]

  fig1 = px.pie(
    conteo_info,
    names="categoria",
    labels=["Electores con informacion", "Electores sin informacion"],
    values="cantidad",
    title="Cobertura de información (Con info vs Sin info)",
    color=["Electores con informacion", "Electores sin informacion"],
    color_discrete_map={
      "Electores con informacion": "#2ecc71",
      "Electores sin informacion": "#e74c3c"
    },
  )

  fig1.update_traces(
    pull=[0.1, 0],
    hovertemplate="%{label}<br>%{value} votos",
    textinfo="label+percent"
  )

  st.plotly_chart(fig1, width="stretch")


  # ===============================================================
  # 2️⃣ SEGUNDO GRÁFICO  
  # True vs False (solo personas con información)
  # ===============================================================

  df_filtrado = df[df["voto"].isin([True, False])]

  conteo_tf = df_filtrado["voto"].value_counts().reset_index()
  conteo_tf.columns = ["voto", "cantidad"]
  conteo_tf["voto"] = conteo_tf["voto"].map({True: "Votó", False: "No votó"})

  fig2 = px.pie(
    conteo_tf,
    names="voto",
    labels=["Votos efectuados", "Votos no efectuados"],
    values="cantidad",
    title="Votantes conocidos (Votó vs No votó)",
    color=["Votos efectuados", "Votos no efectuados"],
    color_discrete_map={
      "Votos efectuados": "#2ecc71",
      "Votos no efectuados": "#e74c3c"
    },
  )

  fig2.update_traces(
    pull=[0.1, 0],
    hovertemplate="%{label}<br>%{value} votos",
    textinfo="label+percent"
  )

  st.plotly_chart(fig2, width="stretch")


def elecotes_conocidos_octubre():
  st.subheader("Análisis de Votantes (Octubre)")
  st.write("Cambiar cuando se tenga el padron de octubre")

def pagina1(df):
  st.title("Análisis de Votantes")
  col1, col2 = st.columns(2)
  with col1:
    st.subheader("(Septiembre)")
    # df = pd.read_csv("./data/padron_con_voto_septiembre.tsv", sep="\t")
    elecotes_conocidos(df)
  with col2:
    elecotes_conocidos_octubre()
    # df = pd.read_csv("./data/padron_con_voto_octubre.tsv", sep="\t")
    # elecotes_conocidos(df, "Octubre")