import streamlit as st
import pandas as pd
import pydeck as pdk
from shapely.geometry import Polygon


def mapa_electores_conocidos(df):

    # =============================
    # 1) Cargar polígonos
    # =============================
    df_poly = pd.read_csv("data/zonas_coronel_rosales.tsv", sep="\t")

    # Normalizar zona y polígono
    df_poly["zona"] = df_poly["zona"].astype(str).str.strip()
    df_poly["poligono"] = df_poly["poligono"].astype(str).str.strip()

    # Crear key uniforme
    df_poly["key"] = df_poly["zona"] + " - " + df_poly["poligono"]

    # =============================
    # 2) Normalizar votantes
    # =============================
    df_votos = df.copy()

    df_votos["zona"] = df_votos["zona"].astype(str).str.strip()
    df_votos["poligono"] = df_votos["poligono"].astype(str).str.strip()

    df_votos["key"] = df_votos["zona"] + " - " + df_votos["poligono"]

    # =============================
    # 3) Verificar claves que no coinciden
    # =============================
    keys_poligonos = set(df_poly["key"].unique())
    keys_votos = set(df_votos["key"].unique())

    faltantes = keys_votos - keys_poligonos

    if len(faltantes) > 0:
        st.warning("⚠️ Polígonos sin coincidencia en el mapa:\n" + "\n".join(sorted(faltantes)))

    # =============================
    # 4) Construir diccionario de polígonos
    # =============================
    poligonos = {}
    for key, grupo in df_poly.groupby("key"):
        grupo_sorted = grupo.sort_values("orden")
        coords = grupo_sorted[["lon", "lat"]].values.tolist()
        poligonos[key] = coords

    # =============================
    # 5) Conteo por polígono
    # =============================
    conteo = df_votos.groupby("key").size().reset_index(name="cantidad")

    # =============================
    # 6) Centroides de cada polígono
    # =============================
    centroides_data = []

    for key, coords in poligonos.items():
        poly = Polygon(coords)
        cx, cy = poly.centroid.x, poly.centroid.y

        cantidad = conteo.loc[conteo["key"] == key, "cantidad"]
        cantidad = int(cantidad.values[0]) if len(cantidad) else 0

        centroides_data.append({
            "key": key,
            "lon": cx,
            "lat": cy,
            "cantidad": cantidad,
            "zona": key.split(" - ")[0]  # ej "ZONA 2"
        })

    df_centroides = pd.DataFrame(centroides_data)

    # =============================
    # 7) Colores por zona
    # =============================
    zona_colores = {
        "ZONA 1": [255, 87, 51, 120],    # naranja suave
        "ZONA 2": [70, 130, 180, 120],   # celeste / steelblue
        "ZONA 3": [60, 179, 113, 120],   # verde suave
        "ZONA 4": [186, 85, 211, 120],   # violeta pastel
    }

    def asignar_color(zona):
        return zona_colores.get(zona, [200, 200, 200, 120])

    df_poly["zona_color"] = df_poly["zona"].apply(asignar_color)

    # =============================
    # 8) Capas de PyDeck
    # =============================

    # POLYGON LAYER
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=[{
            "polygon": poligonos[key],
            "zona": key.split(" - ")[0],
            "color": asignar_color(key.split(" - ")[0])
        } for key in poligonos.keys()],
        get_polygon="polygon",
        get_fill_color="color",
        get_line_color=[0, 0, 0],
        line_width_min_pixels=1,
        pickable=True,
    )

    # TEXT LAYER → cantidad por polígono
    text_layer = pdk.Layer(
        "TextLayer",
        data=df_centroides,
        get_position='[lon, lat]',
        get_text="cantidad",
        get_size=28,
        get_color=[0, 0, 0],
        get_alignment_baseline="'center'",
        billboard=True,
    )

    # =============================
    # 9) Vista inicial
    # =============================
    view_state = pdk.ViewState(
        latitude=df_votos["lat"].mean(),
        longitude=df_votos["lon"].mean(),
        zoom=12,
    )

    deck = pdk.Deck(
        layers=[polygon_layer, text_layer],
        initial_view_state=view_state,
        tooltip={"text": "{zona}"} # type: ignore
    )

    st.pydeck_chart(deck)


# =====================================
# PÁGINA STREAMLIT
# =====================================
def pagina3(df):
    st.title("🗺️ Mapa de Votantes Geolocalizados")
    st.markdown("---")
    mapa_electores_conocidos(df)
    st.markdown("## 📊 Análisis por Zona y Polígono")
    st.markdown("### Distribución de Género y Profesión")

    # ============================
    #   LIMPIEZA PROFESIÓN
    # ============================
    df2 = df.copy()
    df2["profesion"] = df2["profesion"].astype(str).str.upper().str.strip()

    categorias_especiales = ["SIN OCUPACION", "ESTUDIANTE", "NO CONSTA", "JUBILADO"]

    def clasificar_profesion(x):
        if x in categorias_especiales:
            return x
        if x == "" or x == "NAN" or pd.isna(x):
            return "SIN DATO"
        return "OTRAS"

    df2["profesion_categoria"] = df2["profesion"].apply(clasificar_profesion)

    # ============================
    #   TABLA DE GÉNERO
    # ============================
    genero_tabla = (
        df2.pivot_table(
            index=["zona", "poligono"],
            columns="genero",
            values="nro_documento",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )

    # ============================
    #   TABLA DE PROFESIÓN
    # ============================
    profesion_tabla = (
        df2.pivot_table(
            index=["zona", "poligono"],
            columns="profesion_categoria",
            values="nro_documento",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )

    # ============================
    #   UNIFICAR TODO
    # ============================
    tabla_final = genero_tabla.merge(
        profesion_tabla, on=["zona", "poligono"], how="outer"
    ).fillna(0)

    # Ordenar mejor
    columnas_orden = (
        ["zona", "poligono"]
        + sorted([c for c in tabla_final.columns if c not in ["zona", "poligono"]])
    )

    tabla_final = tabla_final[columnas_orden]

    # ============================
    #   MOSTRAR TABLA
    # ============================
    st.dataframe(tabla_final, use_container_width=True)
