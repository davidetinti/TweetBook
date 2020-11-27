from django.shortcuts import render
from TweetBook.models import Tweets
from django.http import JsonResponse
import requests
import os
import json
from django.contrib.staticfiles.views import serve
import urllib

# Development team beared token
bearer_token = "AAAAAAAAAAAAAAAAAAAAAMzfIgEAAAAAcYcSaUQX0eaJxXBw5SERUTyD610%3D1pKF18xmAtUPj7WBft8SOEjKvFerNUL5HXXyftdckFFYX5oi0K"

# Render main page
def index(request):
    """Site homepage"""
    # Render the index.html with the data in the context dictionary
    return render(request, "index.html")

# Render Vue Single File Components
def component(request, name):
    return render(request, "components/" + name)

def search(request):
    keywords = urllib.parse.quote(request.GET.get("keywords"))
    retweets = request.GET.get("retweets") == "true"
    replies = request.GET.get("replies") == "true"
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

    return JsonResponse(json_response)


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()
