import time
import main 
import json
import os
from dotenv import load_dotenv

load_dotenv()

max_tweet_length = 280

twitter = main.make_token()
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
token_url = "https://api.twitter.com/2/oauth2/token"

data = main.load_token_from_file()

refreshed_token = twitter.refresh_token(
    client_id=client_id,
    client_secret=client_secret,
    token_url=token_url,
    refresh_token=data["refresh_token"],
)

main.save_token_to_file(refreshed_token)

def read_quotes_from_file(filename):
    with open(filename, "r", encoding="utf-8") as json_file:
        quotes_data = json.load(json_file)
    return quotes_data

def get_last_tweet_index(marker_file):
    try:
        with open(marker_file, "r") as file:
            index = int(file.read().strip())
            return index
    except FileNotFoundError:
        return -1

def update_last_tweet_index(marker_file, index):
    with open(marker_file, "w") as file:
        file.write(str(index))

def fetch_new_quote(quotes_data, last_tweet_index):
    total_quotes = len(quotes_data)
    next_tweet_index = (last_tweet_index + 1) % total_quotes
    new_quote = quotes_data[next_tweet_index]
    return new_quote, next_tweet_index


def split_quote_into_parts(quote, max_tweet_length):
    quote_parts = []
    current_part = ""
    words = quote.split()

    for word in words:
        if len(current_part) + len(word) + 1 <= max_tweet_length:
            current_part += word + " "
        else:
            quote_parts.append(current_part.strip())
            current_part = word + " "

    if current_part:
        quote_parts.append(current_part.strip())

    return quote_parts


def send_tweet(payload):
    res = main.post_tweet(payload, refreshed_token)
    return res.json()


def send_tweets_as_replies(quote_parts):
    if not quote_parts:
        return

    reply_to_tweet_id = None

    for _, part in enumerate(quote_parts):
        payload = {"text": part}
        if reply_to_tweet_id:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}

        res = send_tweet(payload)
        print(res)
        response_data = res.get("data", {})
        tweet_id = response_data.get("id")
        reply_to_tweet_id = tweet_id
        time.sleep(2)


quotes_data = read_quotes_from_file("quote.json")
marker_file = "last_tweet_index.txt"
last_tweet_index = get_last_tweet_index(marker_file)
new_quote, next_tweet_index = fetch_new_quote(quotes_data, last_tweet_index)
quote_parts = split_quote_into_parts(new_quote["quote"], max_tweet_length)
send_tweets_as_replies(quote_parts)
update_last_tweet_index(marker_file, next_tweet_index)
