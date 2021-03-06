###################################################################
# MAIN MODULE FOR AUXILIARY FUNCTIONS, MOSTLY FOR WEBSCRAPPING:
# 1. Global variables: 
#   -   headers required to trick amazon that it is na actual user searching, 
#   -   client is link to credentials for google translate API
# 2. Function for translating search phrase to Polish for Allegro (translate_to_polish())
# 3. Two debugging functions: one for printing in terminal, one for writing to file.
# 4. Webscrapping functions - the core of the app:
#   -   The first is a formatting function for price info. 
#       This info is convoluted for amazon and had to be properly formatted.
#       The other info had to be adjucted accordingly.
#   -   The next three functions are for webscrapping in each of the platforms.
#       Each function consists of two-three subfunctions.
# 5. Database functions, they limit and taylor the data for display and save in database:
#   -   The first function limits results to 10 for each platform in one search.
#       This allows to keep the database small and clean (it is necessary to keep it small on a payed server).
#   -   The latter sets the common id for searches and results.
###################################################################

import requests, datetime
from bs4 import BeautifulSoup

# imports for google tranlate API
from google.cloud import translate_v2
from google.oauth2 import service_account
from comparator import google_key

# header for tricking amazon that 'it is not a robot'
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;     x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate",     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

# credentials for google translate API
client = service_account.Credentials.from_service_account_file(google_key)


### TRANSLATOR FUNCTION
def translate_to_polish(phrase):
    # translates from English to Polish for Allegro
    translation_client = translate_v2.Client(target_language='pl')
    result = translation_client.translate(phrase, source_language='eng')
 
    return result['translatedText']


### DEBUGGING FUNCTIONS
def print_to_file(data):
    # function for debugging reasons
    with open('search_data.txt', 'w') as filename:
        filename.write(data)


def print_results(result_json):
    # function for debugging reasons, not used in the app
    for i, item in enumerate(result_json):
        print(f'--- Item {i} ---')
        print(item['platform'])
        print(item['title'])
        print(item['link'])
        print(item['image'])
        print(item['price'])
        print()



### WEBSCRAPPING FUNCTIONS
def price_info_format(price_info_list):
    # changes the info list into the html format, ready for display
    for i, item in enumerate(price_info_list):
        if item.startswith('$') or item.endswith('zł'):
            price_info_list[i] = f'<span class="price"> {item}</span>'
    final_list = ' '.join(price_info_list)
    return final_list


def amazon_search(phrase):
# function for search at amazon

    source = requests.get(f'https://www.amazon.com/s?k={phrase}', headers=headers).text
    soup = BeautifulSoup(source, 'lxml')

    articles = soup.select('div[data-component-type="s-search-result"]')

    # these are class endings taht indicate the first price container (usually the lowest) or the secondar price containers
    priceholder_tags = ['small', 'mini'] 

    def compose_price_info(article, price_tags):
        price_final = []

        for info_tag in price_tags:
            # indicating cointainer for price info
            main_tag = article.find_all('div', class_=f'a-section a-spacing-none a-spacing-top-{info_tag}')

            # recognizing if this is the main container or the container for additional options
            if info_tag == 'small':
                priceholders = main_tag
            elif info_tag == 'mini' and len(main_tag) > 0:
                priceholders = main_tag[0].find_all('div', class_='a-row a-spacing-mini')
            else: 
                priceholders = [] # option for no additional info

            # adding elements of the info to the list
            for holder in priceholders:
                price_full = []
                h_title = holder.find('div', class_='a-row a-size-base a-color-base')
                if h_title:
                    h_title = h_title.text
                    h_title = h_title.strip()
                    if not h_title.startswith('$'):
                        price_full.append(h_title)
                price = holder.find('span', class_='a-offscreen')
                if price:
                    price_full.append(price.text)
                comments = holder.find('span', attrs={'dir': 'auto'})
                if comments:
                    price_full.append(comments.text)

                if len(price_final) == 0 or (len(price_full) > 1 and price_full[1].startswith('$')):
                    price_final.append(price_full)
                    
        return price_final

    def price_check(price_list):
        # check if if price has been included in the price description
        price_check = False
        for i, info_list in enumerate(price_list):
            for item in info_list:
                if item.startswith('$'):
                    price_check = True
                # remove "starts from" element from price description
                if item.lower().startswith('from'):
                    info_list.remove(item)
            # changing format of a sub-list to html-friendly with price
            price_list[i] = price_info_format(info_list)
        if not price_check:
            price_list.append('Price not given')
            # changing format of a sub-list to html-friendly with price
            for j, info_list2 in enumerate(price_list):
                if len(price_list) > 1:
                    price_list[j] = ''.join(info_list2)
        
        return price_list


    def amazon_search_json(html_element, price_tags):
    # main sub-function, compose list of objects - each object a search result
    # html_element is an element (list) for search from amazon, price_tags is a tag list for prices (primary and secondary)
        results = []
        if len(html_element) > 0:
            for i, article in enumerate(html_element):
                platform = 'amazon'
                title = article.h2.a.span.text
                link = 'https://www.amazon.com' + article.h2.a['href']
                image = article.img['src']

                price_info = compose_price_info(article, price_tags)
                price_updated = price_check(price_info)

                # the function returns list of dictionaries (quasi-JSON)
                results.append({'platform': platform, 'title': title, 'link': link, 'image':image, 'price': price_updated})

        return results
    # launch main subfucntion

    amazon_results = amazon_search_json(articles, priceholder_tags)
    return amazon_results


