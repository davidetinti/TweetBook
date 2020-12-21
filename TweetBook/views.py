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
bearer_token = "YOUR_BEARER_TOKEN"
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
login_redirect_url = "YOUR_REDIRECT_URL"

# Render main page


def index(request):
    return render(request, "index.html")

# Render Vue Single File Components


def component(request, name):
    return render(request, "components/" + name)

def compose_search_url(request):
    keywords = urllib.parse.quote(request.GET.get("keywords"))
    retweets = request.GET.get("retweets") == "true"
    replies = request.GET.get("replies") == "true"
    user = urllib.parse.quote(request.GET.get("user"))
    location = request.GET.get("location")
    hashtag = urllib.parse.quote(request.GET.get("hashtag"))
    tag = urllib.parse.quote(request.GET.get("tag"))
    
    url = (
        "https://api.twitter.com/1.1/search/tweets.json?"
        + "result_type=recent&count=100&q="
        + ("" if (keywords == "") else keywords)
        + ("" if (user == "") else " from:" + user)
        + ("" if (hashtag == "") else " %23" + hashtag)
        + ("" if (tag == "") else " @" + tag)
        + ("" if (retweets) else " -filter:retweets")
        + ("" if (replies) else " -filter:replies")
        + ("" if (location == "") else " &geocode=" + location)
    )
    return url

def search(request):
    only_geolocated = request.GET.get("only_geolocated") == "true"

    url = compose_search_url(request)

    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    json_response = connect_to_endpoint(url, headers)
    if only_geolocated:
        return JsonResponse(check_geo_tweets(json_response))
    else:
        return JsonResponse(json_response)

def check_geo_tweets(initial_response):
        final_response = {
            "statuses": []
        }

        for index, tweet in enumerate(initial_response["statuses"]):
            if tweet["place"] and len(final_response["statuses"]) < 100:
                final_response["statuses"].append(tweet)

        if len(final_response["statuses"]) < 100 or not initial_response["search_metadata"]["next_results"]:
            new_url = "https://api.twitter.com/1.1/search/tweets.json" + \
                initial_response["search_metadata"]["next_results"]
            final_response["statuses"] = get_more_geo_tweets(final_response["statuses"], new_url)
        return final_response

def get_more_geo_tweets(array, url):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    new_tweets_found = connect_to_endpoint(url, headers)

    while len(array) < 100 and new_tweets_found["search_metadata"].get("next_results"):
        for index, tweet in enumerate(new_tweets_found["statuses"]):
            if tweet["place"] and len(array) < 100:
                array.append(tweet)
        url = "https://api.twitter.com/1.1/search/tweets.json" + \
            new_tweets_found["search_metadata"]["next_results"]
        new_tweets_found = connect_to_endpoint(url, headers)
    
    return array


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
    api = get_api_instance(access_token, access_token_secret)
    return JsonResponse(api.me()._json)


def get_api_instance(access_token, access_token_secret):
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
        keyword = request.GET.get("keywords")
        message = "Guarda i risultati della mia ricerca per " + \
            keyword + " su TweetBook #IngSw2020"
        filename = "tmp.jpg"

        # get API instance
        api = get_api_instance(access_token, access_token_secret)

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


gmail_user = 'GMAIL_ADDRESS'
gmail_password = 'GMAIL_PASSWORD'


def notify(request):
    receiver = request.GET.get("mail")
    sent_from = gmail_user
    to = [receiver]
    subject = 'Nuovi risultati su TweetBook'
    body = "Ci sono nuovi risulati nella ricerca"

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
