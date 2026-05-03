# import math
# from datetime import datetime, timedelta
# import disnake
# import pytz
# from disnake import ApplicationCommandInteraction
# from disnake.ext import commands, tasks
import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands, tasks

from models import Summoner, Rank, Match
from client import get_puid, get_summoner_info, get_recent_match_ids, get_match_data
from draw import generate_image
from json_util import open_json_file, write_json_file


bot = commands.InteractionBot()

matches_json_file = "match_data.json"
# data_json_file = "test_data.json"
data_json_file = "data.json"
discord_token = "MTQwNjIwMzI3OTg4NDU1NDMzMA.Gx-L8m.TZkfkRXMD_umZudkE2-dl96MTECiaNUjRVxWcs"
CHANNEL_ID = 1399498567575670845
platforms = ["BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "LA2", "NA1", "OC1", "TR1", "RU", "PH2", "SG2", "TH2", "TW2", "VN2"]
regions = [" ", "EUROPE", "ASIA", "SEA"]


def request_latest_match_ids(puuids):
    latest_match_ids = []
    for puuid in puuids:
        latest_match_ids = latest_match_ids + get_recent_match_ids(puuid)

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

    latest_matches = [match for match in saved_matches if match.match_id not in match_ids_to_delete]

    if match_ids_to_delete or match_ids_to_retrieve:
        new_matches = get_match_data(match_ids_to_retrieve)
        latest_matches = latest_matches + new_matches
        write_json_file(matches_json_file, [m.to_dict() for m in latest_matches])

    return latest_matches


def add_summoner(name, tag):
    summoners = [Summoner.from_dict(s) for s in open_json_file(data_json_file)]

    if any((s.name == name and s.tagline == tag) for s in summoners):
        return "Summoner already exists."
    else:
        puuid = get_puid(name, tag)
        summoner = get_summoner_info(puuid, name, tag)
        summoners.append(summoner)
        write_json_file(data_json_file, [s.to_dict() for s in summoners])
        return "Summoner added."


def remove_summoner(name, tag):
    summoners = [Summoner.from_dict(s) for s in open_json_file(data_json_file)]

    if any((s.name == name and s.tagline == tag) for s in summoners):
        for summoner in summoners:
            if summoner.name == name and summoner.tagline == tag:
                summoners.remove(summoner)
                break
        write_json_file(data_json_file, [s.to_dict() for s in summoners])
        return "Summoner deleted."

    else:
        return "Summoner already exists."


def check_and_generate_leaderboard_image():
    print("Starting...")

    summoners = [Summoner.from_dict(s) for s in open_json_file(data_json_file)]
    if summoners is None:
        return False

    else:
        latest_match_ids = request_latest_match_ids([s.puuid for s in summoners])
        stored_matches = load_match_data_from_file()
        stored_match_ids = [match.match_id for match in stored_matches]

        new_match_ids = set(latest_match_ids) - set(stored_match_ids)

        if not new_match_ids:
            print("No new matches")
            return False

        else:
            print("New matches, continuing")
            old_match_ids = set(stored_match_ids) - set(latest_match_ids)
            latest_matches = []
            relevant_saved_matches = [match for match in stored_matches if match.match_id not in old_match_ids]
            latest_matches = latest_matches + relevant_saved_matches
            new_matches = request_latest_match_data(new_match_ids)
            latest_matches = latest_matches + new_matches

            latest_summoners = []
            for summoner in summoners:
                latest_summoner = get_summoner_info(summoner.puuid, summoner.name, summoner.tagline)
                latest_summoners.append(latest_summoner)

            latest_summoners.sort(key=lambda s: (
            Rank.tierOrder[s.tier], Rank.rankOrder[s.rank], s.lp, int(s.wins / (s.wins + s.losses) * 100)), reverse=True)

            # Set the 'position' attribute to their index in the list (1-based index)

            # TODO currently load_match_data requests each summoners recent matches, so does get_recent_match_ids in the summoners loop, should only need one request
            match_lookup = {m.match_id: m for m in latest_matches}

            for idx, summoner in enumerate(latest_summoners, start=1):
                summoner.position = idx
                summoner.recent_match_ids = get_recent_match_ids(summoner.puuid)

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

            generate_image(summoners, latest_summoners)

            write_json_file(data_json_file, [s.to_dict() for s in latest_summoners])
            write_json_file(matches_json_file, [m.to_dict() for m in latest_matches])
            return True


if __name__ == "__main__":

    @bot.event
    async def on_ready():
        print('Logged in as {0.user}'.format(bot))
        print("")
        if not update_race_image.is_running():
            update_race_image.start()


    @tasks.loop(seconds=60)
    async def update_race_image():
        should_send_image = check_and_generate_leaderboard_image()
        if should_send_image:
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                try:
                    with open("Rank list.png", 'rb') as f:
                        picture = disnake.File(f)
                        await channel.send(file=picture)
                        print("Image posted successfully.")
                except Exception as e:
                    print(f"Error posting image: {e}")


    @bot.slash_command(description="Add summoner to The Race - TFT")
    async def add(inter: ApplicationCommandInteraction, name: str, tagline: str):
        await inter.response.defer()

        message = add_summoner(name, tagline)
        await inter.send(f'{message}')


    @bot.slash_command(description="Remove a summoner from The Race - TFT")
    async def remove(inter: ApplicationCommandInteraction, name: str, tagline: str):
        await inter.response.defer()

        message = remove_summoner(name, tagline)
        await inter.send(f'{message}')


bot.run(discord_token)
