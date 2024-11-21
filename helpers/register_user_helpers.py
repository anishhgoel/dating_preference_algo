import os
from dotenv import load_dotenv
import pymongo
import requests
import cv2
import base64
from PIL import Image
import io
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from openai import OpenAI


load_dotenv()
cluster_uri = os.getenv('MONGODB_CLUSTER_URL')  # Create a new client and connect to the server
mongo_client = MongoClient(cluster_uri, server_api=ServerApi('1'))

#openai client
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#########################################################################################################
# Helper functions to register a user
#########################################################################################################
#Location details of user

def get_location_details():
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

def validate_choice(user_input, valid_options, field_name):
    user_input = user_input.lower().strip()
    valid_options_lower = [opt.lower() for opt in valid_options]
    while user_input not in valid_options_lower:
        print(f"\nInvalid {field_name}. Please choose from:")
        for option in valid_options:
            print(f"- {option}")
        user_input = input(f"Enter your {field_name}: ").lower().strip()
    
    return user_input


def parse_features_response(response_str):
    """
    Parses the OpenAI API response, handling markdown code blocks and cleaning the string
    """
    # Remove markdown code blocks if present
    clean_str = response_str.replace('```python', '').replace('```', '').strip()
    
    try:
        # Convert string to dictionary
        features = eval(clean_str)
        return features
    except:
        # Try cleaning up the string more aggressively if first attempt fails
        try:
            # Remove any whitespace and newlines
            clean_str = ''.join(clean_str.split())
            return eval(clean_str)
        except Exception as e:
            print(f"Error parsing features: {e}")
            return None

