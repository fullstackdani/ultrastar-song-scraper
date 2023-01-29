#http://usdb.animux.de/index.php?link=byartist
#http://usdb.animux.de/index.php?link=byartist&select=A
#http://usdb.animux.de/index.php?&link=detail&id=25926

import requests, re, subprocess, os, sys, shutil
from unidecode import unidecode
from youtubesearchpython import VideosSearch
from bs4 import BeautifulSoup

# Global Vars
baseURL = 'http://usdb.animux.de/'
cookies = 'PHPSESSID=pimmgp74q7pvvsc0rcpsvtq1b0; __utma=7495734.1066121223.1674939615.1674939615.1674939615.1; __utmc=7495734; __utmz=7495734.1674939615.1.1.utmcsr=l.messenger.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt=1; __utmb=7495734.6.10.1674939615'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Cookie': cookies,
    'Host': 'usdb.animux.de',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
}

# Global Functions
def youtubeFile(url, _type):
    command = "youtube-dl -x "

    if _type == "video":
        command = command+"-f mp4"
    else:
        command = command+"--audio-format mp3"

    command = command+" -e -g " + url

    rows = exec(command).split("\n")

    return youtubeFixURL(rows[1])


def youtubeFixURL(url):
    if url.find('manifest') != -1:
        try:
            result = xmltodict.parse(request(url=url).content)
            url = result['MPD']['Period']['AdaptationSet'][0]['Representation'][0]['BaseURL']
        except:
            url = url

    return url


def youtubeSearch(query, _type, limit=5):
    rows = VideosSearch(query, limit).result()["result"]

    results = []
    for row in rows:
        if row['type'] == 'video':
            results.append({
                'title': row['title'],
                'url': row['link'],
                'thumbnail': row['thumbnails'][0]['url']
            })

    return results


def exec(command):
    return subprocess.run(command.split(' '), stdout=subprocess.PIPE).stdout.decode("utf-8")


def images(query):
    response = requests.get(
        "https://google.com/search?q="
        + query.replace(" ", "+")
        + "&tbm=isch"
    )
    
    results = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        for g in soup.find_all("div", class_="NZWO1b"):
            img = g.find_all("img")
            if img and ("src" in img[0].attrs):
                if img[0].attrs["alt"].strip() == "":
                    img[0].attrs["alt"] = query
                results.append(
                    {
                        "title": img[0].attrs["alt"],
                        "url": img[0].attrs["src"],
                        "thumbnail": img[0].attrs["src"],
                    }
                )

        result = results[0]
    
    return result

# Get Artists Alphabet
def getAlphabet():
    url = headers['Referer'] = baseURL + "index.php?link=byartist"
    data = requests.get(url = url, headers = headers)

    response = []

    soup = BeautifulSoup(data.text, features="html.parser")
    for alphabet in soup.select('h1 a[href*="index.php?link=byartist&select="]'):
        response.append(alphabet['href'].replace('index.php?link=byartist&select=', ''))
    
    return response

def getArtistSongsByFirstNameLetter(letter):
    url = headers['Referer'] = baseURL + "index.php?link=byartist&select=" + str(letter)
    data = requests.get(url = url, headers = headers)

    soup = BeautifulSoup(data.text, features="html.parser")
    for scripts in soup.select('script[type="text/javascript"]:not([src])'):
        if '?&link=detail&id=' in scripts.get_text():
            response = []

            songs = re.findall('\$\(\"(.*)\"\).innerHTML.*detail&id=(.*)\'>(.*)<\/a>', scripts.get_text())

            for song in songs:
                response.append({
                    "id": song[1],
                    "artist": song[0],
                    "song": song[2]
                })
    
            return response
    
    return []

