import requests
import random
from enum import Enum

WAIFUAPIURL = "https://api.waifu.pics"

SFWWEIGHT = 0.95
NSFWWEIGHT = 0.05

WAIFUWEIGHT = 0.95
NEKOWEIGHT = 0.05

class WaifuType(str, Enum):
    SFW = "sfw"
    NSFW = "nsfw"

class WaifuCat(str, Enum):
    WAIFU = "waifu"
    NEKO = "neko"

def get_random_waifu_url() -> str:
    wtype = random.choices(
        list(WaifuType),
        weights=[SFWWEIGHT, NSFWWEIGHT],
        k=1
    )[0]
    category = random.choices(
        list(WaifuCat),
        weights=[WAIFUWEIGHT, NEKOWEIGHT],
        k=1
    )[0]
    response = requests.get(WAIFUAPIURL + f"/{wtype}/{category}")
    imgurl = response.json()['url']
    return imgurl