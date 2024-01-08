import requests
from bs4 import BeautifulSoup
import time
from discord_webhook import DiscordWebhook, DiscordEmbed

url = "https://thunderstore.io/c/lethal-company/?ordering=last-updated"
webhook_url = "https://discord.com/api/webhooks/{channel_id}/{token}"


def find_new_dicts(old_list, new_list):
    """
    Find new dictionaries in new_list that are not present in old_list.

    Parameters:
    - old_list: List of dictionaries
    - new_list: List of dictionaries

    Returns:
    - List of dictionaries containing new entries in new_list
    """
    names = [i.get("name") for i in old_list]
    new_dicts = [new_dict for new_dict in new_list if new_dict.get("name") not in names]
    return new_dicts


def fetch_items():
    """
    Webscrapes the thunderstore website for updates

    Returns:
    - List of dictionaries containing all the mods
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    listitems = soup.find("div", class_="package-list")

    out = []
    for item in listitems.children:
        if item.find("h5") == -1:
            continue
        
        name = item.find("h5").text

        children = list(item.children)
        
        img = children[1].find("img")["src"]
        description = children[5].text.strip()
        tags = [i.text.strip() for i in children[7] if i.text.strip() != ""]

        likebar = children[3]
        downlaods = list(list(likebar.children)[1].children)[1].text.strip()
        likes = list(list(likebar.children)[1].children)[3].text.strip()

        author = list(likebar.children)[-2].find("a").text.strip()
        author_url = "https://thunderstore.io" + list(likebar.children)[-2].find("a")["href"]

        out.append({
            "name": name,
            "img": img,
            "description": description,
            "tags": tags,
            "likes": likes,
            "downlaods": downlaods,
            "author": author,
            "author_url": author_url
        })
    
    return out


items = fetch_items()
#items.remove(items[2])
while True:
    new_items = fetch_items()
    diff = find_new_dicts(items, new_items)
    items = new_items
    print("Diff:", [i.get("name") for i in diff])

    for mod in diff:
        # Create the embed and send it to the server
        webhook = DiscordWebhook(url=webhook_url)

        embed = DiscordEmbed(title=mod.get("name"), description=mod.get("description"), color="df3432")
        embed.set_thumbnail(url=mod.get("img"))

        embed.add_embed_field(name="Downloads", value="`"+mod.get("downlaods")+"`", inline=True)
        embed.add_embed_field(name="Likes", value="`"+mod.get("likes")+"`", inline=True)
        embed.add_embed_field(name="Tags", value="```"+", ".join(mod.get("tags"))+"```", inline=False)

        embed.set_author(name=mod.get("author"), url=mod.get("author_url"))
        embed.set_footer(text="Cosmic Collectors", icon_url="https://cdn.discordapp.com/icons/1178990094301007942/a_7bb927e6b20b7257069d540216be9a26.webp")
        embed.set_timestamp()

        webhook.add_embed(embed)
        resp = webhook.execute()

    # Check every five minutes
    for i in range(30):
        print(f"\r[{'.'*i}{' '*(29-i)}] ", end="", flush=True)
        time.sleep(10)
