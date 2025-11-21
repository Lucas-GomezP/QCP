import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go


def inferir_votantes_octubre():
  st.title("Estimación de θ (por franja etaria y partido) - Octubre")

  # -----------------------------
  # Cargar datos
  # -----------------------------
  df_theta = pd.read_csv("data/theta_estimates.csv")
  df_ci = pd.read_csv("data/theta_bootstrap_summary.csv")

  # Asegurar que la columna age_group sea string
  df_theta["age_group"] = df_theta["age_group"].astype(str)

  # -----------------------------
  # HEATMAP (primer gráfico)
  # -----------------------------
  st.subheader("Heatmap de θ por franja x partido")

  df_heat = df_theta.set_index("age_group")

  fig_heatmap = px.imshow(
      df_heat,
      color_continuous_scale="Viridis",
      aspect="auto",
      labels=dict(color="Prob"),
  )

  fig_heatmap.update_layout(
      xaxis_tickangle=-60,
      width=1300,
      height=600,
  )

  st.plotly_chart(fig_heatmap, width="stretch")
  st.markdown("""
  ### ¿Qué muestra este gráfico?
  Este mapa de calor muestra **cómo varía la probabilidad estimada (θ)** de que una persona de cierta franja etaria vote a determinado partido.

  ### ¿Cómo leerlo?
  - Cada **fila** es una franja etaria.
  - Cada **columna** es un partido.
  - Los colores indican **qué tan alta es la probabilidad**:
    - Colores claros → probabilidad alta.
    - Colores oscuros → probabilidad baja.

  ### ¿Para qué sirve?
  Permite ver **tendencias generales**, por ejemplo:
  - qué partidos son más fuertes en edades jóvenes o mayores;
  - dónde hay patrones homogéneos o contrastes entre grupos.
  """)

  st.markdown("---")
  # -----------------------------
  # Radio para elegir tipo de gráfico
  # -----------------------------
  st.subheader("Intervalo de confianza de θ")

  tipo = st.radio(
      "¿Cómo querés mostrar los intervalos?",
      ["Por franja etaria", "Por partido", "Todos los partidos por franja (punto + CI)"]
  )

  # -----------------------------
  # Función: estilo matplotlib en Plotly
  # -----------------------------
  def plot_bars_with_ci_plotly(theta, thetas_boot, parties, AGE_LABELS):
      G, P = theta.shape
      x = np.arange(G)

      fig = go.Figure()

      for p in range(P):
          med = theta[:, p]

          if thetas_boot is not None and not np.isnan(thetas_boot).all():
              lows = np.percentile(thetas_boot[:, :, p], 2.5, axis=0)
              highs = np.percentile(thetas_boot[:, :, p], 97.5, axis=0)

              fig.add_trace(go.Scatter(
                  x=x,
                  y=med,
                  mode='markers',
                  name=parties[p],
                  error_y=dict(
                      type='data',
                      symmetric=False,
                      array=highs - med,
                      arrayminus=med - lows,
                      thickness=1.5,
                      width=3
                  )
              ))
          else:
              fig.add_trace(go.Scatter(
                  x=x,
                  y=med,
                  mode='lines+markers',
                  name=parties[p]
              ))

      fig.update_layout(
          title='Distribución por franja etaria por partido (punto + 95% CI)',
          xaxis=dict(
              tickmode='array',
              tickvals=x,
              ticktext=AGE_LABELS,
              title='Franja etaria'
          ),
          yaxis=dict(title='Probabilidad estimada'),
          legend=dict(x=1.02, y=1, orientation='v'),
          margin=dict(l=40, r=150, t=80, b=40),
          height=500
      )

      return fig


  # -----------------------------
  # MODO 1: Por franja etaria
  # -----------------------------
  if tipo == "Por franja etaria":
      
      grupos = df_ci["age_group"].unique().tolist()
      seleccionado = st.selectbox("Elegir franja etaria", grupos)

      df_sel = df_ci[df_ci["age_group"] == seleccionado]

      fig_ci = go.Figure()

      fig_ci.add_trace(go.Scatter(
          x=df_sel["party"],
          y=df_sel["theta_50"],
          mode="markers",
          marker=dict(size=10),
          name="θ median"
      ))

      fig_ci.add_trace(go.Scatter(
          x=df_sel["party"],
          y=df_sel["theta_2.5"],
          mode="lines",
          line=dict(width=0),
          showlegend=False
      ))

      fig_ci.add_trace(go.Scatter(
          x=df_sel["party"],
          y=df_sel["theta_97.5"],
          fill='tonexty',
          mode="lines",
          line=dict(width=0),
          name="IC 95%"
      ))

      fig_ci.update_layout(
          xaxis_tickangle=-60,
          title=f"Intervalos de confianza - {seleccionado}",
          width=1300,
          height=600
      )

      st.plotly_chart(fig_ci, width="stretch")
      st.markdown("""
      ### ¿Qué muestra este gráfico?
      Para una **franja etaria seleccionada**, mostramos la probabilidad estimada (θ) de votar a cada partido.

      ### ¿Cómo leerlo?
      - **Puntos:** muestran la estimación central (mediana) de la probabilidad.
      - **Sombra entre líneas:** representa el **intervalo de confianza del 95%**.
      - Indica la zona donde se espera que esté el valor real según las simulaciones.
      - Una sombra más ancha = más incertidumbre.
      - Una sombra más estrecha = estimación más precisa.

      ### ¿Qué significa?
      Ayuda a comparar **partido por partido dentro de un mismo grupo de edad**, viendo tanto la estimación como la incertidumbre.
      """)


  # -----------------------------
  # MODO 2: Por partido
  # -----------------------------

  elif tipo == "Por partido":
      
      partidos = df_ci["party"].unique().tolist()
      seleccionado = st.selectbox("Elegir partido", partidos)

      df_sel = df_ci[df_ci["party"] == seleccionado]

      fig_ci = go.Figure()

      fig_ci.add_trace(go.Scatter(
          x=df_sel["age_group"],
          y=df_sel["theta_50"],
          mode="markers",
          marker=dict(size=10),
          name="θ median"
      ))

      fig_ci.add_trace(go.Scatter(
          x=df_sel["age_group"],
          y=df_sel["theta_2.5"],
          mode="lines",
          line=dict(width=0),
          showlegend=False
      ))

      fig_ci.add_trace(go.Scatter(
          x=df_sel["age_group"],
          y=df_sel["theta_97.5"],
          fill='tonexty',
          mode="lines",
          line=dict(width=0),
          name="IC 95%"
      ))

      fig_ci.update_layout(
          xaxis_tickangle=-30,
          title=f"Intervalos de confianza - {seleccionado}",
          width=1100,
          height=500
      )

      st.plotly_chart(fig_ci, width="stretch")
      st.markdown("""
      ### ¿Qué muestra este gráfico?
      Para un **partido seleccionado**, mostramos cómo cambia la probabilidad estimada (θ) según la franja etaria.

      ### ¿Cómo leerlo?
      - **Puntos:** estimación central (mediana).
      - **Sombra:** intervalo de confianza del 95%.
      - Mirá la dirección de los puntos:
      - Si suben → mayor apoyo en edades mayores.
      - Si bajan → mayor apoyo en edades jóvenes.

      ### ¿Qué significa?
      Permite ver la **composición etaria del voto** de cada partido y qué tan segura es esa estimación.
      """)


  # -----------------------------
  # MODO 3: Estilo matplotlib en Plotly
  # -----------------------------
  else:
      

      parties = df_theta.columns.drop("age_group").tolist()
      AGE_LABELS = df_theta["age_group"].tolist()

      theta = df_theta.drop(columns=["age_group"]).values  # G × P

      # Como no tenemos bootstrap B×G×P en este CSV → usar None
      thetas_boot = None

      fig = plot_bars_with_ci_plotly(theta, thetas_boot, parties, AGE_LABELS)
      st.plotly_chart(fig, width="stretch")
      st.markdown("""
      ### ¿Qué muestra este gráfico?
      Es una visualización estilo científico que muestra, para cada franja etaria y partido, la **probabilidad estimada (θ)** acompañada de su **intervalo de confianza**.

      ### ¿Cómo leerlo?
      - **Cada punto** representa la estimación central (mediana) de θ.
      - **Las barras verticales** son el intervalo de confianza del 95%.
      - Muestran la variabilidad que surge de las simulaciones bootstrap.
      - Barras largas → más incertidumbre.
      - Barras cortas → estimaciones más estables.

      ### ¿Qué aporta este gráfico?
      Ayuda a ver **diferencias finas** entre partidos dentro de cada edad, con énfasis en cuán confiables son las estimaciones.
      """)