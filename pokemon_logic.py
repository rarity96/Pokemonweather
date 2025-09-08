import mainapp, sqlite3, random
from mainapp import st

LVL = {
    1: 3,
    2: 6,
    3: 10,
    4: 15,
    5: 21,
}


@st.cache_resource
def sqlite_connect():
    con = sqlite3.connect('pokeweather.db', check_same_thread=False)
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    return con

pb = mainapp.pb

@st.cache_data
def get_ids_by_type(type_name, max_id = 151) -> list[int]:

    typ = pb.type_(type_name)
    ids = []
    for i in typ.pokemon:
        url = i.pokemon.url
        pok_id = int(url.rstrip("/").split("/")[-1])
        if pok_id <= max_id:
            ids.append(pok_id)
    return ids


def get_random_pokemon_by_type(type_name: str, max_id: int = 151):
    ids = get_ids_by_type(type_name, max_id)
    if not ids:
        return None
    pid = random.choice(ids)
    return pb.pokemon(pid)

def get_pokemon(preferred_type):
    if preferred_type:
        pokemon = get_random_pokemon_by_type(preferred_type, 151)
        if pokemon is None:
            random_id = random.randint(1, 151)
            pokemon = pb.pokemon(random_id)
    else:
        random_id = random.randint(1,151)
        pokemon = pb.pokemon(random_id)
    types = [t.type.name for t in pokemon.types]
    return {"id": pokemon.id, "name": pokemon.name.capitalize(), "img_url": get_pokemon_image(pokemon.id, prefer='official'), "types": types}

def get_pokemon_image(pokemon_id, prefer="official") -> str| None:
    pokemon = pb.pokemon(pokemon_id)
    image = pokemon.sprites

    if prefer == "official":
        try:
            url = image.other['official-artwork']['front_default']
            if url:
                return url
        except Exception:
            pass
    url = getattr(image, 'front_default', None)
    if url:
        return url

    try:
        return image.other['home']['front_default']
    except Exception:
        return None


def calculate_exp(pokemon_id):
    con = sqlite_connect()
    c = con.cursor()
    check_exp = c.execute("SELECT total_exp FROM pokemon WHERE id = ?", (pokemon_id,)).fetchone()
    current_exp = 0 if (check_exp is None or check_exp[0] is None) else check_exp[0]
    for lvl, exp_needed in LVL.items():
        if current_exp < exp_needed:
            return lvl
    return max(LVL.keys())
#     if current_exp < 2:
#         return 1
#     elif current_exp < 4:
#         return 2
#     elif current_exp < 6:
#         return 3
#     else:
#         return 4
