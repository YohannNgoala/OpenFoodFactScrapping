import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime




#Invisible Chrome opening
def set_options():
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    return options

def get_soup_html(options, url, page):
    driver = webdriver.Chrome(options=options, executable_path="C:\IA School\chromedriver")
    driver.get(url + str(page))
    html = driver.page_source
    driver.quit()
    return BeautifulSoup(html, 'html.parser')

def get_products_href(soup, productsHref):
    elements = soup.find_all('a', attrs={'class': 'list_product_a'})
    for e in elements:
        productsHref.append(e["href"])
    return productsHref

def get_all_hrefs():
    hasNextPage = True
    page = 6
    options = set_options()
    productsHref = []
    while ( hasNextPage and page < 7):
        soup = get_soup_html(options, "https://fr.openfoodfacts.org/", page)
        productsHref = get_products_href(soup, productsHref)
        page += 1
        if soup.find('a', {'rel': 'next$nofollow'}) == None:
            hasNextPage = False
    return productsHref

def find_element_regex(soup, regex):
    element = soup.find(string=re.compile(regex))
    if element == None:
        return 'XXX'
    else:
        return element[-1]

def find_elements_flag(soup, flag, attribute, name, isHref, refName):
    elements = soup.findAll(flag, {attribute:name})
    if elements == []:
        return 'XXX'
    else:
        element = []
        for e in elements:
            if isHref == True:
                ref = e["href"][0:len(refName)]
                if  ref == refName:
                    element.append(e.getText())
            else:
                element.append(e.getText())
        if element == []:
            element = 'XXX'
        return element

def get_quantity(weights, idx):
    try:
        q = weights[idx].strip()
        if (idx != 0):
            q = q[:-1]
            q = q.strip()
            float(q)
        return q
    except:
        return 'XXX'

def get_energy(soup):
    if (soup.find(string=re.compile('([0-9])+ (kcal)')) == None):
        energy = 'XXX'
    else:
        energy = soup.find(string=re.compile('([0-9])+ (kcal)')).strip()
        energy = energy.replace(' kcal', '')
    try:
        float(energy)
        return energy
    except:
        return 'XXX'

#compare
#website

def scrap_product_data(href, data):
    options = set_options()
    soup = get_soup_html(options, href ,' ')
    weights = soup.findAll(string=re.compile("^ [0-9]+((\.|,)[0-9]+)? ?(g|l)")) #Regex to get all quantities in the html page
    data['ProductName'].append(find_elements_flag(soup, 'h1', 'property', 'food:name', False,''))
    data['BarCode'].append(find_elements_flag(soup, 'span', 'property','food:code', False, ''))
    data['NutriScore'].append(find_element_regex(soup, "Nutri-Score [A-E]"))
    data['NovaScore'].append(find_element_regex(soup, "NOVA [1-4]"))
    data['EcoScore'].append(find_element_regex(soup, "Éco-Score [A-E]"))
    data['Quantity'].append(get_quantity(weights, 0))
    data['Conditioning'].append(find_elements_flag(soup, 'a', 'href', re.compile('/conditionnement'),
                                          True, '/conditionnement'))
    data['Brands'].append(find_elements_flag(soup, 'a', 'itemprop', 'brand', True, '/marque'))
    data['Categories'].append(find_elements_flag(soup, 'a', 'class', 'tag well_known', True, '/categorie'))
    data['Label'].append(find_elements_flag(soup, 'a', 'class', re.compile('(tag well_known)|(tag user_defined)'), True, '/label'))
    data['Origin'].append(find_elements_flag(soup, 'a', 'class', 'tag well_known', True, '/origine'))
    data['ManufacturePlace'].append(find_elements_flag(soup, 'a', 'href', re.compile('/lieu-de-fabrication'),
                                          True, '/lieu-de-fabrication'))
    data['Traceability'].append(find_elements_flag(soup, 'a', 'href', re.compile('/code-emballeur'),
                                          True, '/code-emballeur'))
    data['Store'].append(find_elements_flag(soup, 'a', 'href', re.compile('/magasin'),
                                          True, '/magasin'))
    data['SellCountries'].append(find_elements_flag(soup, 'a', 'href', re.compile('/pays'),
                                          True, '/pays'))
    data['Additives'].append(find_elements_flag(soup, 'a', 'href', re.compile('/additif'),
                                          True, '/additif'))
    data['PalmOil'].append(find_elements_flag(soup, 'a', 'href',
                                 re.compile('/ingredients-issus-de-l-huile-de-palme'),
                                 True, '/ingredients-issus-de-l-huile-de-palme'))
    data['Fat'].append(get_quantity(weights, 1))
    data['TransFat'].append(get_quantity(weights, 2))
    data['Sugar'].append(get_quantity(weights, 3))
    data['Salt'].append(get_quantity(weights, 4))
    data['Energy'].append(get_energy(soup))
    print(weights)
    return data



if __name__ == '__main__':
    startTime = datetime.now()
    data = {'ProductName': [],
            'BarCode': [],
            'NutriScore': [],
            'NovaScore': [],
            'EcoScore': [],
            'Quantity': [],
            'Conditioning': [],
            'Brands': [],
            'Categories': [],
            'Label': [],
            'Origin': [],
            'ManufacturePlace': [],
            'Traceability': [],
            'Store': [],
            'SellCountries': [],
            'Additives': [],
            'PalmOil': [],
            'Fat': [],
            'TransFat': [],
            'Sugar': [],
            'Salt': [],
            'Energy': []
            }
    index = []
    productsHref = get_all_hrefs()
    data = scrap_product_data(productsHref[68], data)
    # for p in productsHref:
    #     data = scrap_product_data(p, data)
    df = pd.DataFrame(data)
    print(data)
