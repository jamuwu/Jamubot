from datetime import datetime, timedelta

def calculate_acc(score):
    total_unscale_score = (float(score['count300']) + float(score['count100']) + float(score['count50']) + float(score['countmiss'])) * 300
    user_score = float(score['count300']) * 300.0 + float(score['count100']) * 100.0 + float(score['count50']) * 50.0
    return (float(user_score)/float(total_unscale_score)) * 100.0

def no_choke_acc(score):
    total_unscale_score = (float(score['count300']) + float(score['count100']) + float(score['count50']) + float(score['countmiss'])) * 300
    user_score = (float(score['count300']) + float(score['countmiss'])) * 300.0 + float(score['count100']) * 100.0 + float(score['count50']) * 50.0
    return (float(user_score)/float(total_unscale_score)) * 100.0

async def time_ago(time1, time2):
    time_diff = time1 - time2
    timeago = datetime(1,1,1) + time_diff
    time_ago = ""
    if timeago.year-1 != 0:
        time_ago += "**{}** *Year{}* ".format(timeago.year-1, 's' if timeago.year-1 != 1 else '')
    if timeago.month-1 !=0:
        time_ago += "**{}** *Month{}* ".format(timeago.month-1, 's' if timeago.month-1 != 1 else '')
    if timeago.day-1 !=0:
        time_ago += "**{}** *Day{}* ".format(timeago.day-1, 's' if timeago.day-1 != 1 else '')
    if timeago.hour != 0:
        time_ago += "**{}** *Hour{}* ".format(timeago.hour, 's' if timeago.hour != 1 else '')
    if timeago.minute != 0:
        time_ago += "**{}** *Minute{}* ".format(timeago.minute, 's' if timeago.minute != 1 else '')
    time_ago += "**{}** *Second{}* ".format(timeago.second, 's' if timeago.second != 1 else '')
    return time_ago