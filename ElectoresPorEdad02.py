import pandas as pd
import plotly.express as px
import streamlit as st


def electores_por_edad(df):
  

  # ============================
  # Cargar TSV
  # ============================
  

  # ============================
  # Calcular edad
  # ============================
  ANIO_ACTUAL = 2025
  df["edad"] = ANIO_ACTUAL - df["fecha_nacimiento"]

  # ============================
  # Clasificar rangos etarios
  # ============================
  def clasificar_rango(edad):
    if 16 <= edad <= 24:
      return "16-24"
    elif 25 <= edad <= 30:
      return "25-30"
    elif 31 <= edad <= 44:
      return "31-44"
    elif 45 <= edad <= 60:
      return "45-60"
    elif edad > 60:
      return "61+"
    else:
      return None  # menores de 16 se descartan

  df["rango_edad"] = df["edad"].apply(clasificar_rango)

  # Eliminar las filas sin rango válido
  df = df.dropna(subset=["rango_edad"])

  # ============================
  # Limpiar columna voto
  # ============================
  # Convertimos a booleano real o None
  df["voto"] = df["voto_septiembre"].map(lambda x: True if x is True else (False if x is False else None))

  # Sacar las filas con voto = None (gente sin información de voto)
  df_votos = df.dropna(subset=["voto_septiembre"])

  # ============================
  # Agrupar y contar
  # ============================
  conteo = df_votos.groupby(["rango_edad", "voto_septiembre"]).size().unstack(fill_value=0)
  conteo.columns = ["No votó", "Votó"]
  conteo = conteo[["Votó", "No votó"]]  # orden lógico

  # ============================
  # Gráfico Plotly
  # ============================
  fig = px.bar(
    conteo,
    x=conteo.index,
    y=["Votó", "No votó"],
    barmode="group",
    title="Participación electoral por rango etario",
    category_orders={"rango_edad": ["16-24", "25-30", "31-44", "45-60", "61+"]},
    color_discrete_map={
      "Voto": "#2ecc71",
      "No voto": "#e74c3c"
    },
  )

  fig.update_layout(
    xaxis_title="Rango de edad",
    yaxis_title="Cantidad de personas",
    legend_title_text="Estado del voto",
    hovermode="x unified",
  )

  st.plotly_chart(fig, width="stretch")
  # ============================
  # Porcentajes de participación
  # ============================

  # Usamos SOLO personas con información (True/False)
  df_info = df.dropna(subset=["voto_septiembre"])

  # Total por rango (solo con info real)
  totales = df_info.groupby("rango_edad").size()

  # Cantidad que votaron por rango
  votaron = df_info[df_info["voto_septiembre"] == True].groupby("rango_edad").size()

  # Construir tabla
  tabla_pct = pd.DataFrame({
      "Total con información": totales,
      "Votaron": votaron
  }).fillna(0)

  tabla_pct["Votaron"] = tabla_pct["Votaron"].astype(int)
  tabla_pct["Participación (%)"] = (
      tabla_pct["Votaron"] / tabla_pct["Total con información"] * 100
  ).round(2)

  # Orden lógico
  tabla_pct = tabla_pct.loc[["16-24", "25-30", "31-44", "45-60", "61+"]]

  st.subheader("📊 Porcentaje de participación por rango etario (solo personas con información)")
  st.dataframe(tabla_pct)

def pagina2(df):
  st.title("Participación por rango etario")
  col1, col2 = st.columns(2)
  with col1:
    # df = pd.read_csv("./data/padron_con_voto_septiembre.tsv", sep="\t")
    electores_por_edad(df)
  with col2:
    st.text("Cambiar cuando se tenga el padron de octubre")