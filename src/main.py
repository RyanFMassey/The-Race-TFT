# import math
# from datetime import datetime, timedelta
# import disnake
# import pytz
# from disnake import ApplicationCommandInteraction
# from disnake.ext import commands, tasks

from models import Summoner, Rank, Match
from client import get_puid, get_summoner_info, get_recent_match_ids, get_match_data
from draw import generate_image
from json_util import open_json_file, write_json_file


# bot = commands.InteractionBot()

matches_json_file = "match_data.json"
data_json_file = "test_data.json"
# data_json_file = "data.json"


def request_latest_match_ids(puuids):
    print("Getting match ids for:")
    print(puuids)

    latest_match_ids = []
    for puuid in puuids:
        latest_match_ids = latest_match_ids + get_recent_match_ids(puuid)
    print("Got recent matches:")
    print(latest_match_ids)
    return latest_match_ids

def load_match_data_from_file():
    saved_matches = [Match.from_dict(m) for m in open_json_file(matches_json_file)]
    if saved_matches is None:
        saved_matches = []
    return saved_matches


def request_latest_match_data(new_match_ids):
    match_data = []
    for match_id in new_match_ids:
        match_data.append(get_match_data(match_id))

    return match_data


def load_match_data(puuids):
    saved_matches = [Match.from_dict(m) for m in open_json_file(matches_json_file)]
    if saved_matches is None:
        saved_matches = []
    latest_matches_ids = []

    for puuid in puuids:
        latest_matches_ids = latest_matches_ids + get_recent_match_ids(puuid)

    latest_matches_ids_set = set(latest_matches_ids)

    saved_match_ids = {match.match_id for match in saved_matches}

    match_ids_to_delete = list(saved_match_ids - latest_matches_ids_set)
    match_ids_to_retrieve = list(latest_matches_ids_set - saved_match_ids)

    print(match_ids_to_delete)
    print(match_ids_to_retrieve)

    latest_matches = [match for match in saved_matches if match.match_id not in match_ids_to_delete]

    if match_ids_to_delete or match_ids_to_retrieve:
        new_matches = get_match_data(match_ids_to_retrieve)
        latest_matches = latest_matches + new_matches
        write_json_file(matches_json_file, [m.to_dict() for m in latest_matches])

    return latest_matches


def add_summoner(summoner_name):
    summoners = [Summoner.from_dict(s) for s in open_json_file(data_json_file)]
    name = summoner_name.split("#")[0]
    tag = summoner_name.split("#")[1]

    if any(s.name + "#" + s.tagline == summoner_name for s in summoners):
        return "Summoner already exists."
    else:
        puuid = get_puid(name, tag)
        summoner = get_summoner_info(puuid, summoner_name, tag)
        summoners.append(summoner)
        write_json_file(data_json_file, [s.to_dict() for s in summoners])
        return "Summoner added."


def remove_summoner(summoner_name):
    summoners = [Summoner.from_dict(s) for s in open_json_file(data_json_file)]
    name = summoner_name.split("#")[0]
    tag = summoner_name.split("#")[1]

    if any(s.name + "#" + s.tagline == summoner_name for s in summoners):
        for summoner in summoners:
            if summoner.name == name and summoner.tagline == tag:
                summoners.remove(summoner)
                break
        write_json_file(data_json_file, [s.to_dict() for s in summoners])
        return "Summoner deleted."

    else:
        return "Summoner already exists."