def capture_and_analyze_face():
    """
    Captures photo and analyzes it using OpenAI's Vision API with improved parsing
    """
    features = None
    window_name = 'Camera Preview - Press SPACE to capture, ESC to cancel'
    
    try:
        # For MacOS, use index 1
        cap = cv2.VideoCapture(1)
        
        if not cap.isOpened():
            print("Could not open camera. Please check camera permissions.")
            return None
            
        # Set camera properties for good quality
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Create window and set properties
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 640, 480)
        
        print("\nCamera initialized successfully!")
        print("Position yourself in front of the camera and press SPACE when ready")
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue
            
            # Add instructions to frame
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, 'Press SPACE to capture', (30, 50), font, 1, (255, 255, 255), 2)
            cv2.putText(frame, 'Press ESC to cancel', (30, 90), font, 1, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow(window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("Capture cancelled by user")
                return None
            elif key == 32:  # SPACE
                print("\nCapturing photo...")
                
                # Convert frame to base64
                _, buffer = cv2.imencode('.jpg', frame)
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                
                try:
                    print("Analyzing facial features...")
                    response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": """Analyze the person's facial features in this image. Return ONLY a Python dictionary in this exact format with no additional text or markdown formatting:
                                        {
                                            'eye_color': '[specific color, not unknown]',
                                            'hair_color': '[specific color]',
                                            'hair_style': '[description]',
                                            'facial_hair': '[description or none]',
                                            'eyebrows': '[description or none]',
                                            'face_shape': '[description or none]',
                                            'eye_shape': '[description or none]',
                                            'skin_tone': '[description or none]',
                                            'facial_features': '[description or none]',
                                            'eyelashes': '[description or none]',
                                            'nose': '[description or none]',
                                            'mouth': '[description or none]',
                                            'chin': '[description or none]',
                                            'cheeks': '[description or none]',
                                            'dimples': '[description or none]',
                                            'face_symmetry': '[description or none]',  
                                            'moles': '[description or none]',
                                            'forehead': '[description or none]',
                                            'jaw': '[description or none]',
                                            'distinctive_features': ['feature1', 'feature2', etc]
                                        }"""
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_base64}",
                                            "detail": "high"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=300
                    )
                    
                    features_str = response.choices[0].message.content.strip()
                    features = parse_features_response(features_str)
                    
                    if features:
                        print("\nFeatures extracted successfully!")
                        print("\nDetected features:")
                        for key, value in features.items():
                            print(f"{key.replace('_', ' ').title()}: {value}")
                            
                        # Validate and clean up features
                        if features.get('eye_color') == 'unknown':
                            print("\nCould not determine eye color clearly. Please specify:")
                            valid_colors = ['brown', 'blue', 'green', 'hazel', 'gray']
                            print("Valid options:", ', '.join(valid_colors))
                            while True:
                                eye_color = input("Enter eye color: ").lower()
                                if eye_color in valid_colors:
                                    features['eye_color'] = eye_color
                                    break
                                print("Please enter a valid eye color")
                        
                        if features.get('distinctive_features') == ['undefined']:
                            features['distinctive_features'] = []
                            print("\nAny distinctive features to add? (glasses, piercings, etc.)")
                            print("Enter features one by one (press Enter without text to finish):")
                            while True:
                                feature = input("Enter feature (or press Enter to finish): ").strip()
                                if not feature:
                                    break
                                features['distinctive_features'].append(feature)
                    else:
                        print("Could not parse facial features")
                        return None
                        
                except Exception as e:
                    print(f"Error analyzing image: {e}")
                    print("Please verify your OpenAI API key and model access.")
                    return None
                break
    
    except Exception as e:
        print(f"Camera error: {e}")
        return None
        
    finally:
        try:
            if cap is not None:
                cap.release()
            cv2.destroyAllWindows()
        except:
            pass
            
    return features


def update_user_features(user_id, features):
    """
    Updates the user document with physical features
    """
    if features is None:
        print("No features to update")
        return False
        
    try:
        result = mongo_client.db.users.update_one(
            {"_id": user_id},
            {"$set": {"physical_features": features}}
        )
        if result.modified_count > 0:
            print("\nPhysical features updated in database successfully!")
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating user features: {e}")
        return False


def get_match_preferences():
    """
    Gets user preferences for potential matches including physical features and hobbies
    """
    preferences = {}
    
    print("\n--- Physical Preferences ---")
    # Height preferences
    while True:
        try:
            min_height = input("Minimum height preferred (e.g., 5'8\" or press Enter to skip): ").strip()
            if not min_height:
                min_height = None
                break
            
            # Validate height format
            height_parts = min_height.replace('"', '').replace("'", ' ').split()
            if len(height_parts) == 2:
                feet = int(height_parts[0])
                inches = int(height_parts[1])
                if 4 <= feet <= 7 and 0 <= inches <= 11:
                    min_height = f"{feet}'{inches}\""
                    break
            print("Invalid height format. Please use format like 5'8\" or leave empty")
        except ValueError:
            print("Invalid height format. Please use format like 5'8\" or leave empty")
    
    # Physical feature preferences using GPT for natural language processing
    print("\nDescribe physical features you're looking for (e.g., hair color, eye color, build, etc.)")
    print("Feel free to write is regular sentences or language.")
    physical_description = input("Physical preferences: ")
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """Convert the physical preference description into a structured dictionary with these keys:
                    {
                        'hair_color': ['list of colors'],
                        'eye_color': ['list of colors'],
                        'hair_style': ['list of styles'],
                        'build': ['list of body types'],
                        'facial_features': ['list of features'],
                        'other_features': ['list of other preferences']
                    }
                    Only include keys where preferences are mentioned."""
                },
                {
                    "role": "user",
                    "content": physical_description
                }
            ],
            max_tokens=200,
            temperature=0
        )
        
        physical_preferences = eval(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Error processing physical preferences: {e}")
        physical_preferences = {'raw_description': physical_description}
    
    print("\n--- Hobby and Interest Preferences ---")
    print("Describe the interests and hobbies you'd like in a potential match")
    print("Feel free to write is regular sentences or language.")

    hobby_description = input("Hobby/Interest preferences: ")
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """Convert the hobby/interest preferences into a dictionary with these keys:
                    {
                        'required_hobbies': ['must-have activities'],
                        'preferred_hobbies': ['nice-to-have activities'],
                        'activity_level': 'active/moderate/relaxed',
                        'interests': ['list of interest areas']
                    }"""
                },
                {
                    "role": "user",
                    "content": hobby_description
                }
            ],
            max_tokens=200,
            temperature=0
        )
        
        hobby_preferences = eval(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Error processing hobby preferences: {e}")
        hobby_preferences = {'raw_description': hobby_description}
    
    # Combine all preferences
    preferences = {
        'height_preference': {
            'min_height': min_height
        },
        'physical_preferences': physical_preferences,
        'hobby_preferences': hobby_preferences
    }
    
    # Print processed preferences for confirmation
    print("\nYour Match Preferences:")
    print("\nHeight Requirement:", min_height if min_height else "No specific requirement")
    
    print("\nPhysical Preferences:")
    for key, value in physical_preferences.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\nHobby/Interest Preferences:")
    for key, value in hobby_preferences.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    return preferences