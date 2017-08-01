import re
import urllib
from bs4 import BeautifulSoup
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
factory = StemmerFactory()
stemmer = factory.create_stemmer()
import numpy as np

class Berita:
    def __init__(self, link):
        self.link = link
    def rangkumanBerita(self):
        stopwords = open('id.stopwords.02.01.2016.txt','r').read().split('\n')
        halamanBerita = urllib.request.urlopen(self.link)
        soup = BeautifulSoup(halamanBerita, "html.parser")
        isi = soup.find("h3", class_="read__content")
        if(len(isi)<2):
            return ""
        isi = isi.find_all("p")
        
        isiParagraf=[]
        for paragraf in isi:
            teks = paragraf.get_text()
            isiParagraf.append(teks)
        isiParagraf = [x for x in isiParagraf if not x.startswith('Baca')]
        
        satuParagraf=[]
        for data in isiParagraf:
            isi = re.split(r'\. +', data)
            isi =[x for x in isi if not x=='']
            satuParagraf.extend(isi)
        
        globaldatakata={}
        datakataperkal ={}
        counterkal =0
        for kalimat in satuParagraf:
            hapuskurung = re.sub(r'([^A-Za-z0-9-\/\.]+)', ' ', kalimat)
            hapustitiktypo = re.sub(r'\s\.\s', ' ', hapuskurung)
            hapustitikawaldanakhir = re.sub(r'(\.\s)|(\.$)', ' ', hapustitiktypo)
            tokenisasi = re.split(r'\s+', hapustitikawaldanakhir)
            token =[x for x in tokenisasi if not x=='']
            # stemmer
            token =[stemmer.stem(x) for x in token]
            datakataperkal[counterkal]={}
            #kata unik
            for kata in token:
                if not kata in stopwords:
                    datakataperkal[counterkal][kata]=0
                    if not kata in globaldatakata.keys():
                        globaldatakata[kata]=0

            for kataunik in datakataperkal[counterkal]:
                for kata in token:
                    if(kataunik==kata):
                        datakataperkal[counterkal][kata] = datakataperkal[counterkal][kata] + 1
                        globaldatakata[kata]= globaldatakata[kata] + 1

            counterkal = counterkal +1
            
        score = {}
        for kal in datakataperkal:
            score[kal] =0
            for kata in globaldatakata.keys():
                for katakal in datakataperkal[kal].keys():
                    if(kata == katakal):
                        tf = 1 + np.log10(datakataperkal[kal][katakal])
                        idf = np.log10(len(globaldatakata)/globaldatakata[kata])
                        bobot = tf * idf
                        score[kal] = score[kal] + bobot
        
        urutbesarkecil = list(sorted(score, key=score.__getitem__, reverse=True))
        batas =0
        dataRangkuman=[]
        for x in urutbesarkecil:
            dataRangkuman.append(x)
            batas = batas+1
            if(batas >= len(datakataperkal)/2):
                break
        rangkuman =np.sort(dataRangkuman) 
        hasil =[]
        for index in rangkuman:
            hasil.append(satuParagraf[index])
        return hasil