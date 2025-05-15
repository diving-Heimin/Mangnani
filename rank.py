import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
from urllib.parse import quote

load_dotenv()

LOL_KEY = os.getenv('LOL_KEY')
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


def get_puuid(gameName, tagLine):
    headers = {
        "X-Riot-Token": LOL_KEY.strip(),
        "User-Agent": "Mozilla/5.0"
    }
    encoded_name = quote(gameName.strip())
    encoded_tag = quote(tagLine.strip())
    url = f"https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_name}/{encoded_tag}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json().get("puuid")
    else:
        print("PUUID 요청 실패:", res.status_code, res.text)
        return None

def get_summoner_by_puuid(puuid):
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": LOL_KEY.strip()}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
         data = res.json()
         sid = data.get("id")
         return sid
    else:
        print("소환사 요청 실패:", res.status_code, res.text)
        return None

def get_rank(summoner_id):
    url = f"https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": LOL_KEY.strip()}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        for queue in data:
            if queue.get("queueType") == "RANKED_SOLO_5x5":
                tier = queue.get("tier")
                return tier

    else:
        print("랭크 요청 실패:", res.status_code, res.text)
        return None

#선수 입장
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user.name}")

@bot.event
async def on_message(message):

    if message.content.startswith("!티어"):
        user = message.author
        guild = message.guild

        riot_id = message.author.display_name.strip()
        if "#" in riot_id:
            name, tag = riot_id.split("#")
        pid = get_puuid(name, tag)
        sid = get_summoner_by_puuid(pid)
        rank = get_rank(sid)
        await message.channel.send(rank)

        if rank == "IRON":
            rank = "아이언"
        elif rank == "BRONZE":
            rank = "브론즈"
        elif rank == "SILVER":
            rank = "실버"
        elif rank == "GOLD":
            rank = "골드"
        elif rank == "PLATINUM":
            rank = "플레티넘"
        elif rank == "EMERALD":
            rank = "에메랄드"
        elif rank == "DIAMOND":
            rank = "다이아몬드"
        elif rank == "MASTER":
            rank = "마스터"
        elif rank == "GRANDMASTER":
            rank = "그랜드 마스터"
        elif rank == "CHALLENGER":
            rank = "챌린저"

        tier_names = ["아이언", "브론즈", "실버", "골드", "플레티넘", "에메랄드", "다이아몬드", "마스터", "그랜드 마스터", "챌린저"]
        for role in user.roles:
            if role.name in tier_names:
                await user.remove_roles(role)
        role = discord.utils.get(guild.roles, name=rank)

        await user.add_roles(role)
        await message.channel.send(f"{user.mention}, {rank}")

bot.run(TOKEN)