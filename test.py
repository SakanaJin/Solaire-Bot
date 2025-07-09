from bs4 import BeautifulSoup
import requests
import random

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

source = requests.get(f"https://e621.net/posts?page={random.randint(1,21)}&tags=hi_res+why", headers = headers)
soup = BeautifulSoup(source.text, 'html.parser')
Images = soup.find_all('img')
img_links=[image['src'] for image in Images]
print(img_links[random.randint(2,65)]) #2 - 65