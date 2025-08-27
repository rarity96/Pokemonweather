import smtplib, ssl
# import freecurrencyapi
import streamlit as st
import random, requests
import os, time
import pokebase as pb

#*******************************************************
input_city = st.text_input("Podaj miasto", placeholder="Szcecin")
#*******************************************************

weather_key = st.secrets['apis']["weather_key"]
sender = st.secrets['email']["sender"]
pw = st.secrets['email']['pw']
receiver = st.secrets['email']['receiver']
currency_key = st.secrets['apis']['currency_key']
CITY = str(input_city)


def kelvin_to_celcius(temperature):
    celcius = temperature - 273.15
    return celcius

def get_weather():
    url = f'http://api.openweathermap.org/data/2.5/weather?appid={weather_key}&q={CITY}&lang=pl'
    result = requests.get(url).json()
    kelvin = result['main']['temp']
    celc = kelvin_to_celcius(kelvin)
    st.write(f'Temp aktualnie: {celc:.2f}°C')
    st.write(f'Opis: {result["weather"][0]["description"]}')
    st.write(f'Prędkość wiatru {result["wind"]["speed"]}m/s')
    return celc, result

def get_pokemon():
    total_count = 151

    random_id = random.randint(1, total_count)
    pokemon = pb.pokemon(random_id)
    st.write(f"ID: {pokemon.id}")
    st.write(f"Nazwa: {pokemon.name.capitalize()}")
    st.write(f"Wzrost: {pokemon.height}")

    types = [t.type.name for t in pokemon.types]
    st.write("Type:", ", ".join(types))
    return {"id": pokemon.id, "name": pokemon.name.capitalize()}

# def check_currency():
#     client = freecurrencyapi.Client(currency_key)
#     final_currency = client.latest('USD', currencies=['PLN'])
#     return final_currency['data']['PLN']

def weather_to_pokemon(celc, poke):
    if celc < 10:
        return (f"Pokemon typu zimowego{poke['name']}")
    elif celc < 16:
        return (f"Pokemon typu normalnego{poke['name']}")
    elif celc < 22:
        return (f"Pokemon typu trawiasty{poke['name']}")
    else:
        return (f"Pokemon typu ognistego{poke['name']}")


def send_email(rate, pokemon):
    port = 465 # For SSL
    smtp_server = "smtp.gmail.com"
    message = f"""\
Subject: Kurs USD/PLN

Aktualna wartosc: {rate:.2f}
Pokemon na dzisiaj:
ID:{pokemon['id']}. {pokemon['name']}
"""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender, pw)
        server.sendmail(sender, receiver, message)

if st.button('refresh'):
    with st.spinner('Getting data...'):
        # rate = check_currency()
        # st.write(f"USD/PLN: {rate:.2f}")
        p = get_pokemon()
        # send_email(rate, p)
        celc, pogoda = get_weather()
        st.spinner("checking the weather...")
        st.write(f'In {CITY}temp today is: {celc:.2f}°C')
        st.write(weather_to_pokemon(celc, p))
# while True:

#     rate = check_currency()
#     pokemon = get_pokemon()
#     # send_email(rate, pokemon)
#     time.sleep(60)`