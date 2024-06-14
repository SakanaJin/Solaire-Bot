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

def waifu_snake(number) -> str:
    if number == 1:
        type ='nsfw'
    else:
        type ='sfw'
    catnum = random.randint(1,100)
    if catnum <= 20:
        category ='neko'
    else:
        category = 'waifu'
    response = requests.get("https://api.waifu.pics/" + type + '/' + category)
    imgurl =response.json()['url']
    return imgurl

def get_trauma() -> str: #make !traumatize
    source = requests.get("https://e621.net/posts?tags=hi_res+", headers = headers)
    soup = BeautifulSoup(source.text, 'html.parser')

    Images = soup.find_all('img')
    img_links=[]

    for image in Images:
        img_links.append(image['src'])

    image = img_links[5]

    #print(Images, "\n")
    #print(image, "\n")
    #print(img_links)
    return image

