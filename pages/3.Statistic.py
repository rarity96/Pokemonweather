from mainapp import st, sqlite_connect
import  pandas as pd
import sqlite3
st.write("Do przegladania statystyk, wyświetlania wykresów i danych.")

@st.cache_resource
def sqlite_connect():
    con = sqlite3.connect('pokeweather.db', check_same_thread=False)
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    return con

con = sqlite_connect()
c = con.cursor()
with st.expander("Zapisani użytkownicy: "):
    try:
        rows = c.execute(
            "SELECT id, name "
            "FROM user "
            "ORDER BY id",
        ).fetchall()
        df = pd.DataFrame(rows, columns=["ID", "username"])
        st.dataframe(df, width='stretch')
    except Exception:
        st.info("Brak użytkowników")


