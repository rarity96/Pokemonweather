import smtplib, ssl, pokemon_logic
import sqlite3
import hashlib
from email.message import EmailMessage
import streamlit as st
import random, requests
import pokebase as pb
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

def sql_con():
    con = sqlite_connect()
    c = con.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS pokemon (
        id        INTEGER,
        user_id   INTEGER NOT NULL,
        name      TEXT,
        type      TEXT,
        lvl       INTEGER DEFAULT 1,
        total_exp INTEGER DEFAULT 0,
        city      TEXT,
        temp      REAL,
        image_url TEXT,
        PRIMARY KEY (id, user_id),
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
    )""")


    c.execute("""
               CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                last_login text
                poke_num INTEGER DEFAULT 0
                )
        """)



    con.commit()



if 'weather_state' not in st.session_state:
    st.session_state['weather_state'] = None
if 'last_city' not in st.session_state:
    st.session_state['last_city'] = ""
if "is_auth" not in st.session_state:
    st.session_state.is_auth = False
if "user" not in st.session_state:
    st.session_state.user = None

def kelvin_to_celcius(temperature):
        celcius = temperature - 273.15
        return celcius

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

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
         st.info("Input a city to get the weather")
         return None
     url = f'http://api.openweathermap.org/data/2.5/weather?appid={weather_key}&q={city}&lang=pl'
     result = requests.get(url).json()
     kelvin = result['main']['temp']
     celc = kelvin_to_celcius(kelvin)
     desc = result['weather'][0]['description']
     return {"city": city, "celc": celc, "desc": desc, "raw": result}

def gain_exp():
    return random.randint(1, 2)

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
        return st.warning("Wrong password")
    if check_pass[0] == password and len(password) > 8:
        return True
    else:
        return st.warning("Wrong password")

def render_login():
    with st.form("login form"):
        input_username = text_input("Username")
        input_password = text_input("Password", type='password')
        submit = form_submit_button("Login")

        if submit:
            if len(input_password) < 8:
                st.warning("The password should be > 8 char")
            else:
                password = hash_password(input_password)
                check_login = checking_login(input_username, password)
                password = check_password(input_username, password)
                if check_login == True and password == True:
                    session_state.is_auth = True
                    session_state.username = input_username
                    rerun()
                else:
                    st.warning("Bad password")


    # *********************************************************** City input part
def render_main():
    if session_state.is_auth == False:
        render_login()
    else:
        if st.button("Logout"):
            st.session_state.is_auth = False
            st.session_state.username = False
            st.rerun()
        st.info(f"You are logged in as {st.session_state.username}")
    col1, col2 = st.columns([1, 0.12])
    with col1:
     input_city = st.text_input("Input city name", placeholder="City", key="Input_city_mainpage")
    with col2:
     with st.popover("🛈", use_container_width=True):
         st.markdown("###Zasady działania")
         st.markdown(
             """-Input a city name for which one you would like to check the weather'   
             -Based on currently weather, pokemon will be choose and add to your pokedex.   
             -Every encounter will be save in database. (Exp and lvl are rising with every next encounter witch catched pokemon)"""
         )


    CITY = str(input_city).capitalize()


    def render_weather_block(state: dict):
        if not state:
            return
        celc =state['celc']
        pogoda =state['raw']
        city =state['city']
        st.write(f'In {city} the temp is: {celc:.1f}°C')
        st.write(f'Weather conditions: {pogoda["weather"][0]["description"]}')
        st.write(f'Speed of wind: {pogoda["wind"]["speed"]} m/s')
        st.spinner("Draw a pokemon...")
        st.write(f"Your pokemon: {state['pokemon_name']}, type: {state['pokemon_types']}")
        login_status = state.get('login_status')
        if state.get('img_url'):
            st.image(state['img_url'], width=800)
    # *******************************************************
    if st.button('Check the weather'):
     with st.spinner('Getting data...'):
         exp = gain_exp()
         sql_con()
         weather = get_weather(CITY)
         if not weather:
             st.stop()
         con = sqlite_connect()
         c = con.cursor()
         user_id = None
         c.execute("UPDATE user SET poke_num = poke_num + 1 WHERE name = ?",(st.session_state.username,))
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
                 st.info(f"You already have this pokemon! Your {pokemon_name} is gaining {exp} exp")
                 c.execute(
                     "UPDATE pokemon SET total_exp = total_exp + ?, lvl = ? WHERE id = ? AND user_id = ?",
                     (exp, new_lvl, pokemon_id, user_id)
                 )
                 con.commit()
             else:
                 st.info(f"Congrats! {st.session_state.username}! It is your first {pokemon_name}")
         else:
             st.info("Please login to save your new pokemon to database")

         st.session_state["weather_state"] = {
             **weather,
             'pokemon_id': pokemon_id,
             'pokemon_name': pokemon_name,
             'pokemon_types': p['types'],
             'img_url': img_url,
         }

    render_weather_block(st.session_state.get('weather_state'))

render_main()