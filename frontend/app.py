import streamlit as st
from streamlit_option_menu import option_menu
from services.services import get_competitions, get_clubs, get_players

selected = option_menu(None, ["Predicciones", "Competiciones", "Clubes", 'Jugadores'], 
    icons=['cash-coin', 'trophy', "dribbble", 'gem'], menu_icon="cast", default_index=0, orientation="horizontal")

if selected == 'Predicciones':
    st.title('Predicciones')
elif selected == 'Competiciones':
    st.title('Competiciones')
elif selected == 'Clubes':
    st.title('Clubes')
elif selected == 'Jugadores':
    st.title('Jugadores')