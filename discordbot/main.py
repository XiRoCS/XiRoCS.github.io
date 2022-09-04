import time

import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from requests_oauthlib import OAuth2Session
import json
import requests
from urllib import parse
import threading



TOKEN = 'MTAxNTc3MzYyNTg3NTQzNTU3MQ.GW3PqQ.PM1_x-nmZTe-5atFFgQJg6ZgUS8Ae9dEHyVtY8'
App_Id = '1015773625875435571'
Public_Key = '7571c6cb6b71c185888affb525e821381e408ec84421426b8c4bd9084f5a9b6d'
ServerIds = [820625137292279838, 846152423806599169]
BungieAPIKey = '8d566a1ee6b54cdc9f14b71fbd1bf8fb'
BungieClientId = 39841
BungieClientSecret = '83rwcWeukekCVsYGRjGej-bXRLqz6oIVuRjJcqE2x0U'
BungieAPIPath = 'https://www.bungie.net/Platform'


intents = nextcord.Intents.default()
intents.members = True

client = nextcord.Client(intents=intents)

base_auth_url = 'https://www.bungie.net/en/oauth/authorize/'
token_url = 'https://www.bungie.net/platform/app/oauth/token/'
redirect_url = 'https://xirocs.github.io/'


session = OAuth2Session(client_id=BungieClientId, redirect_uri=redirect_url)

auth_link = session.authorization_url(base_auth_url)
print(f"Auth Link: {auth_link[0]}")


redirect_response = input('Input: ')
query_def=parse.parse_qs(parse.urlparse(redirect_response).query)['code'][0]
initial = True
last_auth = 0


session.fetch_token(
    client_id = BungieClientId,
    client_secret= BungieClientSecret,
    token_url = token_url,
    authorization_response = redirect_response)


def refresh_token():
    while True:
        session_token_json = session.token
        session_refresh_token = session_token_json['refresh_token']
        session_duration = session_token_json['expires_in']
        time.sleep(session_duration)
        session.refresh_token(
            client_id=BungieClientId,
            client_secret=BungieClientSecret,
            token_url=token_url,
            refresh_token=session_refresh_token)

x = threading.Thread(target=(refresh_token),args =())
x.start()

def bungie_API_request(url):
    additional_headers = {'X-API-KEY': BungieAPIKey}
    response = session.get(url = url, headers = additional_headers)
    return response

response = bungie_API_request('https://www.bungie.net/Platform/User/GetCurrentBungieNetUser/')

def response_to_json(response):
    response_byte = str(response.content)
    response_text = response_byte.removeprefix("b'")
    response_text = response_text.removesuffix("'")
    response_json = json.loads(response_text)
    return response_json

def user_data():
    response = bungie_API_request('https://www.bungie.net/Platform/User/GetCurrentBungieNetUser/')

    bungiemembershipID = str(response_to_json(response)['Response']['membershipId'])

    bungiemembershipType = str(254)

    response = bungie_API_request(
        'https://www.bungie.net/Platform/Destiny2/' + bungiemembershipType + '/Profile/' + bungiemembershipID + '/LinkedProfiles/')

    d2membershipID = str(response_to_json(response)['Response']['profiles'][0]['membershipId'])
    d2membershipType = str(response_to_json(response)['Response']['profiles'][0]['membershipType'])

    response = bungie_API_request(
        'https://www.bungie.net/Platform/Destiny2/' + d2membershipType + '/Profile/' + d2membershipID + '/?components=200')

    character_ids = response_to_json(response)['Response']['characters']['data'].keys()
    return_json = {"bungiemembershipID": bungiemembershipID, "bungiemembershipType":bungiemembershipType, "d2membershipID": d2membershipID, "d2membershipType":d2membershipType, "character_ids": character_ids}
    return return_json

@client.slash_command(name = 'dailylostsector', description='Returns the legendary lost sector for today', guild_ids=ServerIds)
async def dailylostsector(interaction: Interaction):
    start_date = '02/09/2022'
    await interaction.response.defer()
    #need to do this manually as there is no API endpoint that returns this data

@client.slash_command(name = 'ada1mods', description='Returns the Mods Ada-1 has for sale today', guild_ids=ServerIds)
async def ada1mods(interaction: Interaction):
    await interaction.response.defer()
    user = user_data()
    character_id_list = user['character_ids']
    x = 0
    for i in character_id_list:
        if x < 1:
            character_id = i
            x += 1
        else:
            break
    response = bungie_API_request('https://www.bungie.net/Platform/Destiny2/'+user['d2membershipType']+'/Profile/'+user['d2membershipID']+'/Character/'+character_id+'/Vendors/?components=400')
    d2_vendor_groups = response_to_json(response)['Response']['vendorGroups']['data']['groups']
    d2_vendor_hashes = []
    for i in d2_vendor_groups:
        vendor_hashes = i['vendorHashes']
        for j in vendor_hashes:
            d2_vendor_hashes.append(j)


    d2_vendors_json = {}

    for i in d2_vendor_hashes:
        response = bungie_API_request('https://www.bungie.net/Platform/Destiny2/Manifest/DestinyVendorDefinition/'+str(i)+'/')
        d2_vendor_name = json.loads(response.content)['Response']['displayProperties']['name']
        d2_vendor_json = {i:d2_vendor_name}
        d2_vendors_json.update(d2_vendor_json)

    response = bungie_API_request('https://www.bungie.net/Platform/Destiny2/'+user['d2membershipType']+'/Profile/'+user['d2membershipID']+'/Character/'+character_id+'/Vendors/350061650/?components=402')
    d2_ada = response_to_json(response)
    d2_ada_inventory = d2_ada['Response']['sales']['data']
    d2_ada_inventory_keys = d2_ada_inventory.keys()

    d2_ada_items = []

    for i in d2_ada_inventory_keys:
        try:
            item = d2_ada_inventory[i]['itemHash']
            response = bungie_API_request('https://www.bungie.net/Platform/Destiny2/Manifest/DestinyInventoryItemDefinition/'+str(item)+'/')
            item_details = response_to_json(response)
            item_Description = str((item_details['Response']['itemTypeAndTierDisplayName']))
            Mod = "Mod"
            if (Mod in item_Description):
                d2_ada_items.append(item_details['Response']['displayProperties']['name'])
            else:

                pass
        except:
            pass
    discord_response = 'The Mods Ada-1 has for sale today are: '
    for i in d2_ada_items:
        discord_response += i+', '
    await interaction.followup.send(discord_response)

client.run(TOKEN)







