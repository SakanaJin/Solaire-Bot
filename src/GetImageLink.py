from bs4 import BeautifulSoup
import requests
import random
import time

#https://img.ifunny.co/videos/e84b050e5ba0ff3f3f3b8bd0de4b3657d50ab9684f5709924621ce43156394e8_1.mp4
#https://img.ifunny.co/images/13a1064fbba4acaa9b355421937d85e51debe8c2d58e5bedb4ee739a19740437_1.jpg

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


def get_ifunny_image()-> str:
    source = requests.get("https://ifunny.co/top-memes/day", headers=headers).text
    soup = BeautifulSoup(source, "html.parser")
    #print(soup.prettify, "\n")

    #time.sleep(3)

    Images= soup.find_all('img')
    img_links=[]
    for image in Images:
        img_links.append(image['src'])
    

    image = img_links[random.randint(0, len(img_links) - 1)]
    #image = "https://img.ifunny.co/" + image[5:]

    print(Images, "\n")
    print(image, "\n")
    print(img_links.index(image), "\n")
    print(img_links)
    return image

#get_ifunny_image()

def get_reddit_berserk_image() -> str:
    #source = requests.get("https://www.reddit.com/r/Berserk/", headers = headers).text
    #source = requests.get("https://www.reddit.com/r/Berserk/", headers=headers)
    #soup = BeautifulSoup(source.text, 'html.parser')
    #time.sleep(5) 
    
    #print(soup)

    #Images = soup.select("faceplate-batch article shreddit-post div shreddit-aspect-ratio shreddit-lightbox-listener div img")
    #img_links=[]

    #for image in Images:
    #    img_links.append(image['src'])

    #image = img_links[random.randint(0, len(img_links) - 1)]
    #print(Images, "\n")
    #print(image, "\n")
    #print(img_links.index(image), "\n")
    #print(img_links)
    #return image

    source = requests.get("https://www.reddit.com/r/Berserk/", headers=headers)
    soup = BeautifulSoup(source.text, 'html.parser')

    domains = soup.find_all("span", class_="domain")

    return "" 


get_reddit_berserk_image()

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

