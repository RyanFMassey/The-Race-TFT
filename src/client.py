import urllib.parse
import requests
from models import Summoner, Match, Player, Trait

api_key = "RGAPI-868dbd9e-853d-4828-b60b-b7c7c116a249"


def get_puid(summoner_name, tag):
    print("Getting puuid for " + summoner_name + "#" + tag)
    url_encoded_name = urllib.parse.quote(summoner_name)
    response = requests.get(
        f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{url_encoded_name}/{tag}',
        headers={'X-Riot-Token': f'{api_key}'})
    print('https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{url_encoded_name}/{tag}')
    return response.json()["puuid"]


def get_summoner_info(puuid, summoner_name, tag):
    response = requests.get(f'https://euw1.api.riotgames.com/tft/league/v1/by-puuid/{puuid}?api_key={api_key}').json()

    wins = response[0]["wins"]
    losses = response[0]["losses"]
    tier = response[0]["tier"]
    rank = response[0]["rank"]
    lp = response[0]["leaguePoints"]

    summoner = Summoner(puuid, summoner_name, tag, tier, rank, lp, wins, losses, 0, 0, 0)
    print(summoner.__dict__)

    return summoner


def get_recent_match_ids(puuid):
    print("Getting matches for " + puuid)
    data = []
    response = requests.get(f'https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?start=0&count=10&api_key={api_key}')
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Failed to retrieve match ids for {puuid}: {response.status_code}")

    return data


def get_match_data(match_ids):
    match_data = []
    for match_id in match_ids:
        match_data.append(get_match_info_by_id(match_id))

    return match_data


def get_match_info_by_id(match_id):
    response = requests.get(f'https://europe.api.riotgames.com/tft/match/v1/matches/{match_id}?api_key={api_key}').json()

    players = []

    players_data = response["info"]["participants"]
    for player_data in players_data:
        traits = []
        traits_data = player_data["traits"]
        for trait_data in traits_data:
            trait = Trait(trait_data["name"], trait_data["num_units"])
            traits.append(trait)

        player = Player(player_data["puuid"], player_data["level"], player_data["placement"], traits)
        players.append(player)

    match = Match(match_id, players)
    return match

