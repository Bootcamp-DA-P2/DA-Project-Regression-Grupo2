import requests
from dotenv import load_dotenv
import os

load_dotenv()
URL_BACKEND = os.getenv('URL_BACKEND')
URL_BACKEND_COMPETITIONS = os.getenv('URL_BACKEND_COMPETITIONS')
URL_BACKEND_CLUBS = os.getenv('URL_BACKEND_CLUBS')
URL_BACKEND_PLAYERS = os.getenv('URL_BACKEND_PLAYERS')

def get_competitions():
    try:
        response = requests.get(URL_BACKEND_COMPETITIONS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Error al obtener las competiciones: {response.status_code} - {response.text}')
            return None
    except Exception as e:
        print(f'Error con la conexión a la API de comepticiones: {e}')
        return None


def get_clubs():
    try:
        response = requests.get(URL_BACKEND_CLUBS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Error al obetener los clubes: {response.status_code} - {response.text}')
            return None
    except Exception as e:
        print(f'Error con la conexión a la API de clubes: {e}')
        return None
    
def get_players():
    try:
        response = requests.get(URL_BACKEND_PLAYERS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Error al obtener los jugadores: {response.status_code} - {response.text}')
            return None
    except Exception as e:
        print(f'Error con la conexión a la API de jugadores: {e}')
        return None