import streamlit as st
from mainapp import send_email

st.write("Jeśli masz jakiś pomysł, lub znalazłeś bład możesz to zgłosić tutaj")
mail_content = st.text_area("Treść wiadomości")
mail_back = st.text_input("Twój mail", key="input_emailpage")
if st.button("Wyślij"):
    if not mail_content or not mail_content.strip():
        st.info("Nie można wysłać pustego maila")
    else:
        try:
            send_email(mail_content, mail_back)
            st.success("Wiadomość wysłana, dzięki za wszelki feedback! :)")
        except Exception as e:
            st.error(f"Nie udało się wysłać wiadomośći: {e}")