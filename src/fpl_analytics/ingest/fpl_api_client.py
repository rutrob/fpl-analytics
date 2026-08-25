import requests

BASE_URL = "https://fantasy.premierleague.com/api"

def get_bootstrap_static() -> dict:
    response = requests.get(f"{BASE_URL}/bootstrap-static/")
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    data = get_bootstrap_static()
    print("Klucze w odpowiedzi:", data.keys())
    print("Liczba zawodnikow:", len(data["elements"]))
    print("Liczba druzyn:", len(data["teams"]))
    print("Przyklad zawodnika:", data["elements"][0])