def ebay_search(phrase):
# function for search at ebay

    source = requests.get(f'https://www.ebay.pl/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={phrase}&_sacat=0', headers=headers).text
    soup = BeautifulSoup(source, 'lxml')
    
    def create_result_list(soup_obj):
        articles2 = soup_obj.find('ul', class_='srp-list')
        results_list = articles2.find_all('li', limit=15)

        # print_to_file(str(results_list))

        return results_list

    def create_result_json(html_results):
        
        results_json = []
        
        for i, item in enumerate(html_results):
            platform = 'ebay'
            title = item.img['alt']
            # h3.text.strip()
            link = item.a['href']
            image = item.find('div', class_='s-item__image-wrapper').img['src']
            price_info = []

            print(i, title)

            price_rawlist = item.find('span', class_="s-item__price").find_all('span')
            for i, element in enumerate(price_rawlist):
                formated_element =  element.text.strip()
                if len(formated_element) > 1:
                    price_info.append(formated_element)

            # double list and additional third element at the start necessary for parity with amazon results
            price_info.insert(0, 'Cena:')
            # eliminate doubles and change the list to a html-friendly format
            price_updated = [price_info_format(list(dict.fromkeys(price_info)))]

            
            # the function returns list of dictionaries (quasi-JSON)
            results_json.append({'platform': platform, 'title': title, 'link': link, 'image':image, 'price': price_updated})

        return results_json
    
    result_list = create_result_list(soup)
    result_ebay = create_result_json(result_list)

    print_results(result_ebay)

    return result_ebay


def allegro_search(phrase):
# function for search at allegro
    source = requests.get(f'https://allegro.pl/listing?string={phrase}', headers=headers).text
    soup = BeautifulSoup(source, 'lxml')

    def create_search_list(soup_obj):
        search_frame = soup_obj.find_all('section', class_="_9c44d_3pyzl")
        articles = []
        for item in search_frame:
            articles.extend(item.find_all('article'))

        return articles

    def create_search_json(raw_list):
        
        results_json = []

        for i, item in enumerate(raw_list):
            platform = 'allegro'
            title = item.h2.text.strip()
            link = item.a['href']

            # allegro sometimes gives two digfferent links for pictures, here the proper one is referred to
            if 'data-src' in item.a.img.attrs.keys():
                image = item.a.img['data-src']
            else:
                image = item.a.img['src']

            # composing price information, equivalent to the former two (two-dimensional list)
            price_info = ['Cena:']
            regular_price = item.find('div', class_='_9c44d_2K6FN').text
            price_info.append(regular_price)
            if item.find('div', class_='_9c44d_21XN-') != None:
                price_with_delivery = item.find('div', class_='_9c44d_21XN-').text
                price_info.append(price_with_delivery)
            
            # in case price is not given, such informtion is given
            if len(price_info) == 1:
                price_info.append('nie podano')

            # making the list two-dimensional (in accordance with ebay and amazon format)
            price_updated = [price_info_format(price_info)]

            # the function returns list of dictionaries (quasi-JSON)
            results_json.append({'platform': platform, 'title': title, 'link': link, 'image':image, 'price': price_updated})

        return results_json

    html_list = create_search_list(soup)
    allegro_results = create_search_json(html_list)

    return allegro_results


### DATABASE FUNCTIONS
def session_results(results):
    # limits the number of search results to 10 per platform
    ses_res = []
    platforms = ['amazon', 'ebay', 'allegro']

    for platform in platforms:
        i = 0
        for result in results:
            if i < 10 and result['platform'] == platform:
                ses_res.append(result)
                i += 1
    
    return ses_res


def create_id(searches):
    search_ids = []
    for search in searches:
        search_ids.append(search.id)
    for i in range(1, 20):
        if i not in search_ids:
            return i
