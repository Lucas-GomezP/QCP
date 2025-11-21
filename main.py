import streamlit as st
from supabase import create_client, Client
import hashlib
from io import StringIO
import pandas as pd

# ========================
#  SUPABASE CONNECTION
# ========================
@st.cache_resource
def init_connection():
  url = st.secrets["SUPABASE_URL"]
  key = st.secrets["SUPABASE_KEY"]
  return create_client(url, key)

supabase = init_connection()

SALT = st.secrets["SALT"]


@st.cache_data(show_spinner="Cargando datos TSV...")
def load_tsv_from_supabase(bucket: str, filename: str) -> pd.DataFrame:
  """
  Descarga un archivo .tsv desde Supabase Storage y lo convierte en DataFrame.
  La función está cacheada mientras dure la sesión del usuario.
  """

  try:
    # Descargar archivo desde un bucket PRIVADO
    response = supabase.storage.from_(bucket).download(filename)

    # Convertir bytes → string
    text_data = response.decode("utf-8")

    # Leer TSV
    df = pd.read_csv(
      StringIO(text_data),
      sep="\t",           # MUY IMPORTANTE PARA TSV
      dtype=str,          # Previene errores por columnas mixtas
      low_memory=False,   # Recomendado para archivos grandes
    )

    return df

  except Exception as e:
    st.error(f"❌ Error al cargar TSV: {e}")
    return pd.DataFrame()


# ========================
#  HASH FUNCTION
# ========================
def hash_password(usuario: str, password: str) -> str:
    texto = f"{usuario}{password}{SALT}"
    return hashlib.sha256(texto.encode()).hexdigest()


# ========================
#  STREAMLIT CONFIG
# ========================
st.set_page_config(page_title="QCP", page_icon="🗳", layout="wide")

if "login" not in st.session_state:
    st.session_state["login"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None


# ========================
#  SUPABASE QUERIES
# ========================
def run_query_login(usuario_input):
    return supabase.table("users").select("id, name, password").eq("name", usuario_input).single().execute()


# ========================
#  SIDEBAR
# ========================
with st.sidebar:
  st.title("🔐 Panel")

  # ----------------------------------------
  # CASE 1: NO LOGUEADO
  # ----------------------------------------
  if not st.session_state["login"]:
    usuario_input = st.text_input("Usuario")
    contrasenia_input = st.text_input("Contraseña", type="password")
    login_btn = st.button("Iniciar sesión")

    if login_btn:
      # ========================
      #  CONSULTA A SUPABASE
      # ========================
      try:
        response = run_query_login(usuario_input)
        if response.data is None:
          st.error("❌ Usuario no encontrado")
        else:
          usuario_db = response.data["name"] # type: ignore
          password_hash_db = response.data["password"] # type: ignore

          password_hash_input = hash_password(usuario_input, contrasenia_input)

          if password_hash_input == password_hash_db:
            st.session_state["login"] = True
            st.session_state["username"] = usuario_db
            st.success("✅ Sesión iniciada correctamente")
            st.rerun()
          else:
            st.error("❌ Contraseña incorrecta")

      except Exception as e:
        st.error(f"Error en la autenticación: {e}")

  # ----------------------------------------
  # CASE 2: LOGUEADO
  # ----------------------------------------
  else:
    st.success(f"Bienvienid@ **{st.session_state['username']}**")

    # Selector de página
    st.session_state["pagina_actual"] = st.radio(
      "📄 Navegación",
      ["Análisis de Votantes", "Analisis de Edad", "Analisis por Zona", "INFERIR SEGUN YO"],
    )

    if st.button("Cerrar sesión"):
      st.session_state["login"] = False
      st.session_state["username"] = None
      st.rerun()


# ========================
# PÁGINAS COMO FUNCIONES
# ========================

from ElectoresConocidos01 import pagina1


from ElectoresPorEdad02 import pagina2

from ElectoresPorZonaConocidos03 import pagina3

from InferirVotantes04 import inferir_votantes_octubre


# ========================
#  MAIN CONTENT
# ========================
if st.session_state["login"]:
  pagina = st.session_state.get("pagina_actual", "Página 1")
  # df = load_tsv_from_supabase("padron", "padron/padron_con_voto_geolocalizado.tsv")
  # files = supabase.storage.from_("padron").list()
  # st.write(files)
  df = pd.read_csv("./data/padron_con_voto_geolocalizado.tsv", sep="\t")
  if pagina == "Análisis de Votantes":
    pagina1(df)
  elif pagina == "Analisis de Edad":
    pagina2(df)
  elif pagina == "Analisis por Zona":
    pagina3(df)
  elif pagina == "INFERIR SEGUN YO":
    inferir_votantes_octubre()

else:
  st.title("Bienvenido a QCP 🗳")
  st.info("➡️ Iniciá sesión desde el menú lateral para continuar.")
