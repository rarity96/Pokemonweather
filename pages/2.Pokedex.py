from mainapp import st
import pandas as pd
from mainapp import sqlite_connect
from streamlit import session_state, text_input, form_submit_button, rerun

if st.session_state.get("is_auth"):
    st.success(f"You are logged in as {st.session_state.get('username')}")
else:
    st.warning("You are not logged in. Please login on main page")

con = sqlite_connect()
c = con.cursor()
user_id = None
if st.session_state.get("is_auth") and st.session_state.get("username"):
     row = c.execute("SELECT id FROM user WHERE name = ?", (st.session_state.username,)).fetchone()
     if row:
         user_id = row[0]
username = st.session_state.username
with st.expander("Pokeomns in database (more_info)"):
    try:
        rows = c.execute(
            "SELECT id, name, type, lvl, total_exp, city, temp "
            "FROM pokemon "
            "WHERE user_id = ? "
            "ORDER BY id",
            (user_id,)
        ).fetchall()
        df = pd.DataFrame(rows, columns=["ID", "Name", "Type", 'lvl', 'total_exp', 'City',
                                         'Temp'])
        st.dataframe(df, width='stretch')
        if st.button('delete db'):
            con = sqlite_connect()
            c = con.cursor()
            c.execute("DROP TABLE IF EXISTS pokemon")
            con.commit()
            st.success("'Pokeomn' table, has been deleted.")
            st.rerun()
    except Exception:
        st.info("There is no pokemons in database")

try:
    rows = c.execute(
        "SELECT id, name, type, image_url, lvl, total_exp "
        "FROM pokemon "
        "WHERE user_id = ? "
        "ORDER BY id",
        (user_id,)
    ).fetchall()
    for id, name, typ, image_url, lvl, total_exp in rows:
        cols = st.columns([1, 3])
        with cols[0]:
            if image_url:
                st.markdown(f"""
                <div style="
                        background:#add8e6; 
                        padding:8px; 
                        border-radius:12px; 
                        display:inline-block; 
                        border: 4px solid #b0acac;
                    ">
                        <img src="{image_url}" width="80" />
                    </div>
                """,
                            unsafe_allow_html=True)

        with cols[1]:
            st.write(f"**{id} – {name}**")
            st.caption(f"Typ: {typ}, lvl: {lvl}, exp: {total_exp}")
except Exception:
    st.info("There is no pokemons in database")
