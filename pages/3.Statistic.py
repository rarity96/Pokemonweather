from mainapp import st, sqlite_connect
import  pandas as pd
import altair as alt
st.write("Do przegladania statystyk, wyświetlania wykresów i danych.")

con = sqlite_connect()
c = con.cursor()
with st.expander("Zapisani użytkownicy: "):
    try:
        rows = c.execute(
            "SELECT id, name, last_login, poke_num "
            "FROM user "
            "ORDER BY id",
        ).fetchall()
        df = pd.DataFrame(rows, columns=["ID", "username", 'last_login', 'poke_num'])
        st.dataframe(df, width='stretch')
    except Exception:
        st.info("Brak użytkowników")


def leader_chart():
    c.execute("SELECT name AS username, poke_num AS pokemons FROM user ORDER BY pokemons DESC")
    rows = c.fetchall()
    c.close()
    return pd.DataFrame(rows, columns=['username', 'pokemons'])

st.write("Who caught the most pokemons?")

df = leader_chart()
st.subheader("Chart")

chart = (alt.Chart(df).mark_bar().encode(
    x = alt.X("pokemons:Q", title = "Złapane pokemony", axis=alt.Axis(tickMinStep=1)),
    color=alt.Color("username:N", legend=None),
    y = alt.Y("username:N",sort="-x", title = "Użytkownik"),
    tooltip=['username', 'pokemons']
).properties(height=250))


st.altair_chart(chart, use_container_width=True)