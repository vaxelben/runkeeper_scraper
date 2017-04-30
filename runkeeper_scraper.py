import requests
from bs4 import BeautifulSoup
import re
import json
import os

tempid = 0
monthsDict = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}

# File
f = open('runkeeper_metz.json', 'w')
f.write('[')

# Loop on runkeeper results pages
for p in range(1, 2):
  print("page " + str(p))
  
  url1 = "http://runkeeper.com/search/routes/" + str(p) + "?distance=&location=metz&lon=6.183&lat=49.111"
  
  r1 = requests.get(url1)
  page1 = r1.text

  soup1 = BeautifulSoup(page1, "html.parser")

  # Loop on runs in each results page
  for item1 in soup1.find_all('div', attrs={'class': 'routeResultTile'}):
    for link in item1.find_all('a'):
      if 'user' in link.get('href'):
        url2 = "http://runkeeper.com" + link.get('href')
        r2 = requests.get(url2)
        page2 = r2.text
        soup2 = BeautifulSoup(page2, "html.parser")

        # Get run date from tag :
        # <meta name="description" content="6.76mi Running Route created on 05/29/2015 on Runkeeper"/>
        for itemDate in soup2.find_all('meta', attrs={'name': 'description'}):
          text = itemDate.get('content')
          m = re.search('Route created on (.+?) on Runkeeper', text)
          if m:
            rawDate = m.group(1)
            dDate = rawDate.split()
            fDate = dDate[5] + "-" + monthsDict[dDate[1]] + "-" + dDate[2]

        # Run coordinates in tags :
        # <script type="text/javascript">
        for item2 in soup2.find_all('script', attrs={'type': 'text/javascript'}):
          if item2.find(string=re.compile('var routePoints')):
            route = item2.getText(strip=True)

            tempid += 1

            for string in item2.stripped_strings:
              finalStr = string.split('\n', 1)[0] + '\n'
              finalStr = finalStr.replace('var routePoints = [', '', 1)
              finalStr = finalStr.replace('];', '', 1)
              finalStr = finalStr.replace('},{', '}\n{')

              test = finalStr.split('\n')
              for i in range(0, len(test) - 1):
                data = json.loads(test[i])

                # Drop unused fields
                data.pop('deltaPause', None)
                data.pop('type', None)
                data.pop('deltaDistance', None)
                data.pop('deltaTime', None)

                # Add an id
                data['tempid'] = tempid
                data['routeDate'] = fDate

                json.dump(data, f, indent=0)
                f.write(',')

f.write(']')
f.close()