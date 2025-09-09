from mainapp import st, sqlite_connect
import  pandas as pd
st.write("Do przegladania statystyk, wyświetlania wykresów i danych.")

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


