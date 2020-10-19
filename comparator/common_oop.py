###################################################################
# MAIN MODULE FOR AUXILIARY CLASSES, FOR WEBSCRAPPING:
# Consists of 5 classes:
# First is class for a signle search result,
# Next three are classes for collecting search results, each for one portal:
# - Amazon
# - Ebay
# - Allegro
# The last class contains debugging methods used in developement
#
# Each of the portal classes contains methods that set up the search parameters and one main method for webscraping
#
# The search phrase for allegro is translated using google API,
# Results from Allegro and Ebay are converted from PLN to USD using exchange rates from Polish NBP API
###################################################################

import requests, datetime, json
from bs4 import BeautifulSoup

# imports for google tranlate API
from google.cloud import translate_v2
from google.oauth2 import service_account
# from comparator import google_key

# header for tricking websites that 'it is not a robot'
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;     x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate",     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
dollar_info = requests.get('http://api.nbp.pl/api/exchangerates/rates/A/USD/?format=json')

# search limit set in global variable, might make it changable in further developement of the app
RESULTS_LIMIT = 15

class Search():
    ''' Class for a single search resault '''
    def __init__(self, phrase, platform, title, link, image, price_list):
        self.phrase = phrase
        self.platform = platform
        self.title = title
        self.link = link
        self.image = image
        self.dollar_exch = json.loads(dollar_info.text)['rates'][0]['mid']
        self.price = self.price_info_format(price_list)

    def __repr__(self):
        return "Search: {}, {} , {} , {} , {} , {}".format(self.phrase, self.platform, self.title, self.link, self.image, self.price)

    def change_to_dollars(self, price_in_pln):
        return price_in_pln / self.dollar_exch

    def price_info_format(self, price_info_list):
        ''' formats the price and converts PLN to USD '''
        for i, item in enumerate(price_info_list):
            # for Polish prices
            if item.endswith('zł'):
                #check if the price at allegro contais from / to
                if 'do' in item:
                    item_list = item.split('do')
                else:
                    item_list = [item]

                # apply currency conversion to every pricein the list
                for j, element in enumerate(item_list):
                    num = element.strip()[0:-2].strip()
                    num = '.'.join(num.split(',')) # change delimiters to dots
                    num = ''.join(num.split(' ')) # remove white spaces in prices
                    num = float(num)
                    dollars = self.change_to_dollars(num)
                    item_list[j] = "$ {:.2f}".format(dollars)
                if len(item_list) > 1:
                    final_price = ' to '.join(item_list)
                else:
                    final_price = item_list[0]
            # for prices in USD
            else:
                final_price = price_info_list[0]
        return final_price


class Amazon():

    def __init__(self, phrase):
        self.platform = 'amazon'
        self.phrase = phrase
        self.articles = None
        self.search_list = self.search(phrase)

    def __repr__(self):
        return f"Platform: {self.platform}, phrase: {self.phrase}"

    def search_setup(self):
        source = requests.get(f'https://www.amazon.com/s?k={self.phrase}', headers=headers).text
        soup = BeautifulSoup(source, 'lxml')

        self.articles = soup.select('div[data-component-type="s-search-result"]')

    def search(self, phrase):
        ''' main sub-function, compose list of objects'''

        # preliminary object setup
        self.phrase = phrase
        self.search_setup()

        # compose result list
        results = []
        if len(self.articles) > 0:
            for i, article in enumerate(self.articles):
                if len(results) < RESULTS_LIMIT:
                    title = article.h2.a.span.text
                    link = 'https://www.amazon.com' + article.h2.a['href']
                    image = article.img['src']
                    
                    # price info a little more complicated - html structure is more convoluted at the Amazon website
                    price_info = article.select('span.a-offscreen')
                    if len(price_info) > 0:
                        price_info = [price_info[0].text]
                    else:
                        price_info = ['not given']

                    results.append(Search(self.phrase, self.platform, title, link, image, price_info))

        return results

