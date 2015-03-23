from bs4 import BeautifulSoup
import requests
from pprint import pprint

url = "hyotynen.iki.fi/trekfailure"
r = requests.get("http://" + url)
data = r.text
soup = BeautifulSoup(data)
from sqlitedict import SqliteDict
dict_db = SqliteDict('resources/treknobabble.sqlite', autocommit=True)


treknobabble = []
failure = {}
myset = []


def get_tb():
    duplicates = 0
    unique = 0
    for x in range(50):
        print "getting treknobabble: " + str(x)
        url = "hyotynen.iki.fi/trekfailure"
        r = requests.get("http://" + url)
        data = r.text
        soup = BeautifulSoup(data)
        for x in range(1):
            myset = []
            for link in soup.find_all('h1'):
                tmp = link.get_text()
                string = tmp[5:-3]
                myset.append(string)
            if myset[0] not in dict_db.iterkeys():
                dict_db[myset[0]] = myset[1]
                unique += 1
            else:
                print "Duplicate"
                duplicates += 1
        treknobabble.append(failure)

# get_tb()

for item in dict_db.iteritems():
    pprint(item)

print len(dict_db)
dict_db.close()

