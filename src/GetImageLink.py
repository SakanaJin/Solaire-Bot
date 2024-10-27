from bs4 import BeautifulSoup
import requests
import random
import time


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def get_meme() -> str: 
    response = requests.get('https://meme-api.com/gimme')
    imgurl = response.json()['url']
    return imgurl

def get_berserk() -> str:
    response = requests.get('https://meme-api.com/gimme/berserk')
    imgurl = response.json()['url']
    return imgurl

def waifu_snake(category) -> str:
    type ='sfw'
    response = requests.get("https://api.waifu.pics/" + type + '/' + category)
    imgurl =response.json()['url']
    return imgurl

