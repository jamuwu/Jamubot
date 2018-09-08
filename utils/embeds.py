from discord import Embed
from time import time


def ppplus_embed(user):
    info = f'▸ **Rank:** #{user["Rank"]}\n    ▸ {user["CountryCode"]}#{user["CountryRank"]}\n'
    info += f'▸ **Performance:** {round(user["PerformanceTotal"], 2)}\n'
    info += f'▸ **Aim (Total):** {round(user["AimTotal"],2)}\n'
    info += f'▸ **Aim (Jump):** {round(user["JumpAimTotal"],2)}\n'
    info += f'▸ **Aim (Flow):** {round(user["FlowAimTotal"],2)}\n'
    info += f'▸ **Precision:** {round(user["PrecisionTotal"],2)}\n'
    info += f'▸ **Speed:** {round(user["SpeedTotal"],2)}\n'
    info += f'▸ **Stamina:** {round(user["StaminaTotal"],2)}\n'
    info += f'▸ **Accuracy:** {round(user["AccuracyTotal"],2)}\n'
    em = Embed(
        title=
        f'PerformancePlus Stats for {user["UserName"]} :flag_{user["CountryCode"].lower()}:',
        description=info,
        url=f'https://syrin.me/pp+/u/{user["UserID"]}',
        color=0x00ffc0)
    em.set_thumbnail(url=f'https://a.ppy.sh/{user["UserID"]}?random={time()}')
    return em


def user_embed(user, pppuser):
    info = f'▸ **Rank:** #{user["pp_rank"]} ({user["country"]}#{user["pp_country_rank"]})\n'
    info += f'  ▸ **PPv2:** {round(float(user["pp_raw"]), 2)}  '
    if pppuser:
        info += f'▸ **PP+:** {round(pppuser["PerformanceTotal"], 2)}\n'
    else:
        info += '\n'
    info += f'▸ **Accuracy:** {round(float(user["accuracy"]), 3)}%\n'
    info += f'▸ **Playcount:** {user["playcount"]}\n'
    totalhits = int(user['count300']) + int(user['count100']) + int(
        user['count50'])
    info += f'▸ **Hits per Play:** {int(totalhits / int(user["playcount"]))}'
    em = Embed(
        title=f'Standard Profile for {user["username"]}',
        description=info,
        url=f'https://osu.ppy.sh/users/{user["user_id"]}',
        color=0x00ffc0)
    em.set_thumbnail(url=f'https://a.ppy.sh/{user["user_id"]}?random={time()}')
    return em