#!/usr/bin/env python3
import asyncio
import websockets
import requests
import json
import sys


def get_rules(rulesURL, headers):
    response = requests.get(
        rulesURL, headers=headers
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    return response.json()

def delete_all_rules(rulesURL, headers, rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        rulesURL, headers=headers, json=payload
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
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
    )

def change_stream_rules(query, rulesURL, headers):
    old_rules = get_rules(rulesURL, headers)
    delete_all_rules(rulesURL, headers, old_rules)
    set_rules(headers, query)

async def stamparoba(websocket, response):
    for response_line in response.iter_lines():
        await asyncio.sleep(0)
        if response_line:
            json_response = json.loads(response_line)
            await websocket.send(json.dumps(json_response, indent=4, sort_keys=True))

async def recvroba(websocket, rulesURL, headers):
    while True:
        newquery = await websocket.recv()
        change_stream_rules(query=newquery, rulesURL=rulesURL, headers=headers)
        print(get_rules(rulesURL, headers))

async def server(websocket, path):
    rulesURL = 'https://api.twitter.com/2/tweets/search/stream/rules'    
    BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAJl8JAEAAAAA3FoulEnY13I3OVgHvqHT4YcUgaQ%3DWqSmntxjhtu3eA0BvG5u6FmwvfoqmWZIETMhzBzghTuF6kwPWd'
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    streamURL = (
        'https://api.twitter.com/2/tweets/search/stream?'
        + "expansions=attachments.media_keys,author_id,geo.place_id"
        + "&tweet.fields=attachments,author_id,created_at,conversation_id,entities,geo,lang"
        + "&media.fields=preview_image_url,url"
        + "&user.fields=profile_image_url"
        + "&place.fields=contained_within,country,country_code,geo,name,place_type"
    )

    query = await websocket.recv()
    change_stream_rules(query=query, rulesURL=rulesURL, headers=headers)
    print(get_rules(rulesURL, headers))
    response = requests.get(streamURL, headers=headers, stream=True)

    await asyncio.gather(
        asyncio.create_task(recvroba(websocket, rulesURL, headers)),
        asyncio.create_task(stamparoba(websocket, response))
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: ./streamsearch.py <DESIRED PORT FOR WEBSOCKET CONNECTION>')
        exit()

    start_server = websockets.serve(server, "localhost", sys.argv[1])

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
