import requests, json

dollarAPI = 'http://api.nbp.pl/api/exchangerates/rates/A/USD/?format=json'
dollar_info = requests.get(dollarAPI)

print(json.loads(dollar_info.text)['rates'][0]['mid'])