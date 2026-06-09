import streamlit as st

from streamlit_option_menu import option_menu

from services.services import get_competitions, get_clubs, get_players

import pandas as pd

from st_aggrid import AgGrid, GridOptionsBuilder



# Para iniciar el frontend, ejecuta el siguiente comando en la terminal desde la carpeta frontend:

# python -m streamlit run app.py





st.set_page_config(

    page_title="Predicciones de Fútbol",

    page_icon="⚽",

    layout="wide"

)





selected = option_menu(None, ["Predicciones", "Competiciones", "Clubes", 'Jugadores'],

    icons=['cash-coin', 'trophy', "dribbble", 'gem'], menu_icon="cast", default_index=0, orientation="horizontal")



if selected == 'Predicciones':

    st.title('Predicciones')



    col1, col2, col3 = st.columns(3)

    with col1:

        modelo_selected = st.selectbox('Selecciona el modelo de predicción', placeholder='Elige un modelo', options=['Regresión Lineal', 'Árbol de Decisión', 'Random Forest', 'XGBoost'], index=None)

    with col2:

        player_selected = st.selectbox('Selecciona el jugador para predecir su valor', placeholder='Elige un jugador', options=['Lionel Messi', 'Cristiano Ronaldo', 'Neymar Jr.', 'Kylian Mbappé'], index=None)

    with col3:

        st.write('')

        st.write('')

        btn_predict = st.button('Predecir', type='primary', disabled=not (modelo_selected and player_selected))



    st.info('Aquí se mostrarán las predicciones del valor de mercado del jugador seleccionado utilizando el modelo de predicción elegido.')



    if player_selected and modelo_selected and btn_predict:

        st.success(f'Predicción del valor de mercado de {player_selected} utilizando el modelo {modelo_selected}.')

    else:

        st.warning('Por favor, selecciona un modelo de predicción y un jugador para mostrar las predicciones.')



elif selected == 'Competiciones':

    st.title('Competiciones')



    st.table(get_competitions())

elif selected == 'Clubes':

    st.title('Clubes')



    st.table(get_clubs())

elif selected == 'Jugadores':

    st.title('Jugadores')



    players = get_players()

    df_players = pd.DataFrame(players)

    df_players = df_players.drop(columns=['id', 'club_id'])

    gb = GridOptionsBuilder.from_dataframe(df_players)

    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)

    gb.configure_side_bar()

    grid_options = gb.build()

    AgGrid(df_players, gridOptions=grid_options, theme="blue")