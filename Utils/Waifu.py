import requests
import random
from enum import Enum

WAIFUAPIURL = "https://api.waifu.im/images"

SFWWEIGHT = 0.95
ECCHIWEIGHT = 0.025
HENTAIWEIGHT = 0.025

WAIFUWEIGHT = 0.95
NEKOWEIGHT = 0.05

class WaifuType(str, Enum):
    SFW = "sfw"
    ECCHI = 'ecchi'
    HENTAI = "hentai"

# class WaifuCat(str, Enum):
#     WAIFU = "waifu"
#     NEKO = "neko"

def get_random_waifu_url() -> str:
    wtype = random.choices(
        list(WaifuType),
        weights=[SFWWEIGHT, ECCHIWEIGHT, HENTAIWEIGHT],
        k=1
    )[0].value
    # category = random.choices(
    #     list(WaifuCat),
    #     weights=[WAIFUWEIGHT, NEKOWEIGHT],
    #     k=1
    # )[0].value
    category = "waifu"
    response = requests.get(WAIFUAPIURL + f"?IsNsfw={wtype != WaifuType.SFW}{f'&IncludedTags={wtype}' if wtype == WaifuType.ECCHI or wtype == WaifuType.HENTAI else ""}")
    imgurl = response.json()["items"][0]['url']
    return imgurl