# import smtplib, ssl
import sqlite3
# import freecurrencyapi
import streamlit as st
import random, requests
import pandas as pd
import os
import pokebase as pb
from datetime import datetime

#*******************************************************
input_city = st.text_input("Podaj miasto", placeholder="Szczecin")
#*******************************************************

weather_key = st.secrets['apis']["weather_key"]
sender = st.secrets['email']["sender"]
pw = st.secrets['email']['pw']
receiver = st.secrets['email']['receiver']
currency_key = st.secrets['apis']['currency_key']
CITY = str(input_city)

@st.cache_resource
def sqlite_connect():
    con = sqlite3.connect('pokeweather.db', check_same_thread=False)
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    return con

def sql_con():
    con = sqlite_connect()
    c = con.cursor()
    check_table_pokemon = c.execute("""SELECT name 
                                        FROM sqlite_master
                                        WHERE type='table' AND name='pokemon'""")
    fetch_check_table_pokemon = c.fetchone()

    if fetch_check_table_pokemon == None:
        c.execute("""CREATE TABLE pokemon (
                id  INTEGER PRIMARY KEY,
                name  TEXT UNIQUE,
                type TEXT,
                lvl INTEGER,
                total_exp INTEGER
            )""")

    con.commit()


def kelvin_to_celcius(temperature):
    celcius = temperature - 273.15
    return celcius

def get_weather():
    if not CITY:
        st.info("Podaj nazwe miasta by sprawdzić pogodę")
        return None, None
    url = f'http://api.openweathermap.org/data/2.5/weather?appid={weather_key}&q={CITY}&lang=pl'
    result = requests.get(url).json()
    kelvin = result['main']['temp']
    celc = kelvin_to_celcius(kelvin)
    st.write(f'Temp aktualnie: {celc:.2f}°C')
    st.write(f'Opis: {result["weather"][0]["description"]}')
    st.write(f'Prędkość wiatru {result["wind"]["speed"]}m/s')
    return celc, result
#
def get_pokemon(preferred_type):
    lvl = 1
    exp = 0
    if preferred_type:
        pokemon = get_random_pokemon_by_type(preferred_type, 151)
        if pokemon is None:
            random_id = random.randint(1, 151)
            pokemon = pb.pokemon(random_id)
    else:
        random_id = random.randint(1,151)
        pokemon = pb.pokemon(random_id)
    # total_count = 151
    #
    # random_id = random.randint(1, total_count)
    # pokemon = pb.pokemon(random_id)
    st.write(f"ID: {pokemon.id}")
    st.write(f"Nazwa: {pokemon.name.capitalize()}")
    st.write(f"Wzrost: {pokemon.height}")

    types = [t.type.name for t in pokemon.types]
    st.write("Type:", ", ".join(types))
    img_url = get_pokemon_image(pokemon.id, prefer='official')
    if img_url:
        st.image(img_url,width=800, caption=None)
    else:
        st.info("Brak obrazka dla tego poksa")
    return {"id": pokemon.id, "name": pokemon.name.capitalize(), "lvl": lvl, "exp":exp}

def get_pokemon_image(pokemon_id, prefer="official") -> str| None:
    pokemon = pb.pokemon(pokemon_id)
    image = pokemon.sprites

    if prefer == "official":
        try:
            url = image.other['official-artwork']['front_default']
            if url:
                return url
        except Exception:
            pass
    url = getattr(image, 'front_default', None)
    if url:
        return url

    try:
        return image.other['home']['front_default']
    except Exception:
        return None

def calculate_lvl(pokemon_id, pokemon_name):
    con = sqlite_connect()
    c = con.cursor()
    check_if_exist = c.execute("SELECT lvl FROM pokemon WHERE id = ?", (pokemon_id,)).fetchone()
    if check_if_exist is None:
        st.info(f"Gratulacje, złapałeś {pokemon_name}!")
        return None
    current_lvl = check_if_exist[0]
    if current_lvl is not None and current_lvl < 2:
        c.execute("UPDATE pokemon SET lvl = ? WHERE id = ?", (2, pokemon_id))
        con.commit()
        current_lvl = 2
        st.info(f"Gratulacje, twój {pokemon_name} awansował na {current_lvl} poziom")
    else:
        st.write(f"poziom {pokemon_name}: {current_lvl}")
    return current_lvl

