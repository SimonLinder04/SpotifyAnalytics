import requests
from pprint import pprint

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





def print_data(data, depth=0, max_depth=2):
    indentation = "    " * depth

    if isinstance(data, dict):
        for key, value in data.items():
            print(indentation + str(key))

            if isinstance(value, (dict, list)):
                if depth < max_depth - 1:
                    print_data(value, depth + 1, max_depth)
            else:
                if depth < max_depth - 1:
                    print("    " * (depth + 1) + str(value))

    elif isinstance(data, list):
        for item in data:
            if depth < max_depth:
                print_data(item, depth, max_depth)

    else:
        print(indentation + str(data))


print(f"{"-" * 100}\n" *10)

pokemon_info = get_pokemon_info(pokemon_name)
print_data(pokemon_info)