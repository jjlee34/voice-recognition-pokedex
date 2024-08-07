import speech_recognition as sr
import boto3

from playsound import playsound
from pymongo import MongoClient
from difflib import SequenceMatcher

uri = "URI"
access_key = "access_key"
secret_key = "secret_key"

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

client = MongoClient(uri)
db = client.pokedex
pokemon_collection = db.pokemon_new

polly_client = boto3.Session(
    aws_access_key_id = access_key,
    aws_secret_access_key = secret_key,
    region_name = 'us-east-2'
).client('polly')

speech_recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Please say something..")
    said_text = speech_recognizer.listen(source)
    print("Thanks for saying something..")
    try:
        search_query = speech_recognizer.recognize_google(said_text)
    except:
        search_query = ""
        print("Could not recognize text sorry!")
    
print(f'You asked for: (search_query)')

results = pokemon_collection.aggregate(
    [
        {
            "$search": {
                "index": "search_by_name",
                "autocomplete": {
                    "query": search_query,
                    "path": "name",
                    "fuzzy": {
                        "prefixLength": 2
                    }
                }
            }
        }
    ]
)

results = list(results)
results.sort(
    key=lambda x: similar(x['name'], search_query),
    reverse=True
)

best_match = results[0]
print(best_match)

if best_match['entry']:
    formatted_text_with_entry = f"{best_match['name']}, {best_match['entry']}"
else:
    formatted_text_with_entry = ""

if len(best_match['types']) > 1:
    formatted_text_with_type = f"It's a {best_match['types'][0]} and {best_match['types'][1]} Pokemon."
else:
    formatted_text_with_type = f"It's a {best_match['types'][0]} Pokemon."

total_stats = best_match['total']
hp = best_match['hp']
attack = best_match['attack']
defense = best_match['defense']
sp_attack = best_match['sp_attack']
sp_defense = best_match['sp_defense']
speed = best_match['speed']
formatted_text_with_stats = f"Total: {total_stats}, HP: {hp}, Attack: {attack}, Defense: {defense}, Special Attack: {sp_attack}, Special Defense: {sp_defense}, Speed: {speed}"

full_entry_text = formatted_text_with_entry + "\n" + formatted_text_with_type + "\n" + formatted_text_with_stats

audio_response = polly_client.synthesize_speech(
    Text = full_entry_text,
    OutputFormat = 'mp3',
    VoiceId = 'Joanna'
)

file = open('entry.mp3', 'wb')
file.write(audio_response['AudioStream'].read())
file.close()

playsound('entry.mp3')