class Ebay():

    def __init__(self, phrase):
        self.phrase = phrase
        self.platform = 'ebay'
        self.search_limit = RESULTS_LIMIT
        self.soup = self.setup_search()
        self.search_list = self.search()
    
    def __repr__(self):
        reprlist = []
        for item in self.search_list:
            reprlist.append(item + "\n")
        return str(reprlist)

    def setup_search(self):
        source = requests.get(f'https://www.ebay.pl/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={self.phrase}&_sacat=0', headers=headers).text
        soup = BeautifulSoup(source, 'lxml')
        return soup

    def create_search_list(self):
        articles2 = self.soup.find('ul', class_='srp-list')
        results_list = articles2.find_all('li', limit=self.search_limit)

        return results_list

    def search(self):
        ''' Main subfucntion, creates the list of objects for display '''

        results = self.create_search_list()

        results_json = []
        
        for i, item in enumerate(results):
            platform = 'ebay'
            title = item.img['alt']
            link = item.a['href']
            image = item.find('div', class_='s-item__image-wrapper').img['src']
            price_info = []

            price_list = [item.find('span', class_="s-item__price").text]

            results_json.append(Search(self.phrase, self.platform, title, link, image, price_list))

        return results_json

class Allegro():

    def __init__(self, phrase):
        self.platform = "allegro"
        self.phrase = self.translate_to_polish(phrase)
        self.soup = self.setup_search()
        self.search_list = self.search()

    def __repr__(self):
        return self.search_list
    
    def translate_to_polish(self, phrase): 
        """ Translates phrase to Polish for Allegro """
        # credentials for google translate API
        client = service_account.Credentials.from_service_account_file('./comparator/credentials/flask-search-compare-5bba163ea97b.json')

        # translation proper
        translation_client = translate_v2.Client(target_language='pl')
        result = translation_client.translate(phrase, source_language='eng')
    
        return result['translatedText']

    def setup_search(self):
        source = requests.get(f'https://allegro.pl/listing?string={self.phrase}', headers=headers).text
        soup = BeautifulSoup(source, 'lxml')
        return soup

    def create_search_list(self):
        search_frame = self.soup.find_all('section', class_="_9c44d_3pyzl")
        articles = []
        for item in search_frame:
            articles.extend(item.find_all('article')[:RESULTS_LIMIT])

        print(len(articles))
        return articles

    def search(self):
        ''' main search subfunction '''
        raw_list = self.create_search_list()
        results_json = []

        for i, item in enumerate(raw_list):
            title = item.h2.text.strip()
            link = item.a['href']

            # allegro sometimes gives two digfferent links for pictures, here the proper one is referred to
            if 'data-src' in item.a.img.attrs.keys():
                image = item.a.img['data-src']
            else:
                image = item.a.img['src']

            # composing price information, equivalent to the former two (two-dimensional list)
            price_info = []
            regular_price = item.find('div', class_='_9c44d_2K6FN').text
            price_info.append(regular_price)
            if item.find('div', class_='_9c44d_21XN-') != None:
                price_with_delivery = item.find('div', class_='_9c44d_21XN-').text
                price_info.append(price_with_delivery)
            
            # in case price is not given, such informtion is given
            if len(price_info) == 0:
                price_info.append('not given')

            results_json.append(Search(self.phrase, self.platform, title, link, image, price_info))

        return results_json

class Debug():
    ''' class used for debugging in the development '''

    @staticmethod
    def print_to_file(data):
        ''' These functions are used to print data inside webscraping functions, only for debugging purposes  '''
        with open('search_data.txt', 'w') as filename:
            filename.write(data)

    @staticmethod
    def print_results(result_json):
        for i, item in enumerate(result_json):
            print(f'--- Item {i} ---')
            print(item['platform'])
            print(item['title'])
            print(item['link'])
            print(item['image'])
            print(item['price'])
            print()