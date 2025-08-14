import os
import requests
from dotenv import load_dotenv

load_dotenv()
riotApKey = os.getenv("RIOT_API_KEY")
discordToken = os.getenv("DISCORD_TOKEN")
discordChannel = int(os.getenv("DISCORD_CHANNEL"))
requestLimit = int(os.getenv("REQUESTS"))
dailyPostTimer = int(os.getenv("DAILY"))

jsonFile = "data.json"

platforms = ["BR1", "EUN1", "EUW1", "JP1", "KR", "LA1", "LA2", "NA1", "OC1", "TR1", "RU", "PH2", "SG2", "TH2", "TW2", "VN2"]
regions = ["AMERICAS", "EUROPE", "ASIA", "SEA"]
version = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()[0]

statisticsForMvp = {
    "killParticipation": 1,
    "kda": 1.2,
    "totalDamageDealtToChampions": 1,
    "damageDealtToBuildings": 0.7,
    "totalDamageTaken": 0.7,
    "goldPerMinute": 1,
    "visionScore": 1
}






    def calculateScore(tier, rank, leaguepoints):
        tierPoints = (Rank.tierOrder[tier] - 1) * 400
        rankPoints = (Rank.rankOrder[rank] - 1) * 100

        if tier == "MASTER":
            tierPoints -= 300
        if tier == "GRANDMASTER":
            tierPoints -= 700
        if tier == "CHALLENGER":
            tierPoints -= 1100

        totalPoints = tierPoints + rankPoints + leaguepoints
        return totalPoints



