import requests

base_url = "https://pokeapi.co/api/v2/"
pokemon_name = "pikachu"

def get_pokemon_info(name):
    url = f"{base_url}/pokemon/{pokemon_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        pokemon_data = response.json()
        return pokemon_data
    else:
        print(f"Failed to retrieved datad | Error code: {response.status_code}")






print(get_pokemon_info(pokemon_name)["height"])