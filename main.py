import streamlit as st
from supabase import create_client, Client
import hashlib


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
      ["Análisis de Votantes", "Analisis de Edad", "Página 3"],
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

def pagina3():
    st.title("📄 Página 3")
    st.write("Contenido de la tercera página.")
    # Más cosas luego


# ========================
#  MAIN CONTENT
# ========================
if st.session_state["login"]:
  pagina = st.session_state.get("pagina_actual", "Página 1")

  if pagina == "Análisis de Votantes":
    pagina1()
  elif pagina == "Analisis de Edad":
    pagina2()
  elif pagina == "Página 3":
    pagina3()

else:
  st.title("Bienvenido a QCP 🗳")
  st.info("➡️ Iniciá sesión desde el menú lateral para continuar.")
