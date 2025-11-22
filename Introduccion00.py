import streamlit as st

def pagina0 ():
  st.title("Introducción")

  st.subheader("De que se trata")
  st.markdown("""
              Este proyecto se concentra en un analisis electoral politico, demografico y estrategico de los resultados de las elecciones, utilizando los datos sacados del padron electoral legislativas de 2025 y la recopilacion de los resultados de escrutinio por mesa. 
              
              Buscando trascender el resultado electoral para identificar el votante Rosaleño.
              """)
  
  st.subheader("Con que data contamos")
  st.markdown("""
              * Padron Electoral 2025
              * Escrutinio por mesa de octubre
              * Escrutinio definitivo de octubre
              * Votantes efectivos de 108 mesas de septiembre
              * Votantes efectivos de 83 mesas de octubre
              """)

  st.subheader("Como se va a trabajar")
  st.markdown("""
              Dado que el voto es secreto, trabajamos con probabilidades. Gracias a los padrones por mesa, sabemos fehacientemente quienes fuueron a votar pero no tenemos informacion de las mesas cuyos padrones no encontramos ni devolvieron. Para clasificar la informaciond de los padrones obtenidos, se cargo en una planilla de excel el numero de mesa y numero de orden de cada elector y esto nos permitio cruzar los datos con el padron general que contiene la informacion mas detallada de cada elector (DNI, ano de nacimiento, direccion, genero, etc)

              Tenemos una recopilacion de los resultados obtenidos en cada mesa de las elecciones de octubre, esto nos permiote saber la posibilidad que tiene cada fuerzxa de ser elegida en cada mesa. Sabenmos el resultado, queremos averiguar como se llega a esto, respondienndo a las preguntas: que hace que un elector elija una fuerza politica y no otra? que caracteristicas humanas determinan esa eleccion? Buscamos crear la identidad del "Votante Modelo" rosalenio y poder caracterizarlo. 
              
              """)
  
  st.subheader("Informacion faltante")
  st.markdown("""
              * Escrutinio por mesa de septiembre
              * 45 padrones de mesa de las elecciones de septiembre
              * 70 padrones de mesa de las elecciones de octubre
              """)
  
  st.subheader("Preguntas disparadoras")
  st.markdown("""
              
              """)