def processSong(song):
    url = headers['Referer'] = baseURL + "index.php?link=detail&id=" + song['id']
    data = requests.get(url = url, headers = headers)

    soup = BeautifulSoup(data.text, features="html.parser")
    
    auxData = soup.select('table tr[class="list_head"] td')
    song['artist'] = auxData[0].get_text()
    song['song'] = auxData[1].get_text()

    fullName = song['artist'] + ' - ' + song['song']

    baseDir = './songs/' + fullName + '/'
    if not(os.path.exists(baseDir)):
        os.mkdir(baseDir)
        print("\n\nProcessing " + song['artist'] + ' - ' + song['song'] + '...')

        song['youtube'] = None
        auxData = soup.select_one('param[name="movie"][value]')
        if auxData and auxData['value']:
            auxData = re.search('.*v/([A-Za-z0-9-_]*)&', auxData['value'])
            if auxData and auxData.groups() and auxData.groups()[0]:
                song['youtube'] = 'https://youtube.com/watch?v=' + auxData.groups()[0]
        
        song['cover'] = None
        auxData = soup.select_one('table tr[class="list_tr1"] td img[src]')
        if auxData and auxData['src'] and not('nocover' in auxData['src']):
            song['cover'] = baseURL + auxData['src']


        url = headers['Referer'] = baseURL + "index.php?link=gettxt&id=" + song['id']
        data = requests.post(url = url, headers = headers, data = {"wd": 1})

        song['lyrics'] = None
        soup = BeautifulSoup(data.text, features="html.parser")
        auxData = soup.select_one('form[id="myform"] textarea[name="txt"]')
        if auxData and auxData.get_text():
            song['lyrics'] = auxData.get_text()

        if not(song['youtube']):
            results = youtubeSearch(song['artist'] + ' - ' + song['song'], 'video', 1)

            if results and len(results) > 0:
                song['youtube'] = results[0]['url']
            else:
                return 'fail - no youtube video'
        
        url = youtubeFile(song['youtube'], 'video')
        if not('.m3u8' in url):
            song['mp4'] = url
        else:
            return 'fail - no video file'
        
        url = youtubeFile(song['youtube'], 'audio')
        if not('.m3u8' in url):
            song['mp3'] = url
        else:
            return 'fail - no audio file'

        del song['youtube']

        if not(song['cover']):
            print('Get cover from google images...')
            auxData = images(song['artist'] + ' - ' + song['song'] + ' album')
            if auxData and auxData['url']:
                song['cover'] = auxData['url']

        auxData = re.findall(r"(^#(ARTIST|TITLE|MP3|COVER|BACKGROUND|VIDEO):.*$(\r\n|\n))", song['lyrics'], re.MULTILINE)
        for auxLine in auxData:
            song['lyrics'] = song['lyrics'].replace(auxLine[0], '')

        song['lyrics'] = "#ARTIST:" + song['artist'] + "\n" + "#TITLE:" + song['song'] + "\n" + "#MP3:" + fullName + ".mp3\n" + "#COVER:" + fullName + ".png\n" + "#BACKGROUND:" + fullName + ".png\n" + "#VIDEO:" + fullName + ".mp4\n" + song['lyrics']

        print("Downloading MP3...")
        tries = 0
        while tries < 3:
            auxData = requests.get(song['mp3'])
            if tries < 3:
                tries+=1
                if auxData and auxData.content:
                    f = open(baseDir + fullName + '.mp3', "wb")
                    f.write(auxData.content)
                    f.close()
                    break
            else:
                shutil.rmtree(baseDir, ignore_errors=True)
                return 'fail - could not download mp3'

        print("Downloading MP4...")
        tries = 0
        while tries < 3:
            auxData = requests.get(song['mp4'])
            if tries < 3:
                tries+=1
                if auxData and auxData.content:
                    f = open(baseDir + fullName + '.mp4', "wb")
                    f.write(auxData.content)
                    f.close()
                    break
            else:
                shutil.rmtree(baseDir, ignore_errors=True)
                return 'fail - could not download mp4'

        print("Downloading Cover...")
        tries = 0
        while tries < 3:
            auxData = requests.get(song['cover'])
            if tries < 3:
                tries+=1
                if auxData and auxData.content:
                    f = open(baseDir + fullName + '.png', "wb")
                    f.write(auxData.content)
                    f.close()
                    break
            else:
                shutil.rmtree(baseDir, ignore_errors=True)
                return 'fail - could not download cover'

        print("Writing Lyrics...")
        f = open(baseDir + fullName + '.txt', "w")
        f.write(song['lyrics'])
        f.close()
    
    else:
        print('Already downloaded.')
    
    return 'Finished successfully.'


# Run Script

print("Getting alphabet...")
tries = 0
while tries < 3:
    tries+=1
    try:
        alphabet = getAlphabet()
        break
    except:
        if tries == 3:
            print('Could not get alphabet...')
            quit()


if len(sys.argv) > 1:
    letter = sys.argv[1][0].lower()
    if letter in alphabet:
        print('That artist does not exist, at least by that name.')
    else:
        alphabet = [letter]

for letter in alphabet:
    print("Getting Songs...")
    tries = 0
    while tries < 3:
        tries+=1
        try:
            songs = getArtistSongsByFirstNameLetter(letter)
            break
        except:
            if tries == 3:
                print('Could not get artists and songs...')

    print("Processing Songs...")
    for song in songs:
        if  (len(sys.argv) < 2 or (len(sys.argv) > 1 and unidecode(sys.argv[1].lower().replace(' ', '')) == unidecode(song['artist'].lower().replace(' ', '')))) and (len(sys.argv) < 3 or (len(sys.argv) > 2 and unidecode(sys.argv[2].lower().replace(' ', '')) == unidecode(song['song'].lower().replace(' ', '')))):
            tries = 0
            while tries < 3:
                tries+=1
                try:
                    print(processSong(song))
                    break
                except:
                    if tries == 3:
                        print('Could not process music...')