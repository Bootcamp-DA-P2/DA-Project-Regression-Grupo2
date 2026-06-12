import streamlit as st
from streamlit_option_menu import option_menu
from services.services import get_competitions, get_clubs, get_players
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import joblib
import os

# Para iniciar el frontend, ejecuta el siguiente comando en la terminal desde la carpeta frontend:
# python -m streamlit run app.py

@st.cache_resource
def cargar_modelo(nombre_modelo):
    modelos_archivos = {
        'Regresión Lineal': 'linear_regression_model.pkl',
        'K-NN': 'knn_regressor_model.pkl',
        'XGBoost' : 'xgboost_model.pkl'
    }
    archivo = modelos_archivos.get(nombre_modelo)
    if archivo:
        ruta_completa = os.path.join('..', 'models', archivo)
        return joblib.load(ruta_completa)
    return None

@st.cache_data
def cargar_datos(function):
    return function



st.set_page_config(
    page_title="Predicciones de Fútbol",
    page_icon="⚽",
    layout="wide"
)

selected = option_menu(None, ["Predicciones", "Competiciones", "Clubes", 'Jugadores'],
    icons=['cash-coin', 'trophy', "dribbble", 'gem'], menu_icon="cast", default_index=0, orientation="horizontal")

if selected == 'Predicciones':
    st.title('Simulador de Valor de Mercado')
    st.subheader('Introduce las características del jugador para calcular su precio')

    df_players = pd.DataFrame(cargar_datos(get_players()))

    
    # Creamos un formulario para agrupar todos los inputs y que no se recargue la página a cada click
    with st.form("formulario_prediccion"):
        clubes = df_players['club_name'].unique().tolist()
        paises = df_players['country_of_birth'].unique().tolist()
        posiciones = df_players['position'].unique().tolist()
        ligas = df_players['league_id'].unique().tolist()
        
        # FILA 1: Modelo y Datos Categóricos
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            modelo_selected = st.selectbox(
                'Modelo de predicción', 
                options=['Regresión Lineal', 'K-NN', 'XGBoost'],
                index=0
            )
        with col2:
            position = st.selectbox('Posición', options=posiciones)
        with col3:
            club_name = st.selectbox('Club', options=clubes)
        with col4:
            league_id = st.selectbox('ID de la Liga', options=ligas)
            
        # FILA 2: Datos Numéricos y País
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            country_of_birth = st.selectbox('País de Nacimiento', options=paises)
        with col6:
            age = st.number_input('Edad', min_value=15, max_value=45, value=25, step=1)
        with col7:
            last_season = st.number_input('Última Temporada activa', min_value=2020, max_value=2026, value=2025, step=1)
        with col8:
            height_in_cm = st.slider('Altura (cm)', min_value=150, max_value=210, value=180, step=1)
            
        # Botón de envío dentro del formulario
        st.write("")
        btn_predict = st.form_submit_button('Predecir Valor de Mercado', type='primary')

    # 3. Lógica al pulsar el botón
    if btn_predict:
        with st.spinner('Calculando...'):
            try:
                # Cargar el modelo elegido
                pipeline = cargar_modelo(modelo_selected)
                
                # Construir el diccionario con las claves EXACTAS que espera el ColumnTransformer
                datos_jugador = {
                    'position': [position],
                    'club_name': [club_name],
                    'league_id': [league_id],
                    'country_of_birth': [country_of_birth],
                    'age': [age],
                    'last_season': [last_season],
                    'height_in_cm': [height_in_cm]
                }
                
                # Convertir a DataFrame (una sola fila)
                X_nuevo = pd.DataFrame(datos_jugador)
                
                # Realizar predicción
                prediccion = pipeline.predict(X_nuevo)[0]
                
                # Control por si la Regresión Lineal da valores negativos
                if prediccion < 0:
                    prediccion = 0
                
                # Mostrar resultado de impacto en la UI
                st.success(f'### ¡Resultados del simulador!')
                st.metric(
                    label=f"Valor estimado con {modelo_selected}", 
                    value=f"{prediccion:,.2f} €"
                )
                
            except Exception as e:
                st.error(f"Error en la predicción. Asegúrate de que las opciones ingresadas coincidan con las que el modelo conoce: {e}")

elif selected == 'Competiciones':
    st.title('Competiciones')
    competitions = cargar_datos(get_competitions())
    st.table(competitions)

elif selected == 'Clubes':
    st.title('Clubes')
    clubs = cargar_datos(get_clubs())
    st.dataframe(clubs)

elif selected == 'Jugadores':
    st.title('Jugadores')
    players = cargar_datos(get_players())
    df_players = pd.DataFrame(players)
    df_players = df_players.drop(columns=['id', 'club_id'])
    gb = GridOptionsBuilder.from_dataframe(df_players)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_side_bar()
    grid_options = gb.build()
    AgGrid(df_players, gridOptions=grid_options, theme="blue")