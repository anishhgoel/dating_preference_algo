import os
from dotenv import load_dotenv
import pymongo
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from openai import OpenAI


load_dotenv()

#Connecting to Database
cluster_uri = os.getenv('MONGODB_URI')  # Create a new client and connect to the server
client = MongoClient(cluster_uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

#openai client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

#Location details of user

def get_location_details():
    name = input("Enter your name: ")
    ipinfo_token = os.getenv('IPINFO_TOKEN')
    response = requests.get(f'https://ipinfo.io/json?token={ipinfo_token}')
    data = response.json()
    location = {
        'city' : data['city'],
        'region' : data['region'],
        'country' : data['country'],
        'loc' : data['loc']
    }
    return location
if __name__ == "__main__":
    pass