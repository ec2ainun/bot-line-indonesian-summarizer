import re
import urllib
from bs4 import BeautifulSoup

class listBerita:
    def __init__(self, link):
        self.link = link
    def daftarBerita(self):
        page = urllib.request.urlopen(self.link)
        soup = BeautifulSoup(page, "html.parser")
        artikel = soup.find_all("div", class_="article__title")
        dataList={}
        counter =0
        for element in artikel:
            dataList[counter] = {}
            dataList[counter]["judul"] = element.a.get_text()
            dataList[counter]["link"] = element.a["href"]
            counter = counter +1
        beritanotVideo = [data for data,info in dataList.items() if not info['judul'].lower().startswith(("video", "vlog")) if not 'galeri' in info['link']]
        dataListBaru = {}
        for x in beritanotVideo:
            dataListBaru[x] ={}
            dataListBaru[x]["judul"] = dataList[x]["judul"] 
            dataListBaru[x]["link"] = dataList[x]["link"]
        
        return dataListBaru