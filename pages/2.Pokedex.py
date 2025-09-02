import streamlit as st
from mainapp import sqlite_connect, pd
st.write("Pokedex")

with st.expander("Pokémony w bazie"):
    con = sqlite_connect()
    c = con.cursor()
    try:
        rows = c.execute("SELECT id, name, type, lvl, total_exp, city, temp FROM pokemon ORDER BY id").fetchall()
        df = pd.DataFrame(rows, columns=["ID", "Nazwa", "Typ", 'lvl', 'total_exp', 'miasto gdzie złapano',
                                         'zarejestrowana temp'])
        st.dataframe(df, width='stretch')
        if st.button('delete db'):
            con = sqlite_connect()
            c = con.cursor()
            c.execute("DROP TABLE IF EXISTS pokemon")
            con.commit()
            st.success("Tabela 'pokemon' została usunięta.")
            st.rerun()
    except Exception:
        st.info("Brak zlapancyh pokemonow")