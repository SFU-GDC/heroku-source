import io
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import numpy as np

import skimage
from skimage.io import imread, imsave
from skimage.transform import resize


import discord
from discord.ext import commands, tasks

# For the game jam schedules

url_by_members = "https://itch.io/jams/upcoming"
url_by_date = "https://itch.io/jams/upcoming/sort-date"

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["gamejams"])
    async def gamejam(self, ctx, option=""):    
        if option.lower() == "soon":
            # NOTE: this option assumes that all jams within the current week are contained in the first page.
            jam_list = scrape_itch_io_jams(url_by_date)

            if jam_list == None:
                await ctx.send("Huh, something went wrong. It should work if you try again right away, but if not please let someone know. ^-^")
                return

            now = datetime.now()
            days_until = lambda jam: (jam["start"] - now).days + (jam["start"] - now).seconds / (60 * 60 * 24)
            next_week = [jam for jam in jam_list if days_until(jam) <= 7]
            next_week.sort(key=lambda n: -int(n["joined"]))

            if len(next_week) == 0: 
                await ctx.send("Sorry, there are no game jams over the next week.")
                return

            limit = 4 #if titles == None else int(titles)
            num_jams = min(len(next_week), limit)
            next_week = next_week[:num_jams]
            next_week[0]["most_members"] = True

            await ctx.send("Here's the {} most popular Game Jams over the next week:".format(num_jams))
            images = []
            master_string = ""
            for jam in next_week:
                master_string += jam_to_str(jam) + "\n"
                if "img" in jam:
                    images.append(jam["img"])
                else:
                    images.append(None)

            await ctx.send("{}".format(master_string))

            fbuf = io.BytesIO()
            imsave(fbuf, make_quad_graphic(images))
            graphic = discord.File(fbuf)
            await ctx.send(file=graphic)

            await ctx.send("To recieve notifications for a specifc jam, run `,join jam_name` (not yet implemented)")
            return
        elif option.lower() == "next":
            print("TODO: implement this too")
            return
        else:
            jam_list = scrape_itch_io_jams(url_by_members)
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
    return "| **{}** {}\n| \tin {}, for {}, {} joined\n| \t@ <https://itch.io{}>".format(
        jam["title"], extra, pretty_date(timediff), jam["length"], jam["joined"], jam["link"])

def pretty_date(td): # td is timedelta
    if td.days >= 2:
        return "{} days".format(td.days)
    else:
        return "{} hours".format(int((td.days * 24 + td.seconds / (60 * 60)) * 10) / 10)

def str_to_datetime(str):
    return datetime(int(str[:4]), int(str[5:7]), int(str[8:10]), int(str[11:13]), int(str[14:16]), int(str[17:19]))

# NOTE: url must be valid!
def scrape_itch_io_jams(url):
    # make an html request & parse the document
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
        joined = 0 if stats_row.div == None else stats_row.div.span.get_text()
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

# src must be smaller than dest
def overlay_image(dest, src, x, y):
    height, width, channels = src.shape
    for y_ in range(0, height):
        for x_ in range(0, width):
            colour = src[y_][x_]
            a = 1 if len(colour) == 3 else colour[3]/256
            dest[y_+y][x_+x] = (colour[0] * a, colour[1] * a, colour[2] * a)

# there are between 1 and 4 images in $images
def make_quad_graphic(images):
    target_height = 2 * 111
    target_width = 2 * 140
    spacing = 4 # NOTE: assuming all images are smaller than this

    sk_images = []
    for i in range(4):
        img = images[i]
        sk_img = np.zeros([target_height, target_width, 3], dtype=np.uint8) if img == None else imread(img)
        sk_img = resize(sk_img, (target_height, target_width), anti_aliasing=True) * 256 
        sk_images.append(sk_img)

    big_height = 2*target_height + spacing * 3
    big_width = 2*target_width + spacing * 3
    sk_img_big = np.zeros([big_height, big_width, 3], dtype=np.uint8)

    overlay_image(sk_img_big, sk_images[0], spacing, spacing)
    overlay_image(sk_img_big, sk_images[1], 2 * spacing + target_width, spacing)
    overlay_image(sk_img_big, sk_images[2], spacing, 2 * spacing + target_height)
    overlay_image(sk_img_big, sk_images[3], 2 * spacing + target_width, 2 * spacing + target_height)

    return sk_img_big

# --------------------------------------------------------------------------- #
# Tests:

def test():
    jam_list = scrape_itch_io_jams(url_by_date)

    print("here")

    if jam_list == None:
        print("Huh, something went wrong. It should work if you try again right away, but if not please let someone know. ^-^")
        return

    now = datetime.now()
    days_until = lambda jam: (jam["start"] - now).days + (jam["start"] - now).seconds / (60 * 60 * 24)
    next_week = [jam for jam in jam_list if days_until(jam) <= 7]
    next_week.sort(key=lambda n: -int(n["joined"]))

    if len(next_week) == 0: 
        print("Sorry, there are no game jams over the next week.")
        return

    limit = 4
    num_jams = min(len(next_week), limit)
    next_week = next_week[:num_jams]
    next_week[0]["most_members"] = True

    print("Here's the {} most popular Game Jams over the next week:".format(num_jams))
    images = []
    master_string = ""
    for jam in next_week:
        master_string += jam_to_str(jam) + "\n"
        if "img" in jam:
            response = requests.get(jam["img"])
            img_bytes = io.BytesIO(response.content)
            images.append(img_bytes)
        else:
            images.append(None)


    print("{}".format(master_string))

    f = make_quad_graphic(images)

# --------------------------------------------------------------------------- #

def setup(bot):
    bot.add_cog(Schedule(bot))