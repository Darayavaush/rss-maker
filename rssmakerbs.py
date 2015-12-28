
import PyRSS2Gen
import datetime
import argparse
import requests
from bs4 import BeautifulSoup
import re
import feedparser


parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name', required=True, help='name of the whole feed')
parser.add_argument('-f', '--file', required=True)
parser.add_argument('-u', '--url', required=True)
parser.add_argument('-b', '--base', help='narrow the lookup to the contents of this item')
parser.add_argument('-c', '--criteria', required=True, help='criteria of picking the base items')
parser.add_argument('-d', '--description', help='description scheme of individual items')
parser.add_argument('-l', '--link', required=True, help='link scheme of individual items. Base item name is \'item\'')
parser.add_argument('-t', '--title', help='title scheme of individual items')
parser.add_argument('-q', '--limit', help='number of items to take. >0 = take items from beginning, otherwise from end', default=-50)
parser.add_argument('-x', '--cookies', help='cookies to include with the request', default='{}')
parser.add_argument('-o', '--overwrite', help='don\'t fetch existing feed', action="store_true")
parser.add_argument('-a', '--auth', help='dictionary containing authorization information')
parser.add_argument('-z', '--debug', action="store_true")
args = parser.parse_args()

if args.overwrite:
    items = []
    oldlinks = []
else:
    feed = feedparser.parse(args.file)
    items = [
        PyRSS2Gen.RSSItem(
            title=x.title,
            link=x.link,
            description=x.summary,
        )
        for x in feed.entries
    ]
    oldlinks = [x.link for x in items]



soup = BeautifulSoup(requests.get(args.url, cookies=eval(args.cookies)).text)
if args.base:
    soup = soup.find(**eval(args.base))
args.limit = int(args.limit)
if args.limit > 0:
    newitems = soup(**eval(args.criteria))[:args.limit]
elif args.limit < 0:
    newitems = soup(**eval(args.criteria))[args.limit:]
else:
    newitems = soup(**eval(args.criteria))
if args.debug:
    print(newitems)
    exit()
for item in newitems:
    link = str(eval(args.link))
    # print(link)
    if link not in oldlinks:
        try:
            description = str(eval(args.description)) if args.description else ''
        except:
            description = ''
        items.append(
            PyRSS2Gen.RSSItem(
                title=str(eval(args.title)) if args.title else item,
                link=link,
                # description= ''
                description=description
                )
        )

        if args.debug:
            print(items[-1].title)
        #     with open('temp.html', 'w', encoding='utf8') as f:
        #         f.write(requests.get(args.url, cookies=eval(args.cookies)).text)
        #         exit()

rss = PyRSS2Gen.RSS2(
    title=args.name,
    link=args.url,
    description="RSS maker made by Dariush.",
    language='en-us',
    lastBuildDate=datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
    docs='http://blogs.law.harvard.edu/tech/rss',
    items=items[-100:],
)
f = open(args.file, encoding="utf-8", mode="w")
f.write(rss.to_xml("utf-8").replace('><', '>\n<'))