if __name__ == "__main__":


    print("Starting...")

    summoners = [Summoner.from_dict(s) for s in open_json_file(data_json_file)]
    if summoners is not None:

        latest_match_ids = request_latest_match_ids([s.puuid for s in summoners])
        stored_matches = load_match_data_from_file()
        stored_match_ids = [match.match_id for match in stored_matches]

        print("Stored match ids")
        print(stored_match_ids)
        print()
        print("Latest match ids")
        print(latest_match_ids)

        new_match_ids = set(latest_match_ids) - set(stored_match_ids)
        print("New match ids")
        print(new_match_ids)

        if not new_match_ids:
            print("No new matches")

        else:
            print("New matches, continuing")
            old_match_ids = set(stored_match_ids) - set(latest_match_ids)
            latest_matches = []
            relevant_saved_matches = [match for match in stored_matches if match.match_id not in old_match_ids]
            latest_matches = latest_matches + relevant_saved_matches
            new_matches = request_latest_match_data(new_match_ids)
            latest_matches = latest_matches + new_matches

            summoners.sort(key=lambda s: (Rank.tierOrder[s.tier], Rank.rankOrder[s.rank], s.lp, int(s.wins / (s.wins + s.losses) * 100)), reverse=True)

            # Set the 'position' attribute to their index in the list (1-based index)

            #TODO currently load_match_data requests each summoners recent matches, so does get_recent_match_ids in the summoners loop, should only need one request
            match_lookup = {m.match_id: m for m in latest_matches}

            for idx, summoner in enumerate(summoners, start=1):
                summoner.position = idx
                summoner.recent_match_ids = get_recent_match_ids(summoner.puuid)
                print(summoner.name, summoner.recent_match_ids)

                placements = []
                for match_id in summoner.recent_match_ids:
                    match_data = match_lookup.get(match_id)
                    if not match_data:
                        continue

                    player_data = next((p for p in match_data.players if p.puuid == summoner.puuid), None)
                    if not player_data:
                        continue

                    placements.append(player_data.placement)

                summoner.recent_placements = placements
                print(f"{summoner.name} recent placements: {summoner.recent_placements}")

            generate_image(summoners, summoners)

            write_json_file(data_json_file, [s.to_dict() for s in summoners])
            write_json_file(matches_json_file, [m.to_dict() for m in latest_matches])


    #
    #
    #
    # @bot.event
    # async def on_ready():
    #     print('Logged in as {0.user} at {1}'.format(bot, datetime.now().strftime('%I:%M:%S %p %d/%m/%Y')))
    #     print("")
    #     if not updateRaceImage.is_running():
    #         updateRaceImage.start()
    #
    #
    # @tasks.loop(seconds=60)
    # async def updateRaceImage():
    #     interval = math.floor(60 * numberOfSummoners(5) / (requestLimit * 0.7))
    #
    #     updateRaceImage.change_interval(seconds=interval)
    #
    #     json_data = openJsonFile(jsonFile)
    #     lastRunTime = json_data['runtime']
    #     # Set the timezone to Europe/London
    #     timezone = pytz.timezone('Europe/London')
    #     currentTime = datetime.now(tz=timezone)
    #     dateStr = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%y")
    #
    #     dailyTime = currentTime.replace(hour=dailyPostTimer, minute=0, second=0, microsecond=0).timestamp()
    #
    #     # If it's past 9pm and last run time is before 9pm today, update the image
    #     if currentTime.timestamp() > dailyTime > lastRunTime:
    #         json_data['runtime'] = dailyTime
    #         writeToJsonFile("data.json", json_data)
    #         if update(False, True):
    #             channel = bot.get_channel(discordChannel)
    #
    #             with open("Daily Rank list.png", 'rb') as f:
    #                 image = disnake.File(f)
    #
    #             await channel.send(f'Daily - {dateStr}', file=image)
    #     else:
    #         if update(False, False):
    #             channel = bot.get_channel(discordChannel)
    #
    #             with open("Rank list.png", 'rb') as f:
    #                 image = disnake.File(f)
    #
    #             await channel.send(file=image)
    #
    #
    # @bot.slash_command(description="Full list of summoners")
    # async def list(inter: ApplicationCommandInteraction):
    #     await inter.response.defer()
    #     jsonData = openJsonFile(jsonFile)
    #     summonerList = []
    #     for summoner in jsonData['summoners']:
    #         summonerList.append(summoner)
    #     await inter.send("\n".join(summonerList))

    #
    # @bot.slash_command(description="lp needed for challenger and grandmaster")
    # async def chall(inter: ApplicationCommandInteraction, platform: str = commands.Param(choices=platforms)):
    #     await inter.response.defer()
    #
    #     mastersUrl = f"https://{platform}.api.riotgames.com/tft/league/v1/masterleagues?queue=RANKED_TFT&api_key=RGAPI-f42c18f5-4234-48aa-b354-c977e092238d"
    #     grandMastersUrl = f"https://{platform}.api.riotgames.com/tft/league/v1/grandmasterleagues?queue=RANKED_TFT&api_key=RGAPI-f42c18f5-4234-48aa-b354-c977e092238d"
    #     challengerUrl = f"https://{platform}.api.riotgames.com/tft/league/v1/challengerleagues?queue=RANKED_TFT&api_key=RGAPI-f42c18f5-4234-48aa-b354-c977e092238d"
    #     combinedHighEloPlayers = []
    #     for url in [mastersUrl, grandMastersUrl, challengerUrl]:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             players = response.json().get("entries", [])
    #             combinedHighEloPlayers.extend(players)
    #         else:
    #             print(f"Failed to fetch data from {url}. Status code:", response.status_code)
    #
    #     sortedHighEloPlayers = sorted(combinedHighEloPlayers, key=lambda x: (-x["leaguePoints"], x["summonerName"]))
    #
    #     challenger_lp_needed = sortedHighEloPlayers[299]["leaguePoints"] + 1 if len(sortedHighEloPlayers) > 299 else None
    #     grandmaster_lp_needed = sortedHighEloPlayers[999]["leaguePoints"] + 1 if len(sortedHighEloPlayers) > 999 else None
    #
    #     await inter.send(f"{platform}\nLP needed for Challenger: {challenger_lp_needed}\nLP needed for Grandmaster: {grandmaster_lp_needed}")
    #
    #
    # @bot.slash_command(description="Patch notes")
    # async def patch(inter: ApplicationCommandInteraction):
    #     await inter.response.defer()
    #     update_available, updated_patch, days_ago, days_till_next, full_url, image_path = checkForNewPatchNotes("data.json", True)
    #     if update_available:
    #         # print("There is a new patch available. Patch version:", updated_patch, full_url, "Image saved at:", image_path)
    #         with open(image_path, 'rb') as f:
    #             image = disnake.File(f)
    #             await inter.send(f'Patch {updated_patch}\n'
    #                              f'{"tomorrow" if days_ago == -1 else "today" if days_ago == 0 else "yesterday" if days_ago == 1 else f"{days_ago} days ago"}\n'
    #                              f'{"" if days_ago < 1 or days_till_next == 13 or days_till_next == 0 else f"next patch in: {days_till_next} days"}\n'
    #                              f'{full_url}', file=image)
    #
    #
    # @bot.slash_command(description="breakdown of mvp score for a given game")
    # async def mvp(inter: ApplicationCommandInteraction, name: str, tagline: str, region: str = commands.Param(choices=regions), game: int = commands.Param(choices=[1, 2, 3, 4, 5])):
    #     await inter.response.defer()
    #     response = requests.get(
    #         f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tagline}?api_key={riotApKey}'
    #     )
    #     if response.status_code == 200:
    #         apiData1 = response.json()
    #         summonerPuuid = apiData1['puuid']
    #         summonerName = apiData1['gameName']
    #         summonerTagline = apiData1['tagLine']
    #         riotApiData = requests.get(f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summonerPuuid}/ids?queue=420&start=0&count=5&api_key={riotApKey}').json()
    #
    #         matchId = riotApiData[game - 1]
    #         mvpData(matchId)
    #
    #         with open("mvp data.txt", 'rb') as f:
    #             dataFile = disnake.File(f)
    #         await inter.send(f'Mvp scores for: {summonerName}#{summonerTagline}, game: {game}', file=dataFile)
    #     else:
    #         summonerFullName = f"{name}#{tagline}"
    #         await inter.send(f'Invalid summoner: {summonerFullName}')
    #
    #
    # @bot.slash_command(description="Mvp scores for all summoners")
    # async def crown(inter: ApplicationCommandInteraction):
    #     await inter.response.defer()
    #     crownData()
    #     with open("crown data.txt", 'rb') as f:
    #         dataFile = disnake.File(f)
    #     await inter.send(f'Mvp scores', file=dataFile)

    #
    # @bot.slash_command(description="Add summoner to the list")
    # async def add(inter: ApplicationCommandInteraction, name: str, tagline: str, platform: str = commands.Param(choices=platforms), region: str = commands.Param(choices=regions)):
    #     await inter.response.defer()
    #     jsonData = openJsonFile(jsonFile)
    #     if "#" in tagline:
    #         tagline = tagline.replace("#", "")
    #
    #     summonerFullName = f"{name}#{tagline}"
    #     summonerList = [summoner.lower() for summoner in jsonData['summoners']]
    #
    #     if summonerFullName.lower() in summonerList:
    #         await inter.send(f'{summonerFullName} is already added')
    #
    #     else:
    #         response = requests.get(
    #             f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tagline}?api_key={riotApKey}'
    #         )
    #         if response.status_code == 200:
    #             apiData1 = response.json()
    #             summonerFullName = apiData1['gameName'] + '#' + apiData1['tagLine']
    #             summonerPuuid = apiData1['puuid']
    #
    #             response = requests.get(
    #                 f'https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{summonerPuuid}?api_key={riotApKey}'
    #             )
    #             apiData2 = response.json()
    #
    #             data = jsonData
    #
    #             data["summoners"][summonerFullName] = {
    #                 "id": apiData2['id'],
    #                 "puuid": summonerPuuid,
    #                 "profileIconId": 123,
    #                 "platform": platform,
    #                 "region": region,
    #                 "score": 0,
    #                 "dailyScore": 0,
    #                 "leaderboardPosition": 100,
    #                 "dailyLeaderboardPosition": 100,
    #                 "gamesPlayed": 0,
    #                 "dailyGamesPlayed": 0
    #             }
    #
    #             writeToJsonFile("data.json", data)
    #             await inter.send(f'{summonerFullName} added')
    #         else:
    #             await inter.send(f'Invalid summoner: {summonerFullName}')
    #
    #
    # @bot.slash_command(description="Remove summoner from the list")
    # async def remove(inter: ApplicationCommandInteraction, name: str, tagline: str):
    #     await inter.response.defer()
    #     jsonData = openJsonFile(jsonFile)
    #     if "#" in tagline:
    #         tagline = tagline.replace("#", "")
    #
    #     summonerFullName = f"{name}#{tagline}"
    #     summonerList = [summoner.lower() for summoner in jsonData['summoners']]
    #
    #     if summonerFullName.lower() not in summonerList:
    #         await inter.send(f"{summonerFullName} has not been added")
    #     else:
    #         # Find the matching summoner in the original case
    #         originalCaseSummoner = next(
    #             summoner for summoner in jsonData['summoners']
    #             if summoner.lower() == summonerFullName.lower())
    #         del jsonData['summoners'][originalCaseSummoner]
    #         writeToJsonFile("data.json", jsonData)
    #         await inter.send(f"{originalCaseSummoner} removed")
    #
    #
    # bot.run(discordToken)
