from pymongo import MongoClient

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

from typing import List, NamedTuple

uri = "mongodb+srv://jordanjlee2023:PAxMi446Hi9mO9wm@jjlee.48gigog.mongodb.net/?appName=JJLee"
client = MongoClient(uri)
db = client.pokedex
pokemon_collection = db.pokemon_new

scraped_pokemon_data = []

class Pokemon(NamedTuple):
    id: int
    name: str
    avatar: str
    details_path: str
    types: List[str]
    total: int
    hp: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    entry: str


url = 'https://pokemondb.net/pokedex/all'
request = Request(
    url,
    headers = {'User-Agent': 'Mozilla/5.0'}
)
page = urlopen(request)
page_content_bytes = page.read()
page_html = page_content_bytes.decode("utf-8")

soup = BeautifulSoup(page_html, "html.parser")

pokemon_rows = soup.find_all("table", id="pokedex")[0].find_all("tbody")[0].find_all("tr")
scraped_count = 0

for pokemon in pokemon_rows:
    pokemon_data = pokemon.find_all("td")
    id = pokemon_data[0]['data-sort-value']
    avatar = pokemon_data[0].find_all("img")[0]['src']
    
    name = pokemon_data[1].find_all("a")[0].getText()
    if pokemon_data[1].find_all("small"):
        if name not in pokemon_data[1].find_all("small")[0].getText():
            name = name + " " + pokemon_data[1].find_all("small")[0].getText()
        else:
            name = pokemon_data[1].find_all("small")[0].getText()
    details_uri = pokemon_data[1].find_all("a")[0]["href"]
    
    types = []
    for pokemon_type in pokemon_data[2].find_all("a"):
        types.append(pokemon_type.getText())

    total = pokemon_data[3].getText()
    hp = pokemon_data[4].getText()
    attack = pokemon_data[5].getText()
    defense = pokemon_data[6].getText()
    sp_attack = pokemon_data[7].getText()
    sp_defense = pokemon_data[8].getText()
    speed = pokemon_data[9].getText()

    entry_url = f'https://pokemondb.net{details_uri}'
    request = Request(
        entry_url,
        headers = {'User-Agent': 'Mozilla/5.0'}
    )
    entry_page_html = urlopen(request).read().decode("utf-8")
    entry_soup = BeautifulSoup(entry_page_html, "html.parser")

    try:
        entry_text = entry_soup.find_all("main")[0].find_all("div", {"class": "resp-scroll"})[2].find_all("tr")[0].find_all("td")[0].getText()
    except:
        #print(f"Could not find pokemon entry text of {name}")
        entry_text = ""
    
    typed_pokemon = Pokemon(
        id = int(id),
        name = name,
        avatar = avatar,
        details_path = details_uri,
        types = types,
        total = int(total),
        hp = int(hp),
        attack = int(attack),
        defense = int(defense),
        sp_attack = int(sp_attack),
        sp_defense = int(sp_defense),
        speed = int(speed),
        entry = entry_text,
    )

    scraped_pokemon_data.append(typed_pokemon)


    pokemon_collection.insert_one(
        {
            "id": typed_pokemon.id,
            "name": typed_pokemon.name,
            "avatar": typed_pokemon.avatar,
            "details_path": typed_pokemon.details_path,
            "types": typed_pokemon.types,
            "total": typed_pokemon.total,
            "hp": typed_pokemon.hp,
            "attack": typed_pokemon.attack,
            "defense": typed_pokemon.defense,
            "sp_attack": typed_pokemon.sp_attack,
            "sp_defense": typed_pokemon.sp_defense,
            "speed": typed_pokemon.speed,
            "entry": typed_pokemon.entry,
        }
    )
    scraped_count += 1
    print(f'{name}, scraped_count: {scraped_count}')

print("--------done--------")
print(len(scraped_pokemon_data))