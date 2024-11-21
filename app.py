import os
from dotenv import load_dotenv
import pymongo
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from openai import OpenAI


load_dotenv()

#Connecting to Database
cluster_uri = os.getenv('MONGODB_CLUSTER_URL')  # Create a new client and connect to the server
mongo_client = MongoClient(cluster_uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    mongo_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

#openai client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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

def resolve_coordinates(city, region, country):
    api_key = os.getenv('LOCATIONIQ_API_KEY')
    location = f"{city}, {region}, {country}"
    url = f"https://us1.locationiq.com/v1/search.php?key={api_key}&q={location}&format=json"
    try:
        response = requests.get(url)
        data = response.json()[0]
        print(data['lat'], data['lon'])
        return data['lat'], data['lon']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
    


    

def validate_date(dob_input):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a date formatting assistant. Respond only with the date in YYYY-MM-DD format. If the date is invalid, respond with 'INVALID'."},
                {"role": "user", "content": f"Convert this date to YYYY-MM-DD format: {dob_input}"}
            ],
            max_tokens=20,
            temperature=0
        )
        standardized_date = response.choices[0].message.content.strip()
        return standardized_date
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

def validate_hobbies(hobbies_list):
    try:
        response = openai_client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role" : "system", "content": "You are a helpful assistant that standardizes a list of hobbies. You might receive a sentence or paragraph of someone telling what they like, respond only with the list of hobbies in the following format: ['hobby1', 'hobby2', 'hobby3'] and make sure each hobby is one word"},
                {"role" : "user", "content": f"Standardize this list of hobbies: {hobbies_list}. Return a comma seperated list"}
            ],
            max_tokens = 200,
            temperature = 0
        )
        standardized_hobbies = response.choices[0].message.content.strip()
        print(standardized_hobbies)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def register_user():
    # name
    name = input("Enter your name: ")
    # age
    while True:
        dob_input = input("Enter your date of birth (YYYY-MM-DD): ")
        dob = validate_date(dob_input)
        if dob:
            break

    # location
    location_details = get_location_details()
    print(f"Detected location : {location_details['city']},{location_details['region']}")
    change_location = input("Do you want to change your location? (yes/no)").lower()

    if change_location == "yes":
        city = input("Enter your city: ")
        region = input("Enter your region: ")
        country = input("Enter your country: ")
        location_details = {
            'city' : city,
            'region' : region,
            'country' : country,
            'loc' : resolve_coordinates(city, region, country)
        }    
    
    # gender
    Pronouns = input("Enter your pronouns: ")
    Gender = input("Enter your gender (Man/ Woman/ Non-binary): ").lower()
    Sexuality = input("Enter your sexual orientation (Straight/ Asexual/ Gay/ Lesbian/ Bisexual ): ").lower()
    Interested_in = input("I'm interested in (Men/ Women/ Nonbinary people/ Everyone): ").lower()

    # hobbies
    hobbies_input = input("Talk about your hobbies, interests and passions: ")
    hobbies = validate_hobbies(hobbies_input)

    user_data = {
        "name": name,
        "date_of_birth": dob,
        "location": {
            "city": location_details['city'],
            "region": location_details['region'],
            "country": location_details['country'],
            "coordinates": location_details['loc']
        },
        "pronouns": Pronouns,
        "gender": Gender,
        "sexual_orientation": Sexuality,
        "interested_in": Interested_in,
        "hobbies": hobbies
    }
    user_id = mongo_client.db.users.insert_one(user_data).inserted_id
    print(f"User {user_id} registered successfully!")
    print(user_data)



    







if __name__ == "__main__":
    register_user()