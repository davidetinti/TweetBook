from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import requests
import os
import json
from django.contrib.staticfiles.views import serve
import urllib
import asyncio
import websockets
import tweepy
from django.utils.crypto import get_random_string
import traceback
import smtplib

# Twitter OAuth parameters
bearer_token = "AAAAAAAAAAAAAAAAAAAAAMzfIgEAAAAAcYcSaUQX0eaJxXBw5SERUTyD610%3D1pKF18xmAtUPj7WBft8SOEjKvFerNUL5HXXyftdckFFYX5oi0K"
consumer_key = "tL4vposmnfl9yXP3ea8AFx6si"
consumer_secret = "dsxs9SGNCFWPr4cSxNEeUUGUgOSyaoA7vB2kq0dUo97ENaznvq"
login_redirect_url = "http://128.116.169.110:8000/home/loginDone/"

# Render main page


def index(request):
    return render(request, "index.html")

# Render Vue Single File Components


def component(request, name):
    return render(request, "components/" + name)


def search(request):
    keywords = urllib.parse.quote(request.GET.get("keywords"))
    retweets = request.GET.get("retweets") == "true"
    replies = request.GET.get("replies") == "true"
    only_geolocated = request.GET.get("only_geolocated") == "true"
    user = urllib.parse.quote(request.GET.get("user"))
    location = request.GET.get("location")
    hashtag = urllib.parse.quote(request.GET.get("hashtag"))
    tag = urllib.parse.quote(request.GET.get("tag"))

    url1 = (
        "https://api.twitter.com/1.1/search/tweets.json?"
        + "result_type=recent&count=100&q="
        + ("" if (keywords == "") else keywords)
        + ("" if (user == "") else "+from:" + user)
        + ("" if (hashtag == "") else "+%23" + hashtag)
        + ("" if (tag == "") else "+@" + tag)
        + ("" if (retweets) else "+-filter:retweets")
        + ("" if (replies) else "+-filter:replies")
        + ("" if (location == "") else "+&geocode=" + location)
    )

    url2 = (
        "https://api.twitter.com/2/tweets/search/recent?"
        + "expansions=attachments.media_keys,author_id,geo.place_id"
        + "&tweet.fields=attachments,author_id,created_at,conversation_id,entities,geo,lang"
        + "&media.fields=preview_image_url,url"
        + "&user.fields=profile_image_url"
        + "&place.fields=contained_within,country,country_code,geo,name,place_type"
        + "&max_results=100&query="
        + ("" if (keywords == "") else keywords)
        + ("" if (user == "") else " from:" + user)
        + ("" if (hashtag == "") else " #" + hashtag)
        + ("" if (tag == "") else " @" + tag)
        + ("" if (retweets) else " -is:retweet")
        + ("" if (replies) else " -is:reply")
        # manca location
    )

    # decide se verrà utilizzata l'API 1.1 (url1) o 2.0 (url2)
    url = url1

    print(url)

    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    json_response = connect_to_endpoint(url, headers)
    if only_geolocated:
        tweets_searched = {
            "statuses": []
        }

        for index, tweet in enumerate(json_response["statuses"]):
            if tweet["place"]:
                if len(tweets_searched["statuses"]) < 100:
                    tweets_searched["statuses"].append(tweet)

        if len(tweets_searched["statuses"]) < 100 or not json_response["search_metadata"]["next_results"]:
            new_url = "https://api.twitter.com/1.1/search/tweets.json" + \
                json_response["search_metadata"]["next_results"]
            search_new_tweets(tweets_searched["statuses"], new_url)
        return JsonResponse(tweets_searched)
    else:
        return JsonResponse(json_response)


def search_new_tweets(array, url):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    new_tweets_found = connect_to_endpoint(url, headers)
    while len(array) < 100 and new_tweets_found["search_metadata"].get("next_results"):
        for index, tweet in enumerate(new_tweets_found["statuses"]):
            if tweet["place"]:
                if len(array) < 100:
                    array.append(tweet)
        url = "https://api.twitter.com/1.1/search/tweets.json" + \
            new_tweets_found["search_metadata"]["next_results"]
        new_tweets_found = connect_to_endpoint(url, headers)


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


login_sessions = {}


def login_start(request):
    key = request.GET.get("key")
    auth = tweepy.OAuthHandler(
        consumer_key, consumer_secret, login_redirect_url + "?key=" + key)
    try:
        redirect_url = auth.get_authorization_url()
        login_sessions[key] = {
            'done': False,
            'access_token': None,
            'access_token_secret': None
        }
    except tweepy.TweepError:
        redirect_url = ""
        print('Error! Failed to get request token for login with key ' + key)
    return JsonResponse({'url': redirect_url, 'key': key})


def login_done(request):
    key = request.GET.get("key")
    oauth_token = request.GET.get("oauth_token")
    oauth_verifier = request.GET.get("oauth_verifier")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.request_token = {'oauth_token': oauth_token,
                          'oauth_token_secret':  oauth_verifier}
    auth.get_access_token(oauth_verifier)
    login_sessions[key]['done'] = True,
    login_sessions[key]['access_token'] = auth.access_token
    login_sessions[key]['access_token_secret'] = auth.access_token_secret
    return render(request, "loginPost.html")


def login_wait(request):
    key = request.GET.get("key")
    return JsonResponse(login_sessions[key])


def get_user_data(request):
    access_token = request.GET.get("access_token")
    access_token_secret = request.GET.get("access_token_secret")
    api = getAPIInstance(access_token, access_token_secret)
    return JsonResponse(api.me()._json)


def getAPIInstance(access_token, access_token_secret):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


def post_status(request):
    try:
        # get parameters
        access_token = request.GET.get("access_token")
        access_token_secret = request.GET.get("access_token_secret")
        map_url = request.GET.get("map_url")
        message = "Guarda i risultati della mia ricerca su TweetBook #IngSw2020"
        filename = "tmp.jpg"

        # get API instance
        api = getAPIInstance(access_token, access_token_secret)

        # fetch image from map_url
        request = requests.get(map_url, stream=True)

        # if request is ok
        if request.status_code == 200:
            # write in binary the content of request's chunks into filename (opened with the name 'image')
            with open(filename, 'wb') as image:
                for chunk in request:
                    image.write(chunk)

            api.update_with_media(filename, status=message)
            os.remove(filename)
        else:
            print("Unable to download image")
        return JsonResponse({"ok": True})
    except Exception:
        traceback.print_exc()
        return JsonResponse({"ok": False})




gmail_user = 'tweetbooknotify@gmail.com'
gmail_password = 'gruppo17swe'

def notify(request):
    receiver = request.GET.get("mail")
    sent_from = gmail_user
    to = [receiver]
    subject = 'Nuovi risultati su TweetBook'
    body = "Ciao"

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        print("Email sent!")
        return JsonResponse({"ok": True})
    except:
        print("Something went wrong...")
        return JsonResponse({"ok": False})
