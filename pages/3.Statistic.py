from mainapp import st, sqlite_connect
import  pandas as pd
import altair as alt
st.write("To check statistics.")

con = sqlite_connect()
c = con.cursor()
with st.expander("Users: "):
    try:
        rows = c.execute(
            "SELECT id, name, last_login, poke_num "
            "FROM user "
            "ORDER BY id",
        ).fetchall()
        df = pd.DataFrame(rows, columns=["ID", "username", 'last_login', 'poke_num'])
        st.dataframe(df, width='stretch')
    except Exception:
        st.info("There is no users. Be the first one!")


def leader_chart():
    c.execute("SELECT name AS username, poke_num AS pokemons FROM user ORDER BY pokemons DESC")
    rows = c.fetchall()
    c.close()
    return pd.DataFrame(rows, columns=['username', 'pokemons'])

st.write("Who caught the most pokemons?")
df = leader_chart()
st.subheader("Top pokemon trainers")
top = st.radio("",["Top 3", "Top 5", "All"])

if top == "Top 3":
    df_top3 = df.nlargest(3, "pokemons")
    chart = (alt.Chart(df_top3).mark_bar().encode(
        x = alt.X("pokemons:Q", title = "Catched pokemons", axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("username:N", legend=None),
        y = alt.Y("username:N",sort="-x", title = "Users"),
        tooltip=['username', 'pokemons']
    ).properties(height=250))
elif top == "Top 5":
    df_top5 = df.nlargest(5, "pokemons")
    chart = (alt.Chart(df_top5).mark_bar().encode(
        x=alt.X("pokemons:Q", title="Catched pokemons", axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("username:N", legend=None),
        y=alt.Y("username:N", sort="-x", title="Users"),
        tooltip=['username', 'pokemons']
    ).properties(height=250))
else:
    chart = (alt.Chart(df).mark_bar().encode(
        x=alt.X("pokemons:Q", title="Catched pokemons", axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("username:N", legend=None),
        y=alt.Y("username:N", sort="-x", title="Users"),
        tooltip=['username', 'pokemons']
    ).properties(height=250))

st.altair_chart(chart, use_container_width=True)