import requests
from bs4 import BeautifulSoup
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TPE1, TIT2, TALB

domain = 'http://www.luoo.net/music/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36','Cookie': 'AspxAutoDetectCookieSupport=1',}
link = 'http://mp3-cdn2.luoo.net/low/luoo/radio{}/{}.mp3'
run = True

def getSoup(url):
    gr = requests.get(url)
    gs = BeautifulSoup(gr.text,'html.parser')
    return gs

def addAlbumPic(songName, coverName):
    audio = MP3(songName, ID3=ID3)
    id3 = ID3(songName)
    if id3.getall('APIC'):id3.delall('APIC')
    id3.add(APIC(encoding = 0,mime = 'image/jpeg',type = 3,data = open(coverName,'rb').read()))
    id3.save(v2_version = 3)

def addAlbumPicEnhance(songName, coverName, songArtists, songAlbum):
    audio = MP3(songName, ID3=ID3)
    audio.add_tags()
    audio.save()
    id3 = ID3(songName)
    id3.add(TPE1(encoding=3,text=songArtists))
    id3.add(TIT2(encoding=3,text=songName[:-4]))
    id3.add(TALB(encoding=3,text=songAlbum))
    id3.add(APIC(encoding = 0,mime = 'image/jpeg',type = 3,data = open(coverName,'rb').read()))
    id3.save(v2_version = 3)

def fileSave(songName,songUrl):
    if os.path.isfile(songName):
        pass
    else:
        with open(songName,'wb') as file:
            file.write(requests.get(songUrl,headers = headers).content)

def folderMaker(foldername):
    if os.path.exists(foldername):
        pass
    else:
        os.mkdir(foldername)
    os.chdir(foldername)

while run:
    indexSoup = getSoup(domain)
    for album in indexSoup.select('.meta.rounded.clearfix a'):
        albumSoup = getSoup(album['href'])
        albumIndex = str(int(album.text[4:7]))
        albumName = album.text
        folderMaker(albumName)
        for song in albumSoup.select('.track-wrapper.clearfix'):
            songName = (song.select('.trackname')[0].text[4:] + '.mp3').replace('/','／').replace('\\','＼')
            coverUrl = song.select('.btn-action-share')[0]['data-img']
            songIndex = albumSoup.select('.track-wrapper.clearfix').index(song) + 1
            songUrl = link.format(albumIndex,'%02d'% songIndex)
            songUrl2 = link.format(albumIndex,str(songIndex))
            coverName = 'temp.jpg'
            try:
                fileSave(songName,songUrl)
            except:
                fileSave(songName,songUrl2)
            fileSave(coverName,coverUrl)
            try:
                addAlbumPic(songName, coverName)
            except:
                songArtists = albumSoup.select('.track-detail')[songIndex - 1].select('p')[1].text[8:]
                songAlbum = albumSoup.select('.track-detail')[songIndex - 1].select('p')[2].text[7:]
                addAlbumPicEnhance(songName, coverName, songArtists, songAlbum)
            os.remove(coverName)
        os.chdir(os.path.pardir)
    try:
        domain = indexSoup.select('a.next')[0]['href']
    except:
        run = False