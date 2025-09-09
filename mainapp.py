import smtplib, ssl, pokemon_logic
import sqlite3
import hashlib
import pandas as pd
from email.message import EmailMessage
import streamlit as st
import random, requests
import pokebase as pb
import base64
from datetime import datetime

from streamlit import session_state, text_input, form_submit_button, rerun

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
if 'is_auth' not in st.session_state:
    session_state.is_auth = False
if 'username' not in st.session_state:
    session_state.username = False

def sql_con():
    con = sqlite_connect()
    c = con.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS pokemon (
        id        INTEGER,                 -- id gatunku
        user_id   INTEGER NOT NULL,        -- właściciel rekordu
        name      TEXT,
        type      TEXT,
        lvl       INTEGER DEFAULT 1,
        total_exp INTEGER DEFAULT 0,
        city      TEXT,
        temp      REAL,
        image_url TEXT,
        PRIMARY KEY (id, user_id),         -- [FIX-PER-USER]
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
    )""")


    c.execute("""
               CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL UNIQUE,
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
     if not city:
         st.info("Podaj nazwe miasta by sprawdzić pogodę")
         return None
     url = f'http://api.openweathermap.org/data/2.5/weather?appid={weather_key}&q={city}&lang=pl'
     result = requests.get(url).json()
     kelvin = result['main']['temp']
     celc = kelvin_to_celcius(kelvin)
     desc = result['weather'][0]['description']
     return {"city": city, "celc": celc, "desc": desc, "raw": result}


def checking_login(username, password):
    sql_con()
    con = sqlite_connect()
    c = con.cursor()
    check_username = c.execute("SELECT name FROM user WHERE name = ?", (username,)).fetchone()
    if check_username is None:
        c.execute("INSERT INTO user (name, password_hash) values (?, ?)", (username, password))
        st.info("stworzyłeś swoje konto!")
        con.commit()
        return True
    else:
        return True


def check_password(username, password):
    sql_con()
    con = sqlite_connect()
    c = con.cursor()
    check_pass = c.execute("SELECT password_hash FROM user WHERE name = ?", (username,)).fetchone()
    if not check_pass:
        return st.warning("Złe hasło")
    if check_pass[0] == password and len(password) > 8:
        return True
    else:
        return st.warning("Złe hasło")

def render_login():
    with st.form("login form"):
        input_username = text_input("Nazwa użytkownika")
        input_password = text_input("Hasło", type='password')
        submit = form_submit_button("Zaloguj")
        if submit:
            password = hash_password(input_password)
            check_login = checking_login(input_username, password)
            password = check_password(input_username, password)
            if check_login == True and password == True:
                session_state.is_auth = True
                session_state.username = input_username
                rerun()
            else:
                st.warning("Złe hasło")

    # *********************************************************** City input part
def render_main():
    if session_state.is_auth == False:
        render_login()
    else:
        if st.button("Wyloguj"):
            st.session_state.is_auth = False
            st.session_state.username = False
            st.rerun()
        st.info(f"Jesteś zalogowany jako {st.session_state.username}")
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
        st.write(f"Twój wylosowany pokemon to: {state['pokemon_name']}, typ: {state['pokemon_types']}")
        login_status = state.get('login_status')
        if state.get('img_url'):
            st.image(state['img_url'], width=800)
    # *******************************************************
    if st.button('Sprawdz pogode'):
     with st.spinner('Getting data...'):
         sql_con()
         weather = get_weather(CITY)
         if not weather:
             st.stop()
         con = sqlite_connect()
         c = con.cursor()
         user_id = None
         if st.session_state.get("is_auth") and st.session_state.get("username"):
             row = c.execute("SELECT id FROM user WHERE name = ?", (st.session_state.username,)).fetchone()
             if row:
                 user_id = row[0]
         wanted_type = temp_to_type(weather['celc'], weather['desc'])
         p = pokemon_logic.get_pokemon(preferred_type=wanted_type)
         pokemon_id = p['id']
         img_url = pokemon_logic.get_pokemon_image(pokemon_id)
         pokemon_name = p['name']
         types_str = ",".join([t.type.name for t in pb.pokemon(pokemon_id).types])
         if user_id is not None:
             before = con.total_changes
             c.execute(
                 "INSERT OR IGNORE INTO pokemon(id, user_id, name, type, city, temp, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 (pokemon_id, user_id, pokemon_name, types_str, CITY, weather['celc'], img_url)
             )
             inserted = (c.rowcount == 1)
             con.commit()

             if not inserted:
                 new_lvl = pokemon_logic.calculate_exp(pokemon_id, user_id)
                 st.info("Tego pokemona już złapałeś! Dostajesz za to 1 exp")
                 c.execute(
                     "UPDATE pokemon SET total_exp = total_exp + 1, lvl = ? WHERE id = ? AND user_id = ?",
                     (new_lvl, pokemon_id, user_id)
                 )
                 con.commit()
             else:
                 st.info(f"Gratulacje {st.session_state.username}! Złapałeś tego pokemona po raz pierwszy")
         else:
             st.info("Zaloguj się, aby zapisać pokemona do twojego pokedexu!")

         st.session_state["weather_state"] = {
             **weather,
             'pokemon_id': pokemon_id,
             'pokemon_name': pokemon_name,
             'pokemon_types': p['types'],
             'img_url': img_url,
         }

    render_weather_block(st.session_state.get('weather_state'))

render_main()