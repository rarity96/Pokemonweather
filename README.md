<h1>PokeWeather</h1>

<p>
A fun educational project that combines real-time weather data with Pokémon catching mechanics.<br>
Based on the weather in your chosen city, you’ll catch a Pokémon from oryginal 151 pokemons of the corresponding type.
You can check LIVE project here: <a href="https://pokemonweather.streamlit.app/">pokemonweather.streamlit.app</a>
</p>

<p>
Built with <b>Streamlit</b>, <b>PokéAPI</b>, <b>OpenWeather API</b>, and <b>SQLite3</b>.
</p>

<hr>

<h2>Features</h2>
<ul>
  <li>Weather integration with OpenWeather API (descriptions available in Polish).</li>
  <li>Random Pokémon catching:
    <ul>
      <li>Weather conditions → mapped to Pokémon types (e.g., rain → water, fog → ghost).</li>
      <li>Pokémon images fetched directly from PokéAPI.</li>
    </ul>
  </li>
  <li>EXP & Level system:
    <ul>
      <li>Pokémon gain EXP every time you encounter them again.</li>
      <li>Levels increase automatically when EXP thresholds are reached.</li>
    </ul>
  </li>
  <li>Pokédex view:
    <ul>
      <li>A full list of caught Pokémon with stats, levels, exp, location, and images.</li>
    </ul>
  </li>
  <li>Rate limiting:
    <ul>
      <li>Optional restriction to only allow catching once per hour. <i>(coming soon)</i></li>
    </ul>
  </li>
  <li>Contact form for submitting feedback and ideas.</li>
  <li>Custom UI:
    <ul>
      <li>Multiple subpages using Streamlit’s <code>pages/</code> directory.</li>
      <li>Styled list of Pokémon with images and stats.</li>
    </ul>
  </li>
</ul>

<hr>

<h2>Tech Stack</h2>
<ul>
  <li><b>Frontend & App:</b> Streamlit</li>
  <li><b>APIs:</b>
    <ul>
      <li><a href="https://pokeapi.co/">PokéAPI</a> (Pokémon data)</li>
      <li><a href="https://openweathermap.org/api">OpenWeather</a> (weather data)</li>
    </ul>
  </li>
  <li><b>Database:</b> SQLite3</li>
  <li><b>Other:</b> Pandas, hashlib (password hashing), Streamlit cache decorators (<code>st.cache_data</code>, <code>st.cache_resource</code>)</li>
</ul>

<hr>

<h2>Running Locally</h2>

<h3>1. Clone the repository</h3>
<pre>
git clone https://github.com/&lt;your-username&gt;/PokeWeather.git
cd PokeWeather
</pre>

<h3>2. Create a virtual environment</h3>
<pre>
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
</pre>

<h3>3. Install dependencies</h3>
<pre>
pip install -r requirements.txt
</pre>

<h3>4. Add secrets</h3>
<p>Create a file <code>.streamlit/secrets.toml</code> with the following content:</p>

<pre>
[apis]
weather_key = "YOUR_OPENWEATHER_KEY"
currency_key = "YOUR_FREECURRENCY_KEY"  # optional

[email]
sender = "example@gmail.com"
pw = "app_password"
receiver = "example@gmail.com"
</pre>

<h3>5. Run the app</h3>
<pre>
streamlit run mainapp.py
</pre>

<hr>

<h2>TODO</h2>
<ul>
  <li>Improve authentication & user sessions</li>
  <li>Enhance UI/UX (responsive layout, more styling)</li>
  <li>Add statistics and charts for caught Pokémon</li>
  <li>Improve API error handling and caching</li>
</ul>
