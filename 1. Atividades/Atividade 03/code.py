import requests, re, sys

# pego a url do site
url = sys.argv[1]

# faco uma requisicao GET
html = requests.get(url).text

# pego apenas os links
urls = re.findall('(?<=href=["\'])https?://.+?(?=["\'])', html)

file = open('result.txt', 'w')

# mostra cada um deles
for url in urls:
    print(url)
    file.write(url + '\n')