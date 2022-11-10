from twilio.rest import Client
import requests
import config

STOCK = "TSLA"

# STOCK price increase/decreases by 5% between yesterday and the day before yesterday.

alpha_parameters = {
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
    'symbol': STOCK,
    'interval': '60min',
    'apikey': config.alpha_apikey
}

alpha_response = requests.get('https://www.alphavantage.co/query', params=alpha_parameters)

alpha_data = alpha_response.json()

stock_data = alpha_data['Time Series (Daily)']

data_list = [value for (key, value) in stock_data.items()]

yesterday_date = data_list[0]['4. close']
before_yesterday_date = data_list[1]['4. close']

diff = float(yesterday_date) - float(before_yesterday_date)
diff = round(diff, 2)

percent = (diff / float(yesterday_date)) * 100
percent = round(percent, 2)

# get the first 3 news pieces for the COMPANY_NAME.

news_parameters = {
    'apiKey': config.news_api_key,
    'q': STOCK,
    'from': '2022-11-09',
    'sortBy': 'popularity'
}

news_response = requests.get('https://newsapi.org/v2/everything', news_parameters)
articles = news_response.json()["articles"]
three_articles = articles[:3]

if percent > 5:
    logo = '🔺'
elif percent < 5:
    logo = '🔻'

# Send a separate message with the percentage change and each article's title and description to your phone number.

formatted_articles = [f" {STOCK} {logo} {percent}% \nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]
client = Client(config.twilio_account_sid, config.twilio_auth_token)
if percent > 2 or percent < -2:
    print('Get News')
    for article in formatted_articles:
        message = client.messages \
                        .create(
                             body=article,
                             from_=config.twilio_phone_number,
                             to=config.my_own_number
                 )
        print(message.status)
