import smtplib, ssl, pokemon_logic
import sqlite3
import hashlib
from email.message import EmailMessage
import streamlit as st
import random, requests
import pokebase as pb
import base64
from datetime import datetime


weather_key = st.secrets['apis']["weather_key"]
sender = st.secrets['email']["sender"]
pw = st.secrets['email']['pw']
receiver = st.secrets['email']['receiver']
currency_key = st.secrets['apis']['currency_key']


@st.cache_resource
def sqlite_connect():
    con = sqlite3.connect('pokeweather.db', check_same_thread=False)
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    return con


if 'weather_state' not in st.session_state:
    st.session_state['weather_state'] = None
if 'last_city' not in st.session_state:
    st.session_state['last_city'] = ""

def sql_con():
    con = sqlite_connect()
    c = con.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS pokemon (
            id  INTEGER PRIMARY KEY,
            name  TEXT UNIQUE,
            type TEXT,
            lvl INTEGER DEFAULT 1,
            total_exp INTEGER DEFAULT 0,
            city text,
            temp REAL,
            image_url TEXT
        )""")

    c.execute("""
               CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                last_login text
                )
        """)



    con.commit()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def kelvin_to_celcius(temperature):
        celcius = temperature - 273.15
        return celcius

def temp_to_type(celc: float, desc) -> str:
    desc = desc.lower()
    if "mgła" in desc or "zamglenie" in desc:
        return "ghost"
    elif "deszcz" in desc or "mżawka" in desc:
        return "water"
    elif celc < 10:
        return "ice"
    elif celc < 16:
        return "normal"
    elif celc < 22:
        return "grass"
    else:
        return "fire"




def send_email(mail_content: str, mail_back: str):
    port = 465 # For SSL
    smtp_server = "smtp.gmail.com"
    msg = EmailMessage()
    msg["Subject"] = "Wiadomość z pokeweather"
    msg["from"] = sender
    msg["to"] = receiver

    message = f"""
    {mail_content}
    ___________
    Wiadomość od:
    {mail_back or "(Brak)"}
 """
    msg.set_content(message)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
         server.login(sender, pw)
         server.send_message(msg)

def get_weather(city):
     if not CITY:
         st.info("Podaj nazwe miasta by sprawdzić pogodę")
         return None, None
     url = f'http://api.openweathermap.org/data/2.5/weather?appid={weather_key}&q={CITY}&lang=pl'
     result = requests.get(url).json()
     kelvin = result['main']['temp']
     celc = kelvin_to_celcius(kelvin)
     desc = result['weather'][0]['description']
     return {"city": city, "celc": celc, "desc": desc, "raw": result}


# ******************************************************* Login Part
col_log, col_pw = st.columns([0.5, 0.5])
with col_log:
    username = st.text_input("Nazwa użytkownika", placeholder="Not working yet", key="input_name_login")
with col_pw:
    password = st.text_input("Hasło", placeholder="Not working yet", type="password", key="input_password")
# *********************************************************** City input part
col1, col2 = st.columns([1, 0.12])
with col1:
 input_city = st.text_input("Podaj miasto", placeholder="Nazwa miasta", key="Input_city_mainpage")
with col2:
 with st.popover("🛈", use_container_width=True):
     st.markdown("###Zasady działania")
     st.markdown(
         """-Wpisz miasto dla którego chcesz poznać pogode i kliknij 'Sprawdź pogode'   
         -Na podstawie aktualnej pogody, zostanie wylosowany pokemon który trafi do twojego pokedex'u.   
         -Każde spotkanie zapisywane jest w bazie (Exp i poziom rosna przy każdym kolejnym spotkaniu złapanego poka"""
     )

CITY = str(input_city).capitalize()


def render_weather_block(state: dict):
    if not state:
        return
    celc =state['celc']
    pogoda =state['raw']
    city =state['city']
    st.write(f'W {city} aktualna temperatura to {celc:.1f}°C')
    st.write(f'Warunki pogodowe: {pogoda["weather"][0]["description"]}')
    st.write(f'Prędkość wiatru: {pogoda["wind"]["speed"]} m/s')
    st.write(f"Twój wylosowany pokemon to: {state["pokemon_name"]}, typ: {state["pokemon_types"]}")
    if state.get('img_url'):
        st.image(state['img_url'], width=800)
# *******************************************************
if st.button('Sprawdz pogode'):
 with st.spinner('Getting data...'):
     # rate = check_currency()
     # st.write(f"USD/PLN: {rate:.2f}")
     weather = get_weather(CITY)
     if not weather:
         st.stop()
     wanted_type = temp_to_type(weather['celc'], weather['desc'])
     p = pokemon_logic.get_pokemon(preferred_type=wanted_type)
     sql_con()
     pokemon_id = p['id']
     img_url = pokemon_logic.get_pokemon_image(pokemon_id)
     if img_url:
         st.image(img_url, width=800, caption=None)
     else:
         st.info("Brak obrazka dla tego poksa")
     new_lvl = pokemon_logic.calculate_exp(pokemon_id)
     pokemon_name = p['name']
     types_str = ",".join([t.type.name for t in pb.pokemon(pokemon_id).types])
     con = sqlite_connect()
     c = con.cursor()
     before = con.total_changes
     c.execute("INSERT OR IGNORE INTO pokemon(id, name, type, city, temp, image_url) values(?, ?, ?, ?, ?, ?)",
               (pokemon_id, pokemon_name, types_str, CITY, weather['celc'], img_url))
     con.commit()
     inserted = (con.total_changes - before) > 0
     if not inserted:
         st.info("Tego pokemona już złapałeś! Dostajesz za to 1 exp")
         c.execute("UPDATE pokemon SET total_exp = total_exp + 1, lvl = ? WHERE id = ?",
                   (new_lvl, pokemon_id,))
         # c.execute("UPDATE pokemon SET lvl = ? WHERE id = ?", (new_lvl, pokemon_id,))
         con.commit()
     else:
         st.info("Gratulacje! Złapałeś tego pokemona po raz pierwszy")

     st.session_state["weather_state"] = {
         **weather,
         'pokemon_id': pokemon_id,
         'pokemon_name': pokemon_name,
         'pokemon_types': p['types'],
         'img_url': img_url,
     }

render_weather_block(st.session_state.get('weather_state'))