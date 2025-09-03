import streamlit as st
from mainapp import sqlite_connect, pd

with st.expander("Pokémony w bazie (info)"):
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

try:
    rows = c.execute("SELECT id, name, type, image_url, lvl, total_exp  FROM pokemon ORDER BY id").fetchall()
    for id, name, typ, image_url, lvl, total_exp in rows:
        cols = st.columns([1, 3])
        with cols[0]:
            if image_url:
                st.image(image_url, width=80)
        with cols[1]:
            st.write(f"**{id} – {name}**")
            st.caption(f"Typ: {typ}, lvl: {lvl}, exp: {total_exp}")
except Exception:
    st.info("Brak zlapancyh pokemonow")
