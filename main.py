import os
import requests
from twilio.rest import Client


stock_key = os.environ.get("STOCK_API_KEY")
stock_url = "https://www.alphavantage.co/query"
stock_params = {
    "function" : "TIME_SERIES_DAILY",
    "symbol" : "GOOG",
    "apikey" : stock_key
}


response = requests.get(stock_url, params=stock_params)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]
stock_list = list(data.keys())

yesterday_date = stock_list[0]
prev_date = stock_list[1]

yesterday_closing_price = float(data[yesterday_date]["4. close"])
prev_closing_price = float(data[prev_date]["4. close"])

stocks_difference = round(yesterday_closing_price - prev_closing_price, 2)
stocks_percent = round(stocks_difference / yesterday_closing_price * 100, 2)

up_or_down = None
if stocks_difference >=0 :
    up_or_down = "🔺"
else:
    up_or_down = "🔻"

news_key = os.environ.get("NEWS_API_KEY")
news_url = "https://newsapi.org/v2/everything"
news_params = {
    "q": stock_params["symbol"],
    "from": yesterday_date,
    "sortBy": "popularity",
    "apikey": news_key
}

response = requests.get(news_url, params=news_params)
response.raise_for_status()
news_data = response.json()

news_headline = news_data["articles"][0]["title"]
news_link = news_data["articles"][0]["url"]

account_sid = os.environ.get("ACCOUNT_SID")
auth_token = os.environ.get("AUTH_TOKEN")

twilio_number = os.getenv("TWILIO_FROM_NUMBER")
my_number = os.getenv("MY_PHONE_NUMBER")
message = None

if abs(stocks_percent) >= 5:
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    from_= twilio_number,
    body=f"{stock_params['symbol']} {up_or_down} {stocks_percent}%.\nHeadline: {news_headline}\nLink: {news_link}",
    to= my_number,
    )

if message:
    print(message.status)
else:
    print("No alert sent")
