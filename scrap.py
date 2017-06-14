from lxml import html
import requests
import re
import json


lb_clean_price = lambda x : re.sub("[^0-9]", "", x)
lb_clean_text = lambda x: x.strip().encode("ascii", "ignore")




def extract_item_from_url(url, current_deep):
    items = []
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
            items = items + extract_item_from_url(next_url, current_deep - 1)
    return items




def get_lbc_items(base_url, max_deep, output_file):
    items = extract_item_from_url(base_url, max_deep)
    file_ouput = open(output_file, "w")
    file_ouput.write(json.dumps(items, indent=4, separators=(',', ': ')))

get_lbc_items("https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/?th=1&ps=1&pe=3&sqs=1&sqe=9&ret=1&ret=2", 2,"./output-buy-price.json")
get_lbc_items("https://www.leboncoin.fr/locations/offres/ile_de_france/?th=1&sqs=1&sqe=8&ret=1&ret=2", 3,"./output-rent-price.json")
