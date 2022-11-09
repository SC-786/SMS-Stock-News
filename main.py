from twilio.rest import Client
import requests
import config

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

alpha_parameters = {
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
    'symbol': STOCK,
    'interval': '60min',
    'apikey': config.alpha_apikey
}

alpha_response = requests.get('https://www.alphavantage.co/query', params=alpha_parameters)

alpha_data = alpha_response.json()

stock_data = alpha_data['Time Series (Daily)']

# list_of_dates = list(stock_data.items())
# yesterday_date_format = (list_of_dates[0][0])
# before_yesterday_date_format = (list_of_dates[1][0])
data_list = [value for (key, value) in stock_data.items()]

yesterday_date_format = data_list[0]
yesterday_date = yesterday_date_format['4. close']
befo_yesterday_date = data_list[1]
before_yesterday_date = befo_yesterday_date['4. close']

# yesterday_date = stock_data[yesterday_date_format]['4. close']
# before_yesterday_date = stock_data[before_yesterday_date_format]['4. close']

diff = float(yesterday_date) - float(before_yesterday_date)
diff = round(diff, 2)

percent = (diff / float(yesterday_date)) * 100
percent = round(percent, 2)

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

news_parameters = {
    'apiKey': config.news_api_key,
    'q': STOCK,
    'from': '2022-11-09',
    'sortBy': 'popularity'
}

news_response = requests.get('https://newsapi.org/v2/everything', news_parameters)
articles = news_response.json()["articles"]
three_articles = articles[:3]

# news1_headline = news_response.json()['articles'][0]['title']
# news1_content = news_response.json()['articles'][0]['content']
# news2_headline = news_response.json()['articles'][1]['title']
# news2_content = news_response.json()['articles'][1]['content']
# news3_headline = news_response.json()['articles'][2]['title']
# news3_content = news_response.json()['articles'][2]['content']

if percent > 0:
    logo = '🔺'
elif percent < 0:
    logo = '🔻'

## STEP 3: Use https://www.twilio.com
# Send a separate message with the percentage change and each article's title and description to your phone number.


formatted_articles = [f" {STOCK} {logo} {percent}% \nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]
client = Client(config.twilio_account_sid, config.twilio_auth_token)
if percent > 2 or percent < -2:
    print('Get News')
    for article in formatted_articles:
        message = client.messages \
                        .create(
                             # body=f"{STOCK} {logo} {percent}%\n"
                             #      f"Headline: {news_response.json()['articles'][i]['title']}\n"
                             #      f"Brief: {news_response.json()['articles'][i]['content']}",
                             body=article,
                             from_= config.twilio_phone_number,
                             to=config.my_own_number
                 )
    print(message.status)