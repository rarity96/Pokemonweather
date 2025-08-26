import smtplib, ssl, freecurrencyapi
import streamlit as st
import random, requests
import os, time
import pokebase as pb
from PIL import Image
from io import BytesIO
from streamlit import spinner
from dotenv import load_dotenv
load_dotenv()

weather_key = st.secrets['apis']["weather_key"]
sender = st.secrets['email']["sender"]
pw = st.secrets['email']['pw']
receiver = st.secrets['email']['receiver']
currency_key = st.secrets['apis']['currency_key']


def get_pokemon():
    total_count = 151

    random_id = random.randint(1, total_count)
    pokemon = pb.pokemon(random_id)
    st.write(f"ID: {pokemon.id}")
    st.write(f"Nazwa: {pokemon.name.capitalize()}")
    st.write(f"Wzrost: {pokemon.height}")

    types = [t.type.name for t in pokemon.types]
    st.write("Typy:", ", ".join(types))
    return {"id": pokemon.id, "name": pokemon.name.capitalize()}

def check_currency():
    client = freecurrencyapi.Client(currency_key)
    final_currency = client.latest('USD', currencies=['PLN'])
    return final_currency['data']['PLN']

st.write(check_currency())

# def send_email(rate, pokemon):
#     port = 465 # For SSL
#     smtp_server = "smtp.gmail.com"
#     message = f"""\
# Subject: Kurs USD/PLN
#
# Aktualna wartosc: {rate}
# Pokemon na dzisiaj:
# ID:{pokemon['id']}. {pokemon['name']}
# """
#     context = ssl.create_default_context()
#     with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
#         server.login(sender, pw)
#         server.sendmail(sender, receiver, message)




while True:
    rate = check_currency()
    pokemon = get_pokemon()
    # send_email(rate, pokemon)
    time.sleep(60)