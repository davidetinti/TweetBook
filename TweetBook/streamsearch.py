#!/usr/bin/env python3
import asyncio
import websockets
import requests
import json
import math

HTTP_PORT = 5000


def get_rules(rules_url, headers):
    response = requests.get(
        rules_url, headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(
                response.status_code, response.text)
        )
    return response.json()


def delete_all_rules(rules_url, headers, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        rules_url, headers=headers, json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )


def set_rules(headers, query):

    rules = [{"value": query}]
    payload = {"add": rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        headers=headers,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(
                response.status_code, response.text)
        )


def change_stream_rules(query, rules_url, headers):
    old_rules = get_rules(rules_url, headers)
    delete_all_rules(rules_url, headers, old_rules)
    set_rules(headers, query)


only_geo = False
place = False
lat = None
lng = None
rad = None
mult_factor = 0


async def transmit_tweet(websocket, response):
    for response_line in response.iter_lines():
        await asyncio.sleep(0)
        if response_line:
            json_response = json.loads(response_line)
            if json_response.get("data"):
                print("Found new Tweet with id #" + json_response["data"]["id"])
                if only_geo:
                    json_response = check_geo(json_response)
                if json_response and place:
                    json_response = check_place(json_response) if check_geo(json_response) else None
                if json_response:
                    await websocket.send(json.dumps(json_response, indent=4, sort_keys=True))
            else:
                print("There's an error with the response obtained")
                print(json_response)


def check_geo(tweet):
    places_presence = tweet["includes"].get("places")
    if (places_presence):
        return tweet
    else:
        return None


def check_place(tweet):
    coords = tweet["includes"]["places"][0]["geo"]["bbox"]
    tweet_lat = (coords[1] + coords[3]) / 2
    tweet_lng = (coords[0] + coords[2]) / 2
    raw_distance = math.sqrt(math.pow(tweet_lat - float(lat), 2) +
                         math.pow(tweet_lng - float(lng), 2))
    distance = raw_distance * mult_factor
    allowed_distance = float(rad)
    if distance < allowed_distance:
        return tweet
    else:
        return None


async def receive_rules(websocket, rules_url, headers):
    while True:
        newquery = await websocket.recv()
        change_stream_rules(query=newquery, rules_url=rules_url, headers=headers)
        print(get_rules(rules_url, headers))


async def server(websocket, path):
    global only_geo
    global place
    global lat
    global lng
    global rad
    global mult_factor
    rules_url = 'https://api.twitter.com/2/tweets/search/stream/rules'
    BEARER_TOKEN = 'YOUR_BEARER_TOKEN'
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    stream_url = (
        'https://api.twitter.com/2/tweets/search/stream?'
        + "expansions=attachments.media_keys,author_id,geo.place_id"
        + "&tweet.fields=attachments,author_id,created_at,conversation_id,entities,geo,lang"
        + "&media.fields=preview_image_url,url"
        + "&user.fields=profile_image_url"
        + "&place.fields=contained_within,country,country_code,geo,name,place_type"
    )

    full_query = await websocket.recv()
    extra_query_index = full_query.find("!EXTRA_TAG! ")
    query = full_query[:extra_query_index-1]
    extra_query = full_query[extra_query_index + 11:]
    if " -is:geo" in extra_query:
        extra_query = extra_query.replace(" -is:geo", "")
        only_geo = True
    else:
        only_geo = False
    if " location:" in extra_query:
        extra_query = extra_query.replace(" location:", "")
        place = True
        index = extra_query.find(",")
        lat = extra_query[:index]
        extra_query = extra_query[index+1:]
        index = extra_query.find(",")
        lng = extra_query[:index]
        if "mi" in extra_query:   
            extra_query = extra_query.replace("mi", "")
            mult_factor = 60
        elif "km" in extra_query:
            extra_query = extra_query.replace("km", "")
            mult_factor = 111
        rad = extra_query[index+1:]
    else:
        place = False
        lat, lng, rad = None, None, None
    change_stream_rules(query=query, rules_url=rules_url, headers=headers)
    print(get_rules(rules_url, headers))
    response = requests.get(stream_url, headers=headers, stream=True)

    try:
        await asyncio.gather(
            asyncio.create_task(receive_rules(websocket, rules_url, headers)),
            asyncio.create_task(transmit_tweet(websocket, response))
        )
    except websockets.exceptions.ConnectionClosed:
        pass


if __name__ == "__main__":
    start_server = websockets.serve(server, host="0.0.0.0", port=HTTP_PORT)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
