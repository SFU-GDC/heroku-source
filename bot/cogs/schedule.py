from datetime import datetime

import requests
from bs4 import BeautifulSoup

import discord
from discord.ext import commands, tasks

# For the game jam schedules

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["gamejams"])
    async def gamejam(self, ctx):
        jam_list = scrape_itch_io_jams()
        
        most_popular = jam_list[:8]
        most_popular.sort(key=lambda n: n["start"])

        if jam_list != None:
            await ctx.send("8 game jams with the most members in order of date:")
            for jam in most_popular:
                await ctx.send(jam_to_str(jam))

            #timeline = discord.File(f)
            #await ctx.send("Here's a timeline of all the game jams on itch.io:")
            #await ctx.send(file=timeline)
            await ctx.send("To recieve notifications for a specifc jam, run `,join jam_name`")
        else:
            await ctx.send("Huh, something went wrong. It should work if you try again right away, but if not please let someone know. ^-^")
    

#NOTES:
# - enable people to subscribe to certain itch.io jams -> two reminders: 7 days before, and 1 day.
# - show a graphic of how long until the most popular jams.
# - list off a few new jams w/ > 20 people.

# --------------------------------------------------------------------------- #

def jam_to_str(jam):
    timediff = jam["start"] - datetime.now()
    return "{}: {} members, starts in {} for {} @ <https://itch.io{}>".format(jam["title"], jam["joined"], timediff, jam["length"], jam["link"])

# TODO?
def pretty_date(timedelta):
    years = "{} years".format() if timedelta.years != 0 else ""
    months = "{} months".format() if timedelta.months != 0 else ""
    days = "{} days".format() if timedelta.days != 0 else ""
    return "{}{}{}{}".format()

def str_to_datetime(str):
    return datetime(int(str[:4]), int(str[5:7]), int(str[8:10]), int(str[11:13]), int(str[14:16]), int(str[17:19]))

def scrape_itch_io_jams():
    # make an html request & parse the document
    url = "https://itch.io/jams/upcoming"
    request = requests.get(url)
    if request.status_code != 200:
        return None
    soup = BeautifulSoup(request.text, 'html.parser')
    
    jam_widget_list = soup.find_all("div", class_="jam_grid_widget")
    if len(jam_widget_list) == 0:
        return None
    jam_widget_list = jam_widget_list[0]

    jam_list = []
    for widget in jam_widget_list.children:
        #print(widget)
        obj = {}

        top_row = widget.div.div
        host_row = top_row.next_sibling
        timestamp_row = host_row.next_sibling
        stats_row = timestamp_row.next_sibling
        is_ranked_row = stats_row.next_sibling

        # game jam may not have image
        if len(list(top_row.children)) == 2:
            img = top_row.div.get("data-background_image") 
            link = top_row.div.a.get("href")
            title = top_row.div.next_sibling.h3.a.get_text()
            obj["img"] = img
            obj["link"] = link
            obj["title"] = title
        else:
            link = top_row.div.h3.a.get("href")
            title = top_row.div.h3.a.get_text()
            obj["link"] = title
            obj["title"] = title

        host = host_row.a.get_text()
        start = timestamp_row.strong.span.get_text()
        length = timestamp_row.strong.next_sibling.next_sibling.get_text()
        joined = stats_row.div.span.get_text()
        ranked = is_ranked_row != None
        obj["host"] = host
        obj["start"] = str_to_datetime(start)
        obj["length"] = length
        obj["joined"] = joined
        obj["ranked"] = ranked

        jam_list.append(obj)

    for jam in jam_list:
        print("{}\n".format(jam))

    return jam_list

def make_timeline():
    pass

# --------------------------------------------------------------------------- #

def setup(bot):
    bot.add_cog(Schedule(bot))