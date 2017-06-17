from lxml import html
import requests
import re
import json


lb_clean_price = lambda x : re.sub("[^0-9]", "", x)

#TODO transform accents to non accents characters
lb_clean_text = lambda x: x.strip().encode("ascii", "ignore")

#This variable contains the values in the parge of the item that we want to save
#We need to remove the none ascii chars
items_to_save = ['Surface', 'GES', 'Pices', 'Classe nergie', 'Type de bien']
def extract_item_detail(url):
    print ("-----"+url)
    page = requests.get(url)
    tree = html.fromstring(page.content)
    section = tree.xpath('//section[@class="properties lineNegative"]')[0]

    #get the table detail
    detail = section.xpath('div[@class="line properties_description"]/p[@itemprop="description"]/text()')
    detail = (lb_clean_text(detail[0]) if detail else "")
    properties = section.xpath('div/h2[@class="clearfix"]')
    dic = {}

    #Get all item properties
    for prop in properties:
        cat = prop.xpath('span[@class="property"]/text()')
        val = prop.xpath('span[@class="value"]/text()')

        cat = (lb_clean_text(cat[0]) if cat else "")
        val = (lb_clean_text(val[0]) if val else "")
        if(cat in items_to_save):

            #Get energie clas stored in a <a> link
            if(cat in ['GES', 'Classe nergie']):
                val = prop.xpath('span/a[@class="popin-open"]/text()')
                val = (val[0][0] if val else "")

            #add all key/values in dictionnary
            dic[cat] = val

    #store description in the dictionnary
    dic['description'] = detail
    return dic

def extract_item_from_url(url, current_deep):
    print url
    items = []
    page = requests.get(url)
    tree = html.fromstring(page.content)
    sections = tree.xpath('//a[@class="list_item clearfix trackable"]')
    for section in sections:
        href= '%s%s' % ("http:",section.xpath('@href')[0])
        price = map(lb_clean_price, section.xpath('section/h3[@class="item_price"]/text()'))
        name = map(lb_clean_text, section.xpath('section/h2[@class="item_title"]/text()'))
        city = map(lb_clean_text, section.xpath('section/p/meta[@itemprop="address"]/@content'))
        date = section.xpath('section/aside/p[@class="item_supp"]/@content')
        depatement = (city[1] if len(city) >1 else '')
        item_detail = extract_item_detail(href)

        if price and name and city and href and date:
            item = {
            'price':price[0],
            'name':name[0],
            'city':city[0],
            'date':date[0],
            'depatement':depatement,
            'href':href,
            'detail':item_detail
            }
            items.append(item)
    next_link = tree.xpath('//a[@id="next"]/@href')

    #Look for the next page
    if next_link:
        next_url = '%s%s' % ("http:",next_link[0])
        if current_deep > 1:
            items = items + extract_item_from_url(next_url, current_deep - 1)
    return items




def get_lbc_items(base_url, max_deep, output_file):
    items = extract_item_from_url(base_url, max_deep)
    file_ouput = open(output_file, "w")
    file_ouput.write(json.dumps(items, indent=4, separators=(',', ': ')))

get_lbc_items("https://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/?th=1&ps=1&pe=3&sqs=1&sqe=9&ret=1&ret=2", 1,"./output-buy-price.json")
get_lbc_items("https://www.leboncoin.fr/locations/offres/ile_de_france/?th=1&sqs=1&sqe=8&ret=1&ret=2", 1,"./output-rent-price.json")
