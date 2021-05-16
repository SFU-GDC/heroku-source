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
    async def gamejam(self, ctx, option=""):
        jam_list = scrape_itch_io_jams()
        
        if option.lower() == "daily":
            print("TODO: implement this")
            return
        
        num_jams = 16 if option.lower() == "more" else 8

        most_popular = jam_list[:num_jams]
        most_popular[0]["most_members"] = True
        most_popular.sort(key=lambda n: n["start"])
        if jam_list != None:
            await ctx.send("Here's the {} Game Jams with the most members:".format(num_jams))
            master_string = ""
            for jam in most_popular:
                master_string += jam_to_str(jam) + "\n"
            await ctx.send("{}".format(master_string))

            #timeline = discord.File(f)
            #await ctx.send("Here's a timeline of all the game jams on itch.io:")
            #await ctx.send(file=timeline)
            await ctx.send("To recieve notifications for a specifc jam, run `,join jam_name` (not yet implemented)")
        else:
            await ctx.send("Huh, something went wrong. It should work if you try again right away, but if not please let someone know. ^-^")
    
    @commands.command()
    async def join(self, ctx, option=""):
        await ctx.send("Sorry, I haven't learned this command quite yet")


#NOTES:
# - enable people to subscribe to certain itch.io jams -> two reminders: 7 days before, and 1 day.
# - show a graphic of how long until the most popular jams.
# - list off a few new jams w/ > 20 people.

# --------------------------------------------------------------------------- #

def jam_to_str(jam):
    extra = "⭐" if "most_members" in jam else ""
    timediff = jam["start"] - datetime.now()
    return "|**{}**: {}\n|\tin *{}*, for *{}*, *{}* members\n|\t@ <https://itch.io{}>".format(
        jam["title"], extra, jam["joined"], pretty_date(timediff), jam["length"], jam["link"])

# TODO: this
def pretty_date(td): # td is timedelta
    if td.days >= 2:
        return "{} days".format(td.days)
    else:
        return "{} hours".format(td.days * 24 + td.seconds / (60 * 60))


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
            obj["link"] = link
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