# def check_currency():
#      client = freecurrencyapi.Client(currency_key)
#      final_currency = client.latest('USD', currencies=['PLN'])
#      return final_currency['data']['PLN']

def temp_to_type(celc: float) -> str:
    if celc < 10:
        return "ice"
    elif celc < 16:
        return "normal"
    elif celc < 22:
        return "grass"
    else:
        return "fire"

@st.cache_data
def get_ids_by_type(type_name, max_id = 151) -> list[int]:

    typ = pb.type_(type_name)
    ids = []
    for i in typ.pokemon:
        url = i.pokemon.url
        pok_id = int(url.rstrip("/").split("/")[-1])
        if pok_id <= max_id:
            ids.append(pok_id)
    return ids

def get_random_pokemon_by_type(type_name: str, max_id: int = 151):
    """Losuje jednego Pokémona z listy typu; zwraca obiekt pokebase.pokemon."""
    ids = get_ids_by_type(type_name, max_id)
    if not ids:
        return None
    pid = random.choice(ids)
    return pb.pokemon(pid)

# def send_email(rate, pokemon):
#     port = 465 # For SSL
#    smtp_server = "smtp.gmail.com"
#     message = f"""\
#  Subject: Kurs USD/PLN
#
# Aktualna wartosc: {rate:.2f}
#  Pokemon na dzisiaj:
#  ID:{pokemon['id']}. {pokemon['name']}
#  """
#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#          server.login(sender, pw)
#          server.sendmail(sender, receiver, message)

if st.button('refresh'):
    with st.spinner('Getting data...'):
        # rate = check_currency()
        # st.write(f"USD/PLN: {rate:.2f}")
        celc, pogoda = get_weather()
        if celc is None:
            st.stop()
        wanted_type = temp_to_type(celc)
        p = get_pokemon(preferred_type=wanted_type)
        # send_email(rate, p)
        st.write(f'In {CITY}temp today is: {celc:.2f}°C')
        st.write(f"Wylosowany poks typu {wanted_type}: {p['name']}")
        sql_con()

        pokemon_id = p['id']
        pokemon_name = p['name']
        lvl = p['lvl']
        total_exp = p['exp']
        types_str = ",".join([t.type.name for t in pb.pokemon(pokemon_id).types])
        con = sqlite_connect()
        c = con.cursor()
        before = con.total_changes
        c.execute("INSERT OR IGNORE INTO pokemon(id, name, type, lvl, total_exp) values(?, ?, ?, ?, ?)",
                  (pokemon_id, pokemon_name, types_str , lvl, total_exp))
        con.commit()
        inserted = (con.total_changes - before) > 0
        if not inserted:
            c.execute("UPDATE pokemon SET lvl = CASE WHEN lvl < 2 THEN 2 ELSE lvl END WHERE id = ?", (pokemon_id,))
            con.commit()

        with st.expander("Pokémony w bazie"):
            rows = c.execute("SELECT id, name, type, lvl, total_exp FROM pokemon ORDER BY id").fetchall()
            df = pd.DataFrame(rows, columns=["ID", "Nazwa", "Typ", 'lvl', 'total_exp'])
            st.dataframe(df)
if st.button('delete db'):
    con = sqlite_connect()
    c = con.cursor()
    c.execute("DROP TABLE IF EXISTS pokemon")
    con.commit()
    st.success("Tabela 'pokemon' została usunięta.")
# while True:

#     rate = check_currency()
#     pokemon = get_pokemon()
#     # send_email(rate, pokemon)
#     time.sleep(60)`