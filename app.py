import os
from dotenv import load_dotenv
import pymongo
import requests
import cv2
import base64
import bcrypt
from PIL import Image
import io
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from openai import OpenAI
from helpers.register_user_helpers import *
from helpers.auth_manager import user_registration, login_user


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

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

#########################################################################################################
# Registerning a user
#########################################################################################################
def register_user():
    username = input("Choose a username: ")
    password = input("Choose a password: ")

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
    
    ethinicity = input("Enter your ethnicity: ")
    height = input("Enter your height (in ftin): ")


    # gender
    VALID_GENDERS = ["man", "woman", "non-binary"]
    VALID_SEXUALITIES = ["straight", "asexual", "gay", "lesbian", "bisexual"]
    VALID_INTERESTS = ["men", "women", "nonbinary people", "everyone"]

    Pronouns = input("Enter your pronouns: ")

    Gender = validate_choice(
        input("Enter your gender (Man/ Woman/ Non-binary): "),
        VALID_GENDERS,
        "gender"
    )

    Sexuality = validate_choice(
        input("Enter your sexual orientation (Straight/ Asexual/ Gay/ Lesbian/ Bisexual): "),
        VALID_SEXUALITIES,
        "sexual orientation"
    )

    Interested_in = validate_choice(
        input("I'm interested in (Men/ Women/ Nonbinary people/ Everyone): "),
        VALID_INTERESTS,
        "interest"
    )

    # hobbies
    hobbies_input = input("Talk about your hobbies, interests and passions: ")
    hobbies = validate_hobbies(hobbies_input)

    user_data = {
        "username": username,
        "name": name,
        "date_of_birth": dob,
        "Ethnicity": ethinicity,
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
    print("\nLet's understand what you're looking for in a potential match...")
    match_preferences = get_match_preferences()
    user_data['match_preferences'] = match_preferences
    
    add_photo = input("Would you like to add your facial features using photo analysis? (yes/no): ").lower()
    
    if add_photo == 'yes':
        print("\nPreparing camera...")
        features = capture_and_analyze_face()
        
        if features:
            user_data['features'] = features
        else:
            print("Failed to capture physical features")
    
    user_id = user_registration(username, password, user_data)
    if user_id:
        print(f"User {user_id} registered successfully!")
    else:
        print("Failed to register user.")



#########################################################################################################

def user_login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    user = login_user(username, password)
    if user:
        print("Login successful!")
        print(f"Hello, {user['name']}!")
        while True:
            print("\nMenu:")
            print("1. Edit Profile")
            print("2. Search for Other Profiles")
            print("3. Logout")
            choice = input("Enter your choice: ")

            if choice == '1':
                print("Editing profile...")
            elif choice == '2':
                print("Searching for other profiles...")
            elif choice == '3':
                print("Logging out...")
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("Login failed.")



if __name__ == "__main__":
    action = input("Do you want to register (r) or login (l)? ")
    if action.lower() == 'r':
        register_user()
    elif action.lower() == 'l':
        user_login()