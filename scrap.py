from lxml import html
import requests
import re
import json


lb_clean_price = lambda x : re.sub("[^0-9]", "", x)
lb_clean_text = lambda x: x.strip().encode("ascii", "ignore")



items = []
def extract_item_from_url(url, current_deep):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    sections = tree.xpath('//section[@class="item_infos"]')
    for section in sections:
        price = map(lb_clean_price, section.xpath('h3[@class="item_price"]/text()'))
        name = map(lb_clean_text, section.xpath('h2[@class="item_title"]/text()'))
        city = map(lb_clean_text, section.xpath('p/meta[@itemprop="address"]/@content'))
        depatement = (city[1] if len(city) >1 else '')
        if price and name and city:
            item = {
            'price':price[0],
            'name':name[0],
            'city':city[0],
            'depatement':depatement
            }
            items.append(item)
        next_link = tree.xpath('//a[@id="next"]/@href')

    #Look for the next page
    if next_link:
        next_url = '%s%s' % ("http:",next_link[0])
        print next_url
        if current_deep > 0:
            extract_item_from_url(next_url, current_deep - 1)





#Get buy prices
base_url = "https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/?th=1&ps=1&pe=3&sqs=1&sqe=9&ret=1&ret=2"
extract_item_from_url(base_url, 20)
file_ouput = open("./output-buy-price.json", "w")
file_ouput.write(json.dumps(items, indent=4, separators=(',', ': ')))

#Get rent prices
items = []
base_url = "https://www.leboncoin.fr/locations/offres/ile_de_france/?th=1&sqs=1&sqe=8&ret=1&ret=2"
extract_item_from_url(base_url, 30)
file_ouput = open("./output-rent-price.json", "w")
file_ouput.write(json.dumps(items, indent=4, separators=(',', ': ')))
