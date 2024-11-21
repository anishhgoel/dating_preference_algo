import bcrypt
import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

#Connecting to Database
cluster_uri = os.getenv('MONGODB_CLUSTER_URL')  # Create a new client and connect to the server
mongo_client = MongoClient(cluster_uri, server_api=ServerApi('1'))


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def user_registration(username, password, user_data):
    hashed_password = hash_password(password)
    user_data.update({
        "username": username,
        "password": hashed_password
    })
    return mongo_client.db.users.insert_one(user_data).inserted_id

def login_user(username, password):
    user = mongo_client.db.users.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        print("Login successful!")
        return user
    else:
        print("Invalid username or password")
        return None