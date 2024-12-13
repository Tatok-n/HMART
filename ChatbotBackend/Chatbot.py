import json, os
import numpy as np
from openai import OpenAI
import pandas as pd
import csv
from flask_cors import CORS
from flask import Flask, request, jsonify

rules = {"Are you interested in a brand new car, a used car, or you don't mind?": ['new','used','None']}
conversation = [{"role": "system", "content": "You are a helpful car salesman chatbot. If the user responds off-topic, acknowledge their comment politely and guide them back to answering the question at hand."}]

DataCollected ={}
finalDataCollected = []
finalExtractedList = []
specOptions = {}

user_spec_list = []

main_conversation = []

count =0

questions = {
    "type": "Do you want a new car, an older car, or it does not matter.",
    "year": "What year should the car be?",
    "make": "Do you have a specific make of car in mind?",
    "model": "Are you looking for a specific model of that make?",
    "body": "What type of body style do you prefer (e.g., sedan, hatchback, convertible)?",
    "door": "How many doors do you need on the car?",
    "extColor": "What exterior color do you prefer?",
    "intColor": "What interior color do you prefer?",
    "engineCylinder": "How many cylinders would you like the engine to have?",
    "transmission": "Do you prefer manual or automatic transmission?",
    "engineBlock": "What type of engine block would you prefer?",
    "engineDesc": "Do you have a preference for the engine description (e.g., turbo, hybrid)?",
    "fuel": "Do you have a preference for fuel type (e.g., petrol, diesel, electric)?",
    "driveTrain": "What type of drivetrain do you prefer (e.g., FWD, AWD, RWD)?",
    "mktClass": "What class of car are you looking for (e.g., luxury, economy)?",
    "capacity": "What is the required seating capacity?",
    "mileage": "What is the acceptable mileage range for the car?",
    "mpg": "What is the minimum miles per gallon (MPG) you'd like the car to have?",
    "price": "What is your price range for the car?"
}


unknown_specs = []


questionCounter = 0
app = Flask(__name__)
CORS(app)
usingRecommendation = False
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def reset_probed_specs() :
    global unknown_specs
    unknown_specs = [
    "Type", "Year", "Make", "Model", "Body", "Doors",
    "Ext_Color_Generic", "Int_Color_Generic", "EngineCylinders",
    "Transmission", "Engine_Block_Type", "Engine_Description",
    "Fuel_Type", "Drivetrain", "MarketClass", "PassengerCapacity",
    "Miles", "CityMPG", "HighwayMPG", "SellingPrice"
]

def returnFinalExtractedData():
    global finalDataCollected
    return finalDataCollected

def get_yes_no(reply):
    global client
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": f"From the user's input {reply} I want you to determine what there answer to the question: "
        "'Do you want to use our car recommendation software or would you like to tell me what type of car you are looking for?"
        " I want you to return a json response with a boolean 'interested' field that is a boolean, return true if the user wants to use the recommendation software"
        "and return false if the user does not want to use the recommendation software."
        "Provide nothing but the json"
        }],
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "yes_or_no",
            "schema": {
                "type": "object",
                "properties": {
                    "interested": {
                        "description": "if the user is interested or not",
                        "type": "boolean"
                    },
                    "additionalProperties": False
                }
            }
        }
    }
    )

    return response.choices[0].message.content

@app.route("/firstReply/<reply>", methods=["POST"])
def firstPrompt(reply):
    global usingRecommendation
    #reply = request.view_args['reply']
    choice = get_yes_no(reply)
    jsonResponse = json.loads(choice)
    usingRecommendation = jsonResponse["interested"]

def generateQuirkyQuestion() :
    global client
    response = client.chat.completions.create(
        model="gpt-4",
        messages=conversation,
        max_tokens=100,
        temperature=0.7  # allows for creative answers
    )
    return response["choices"][0]["message"]["content"].strip()

def generateQuestion() :
    global client, main_conversation, unknown_specs, specOptions

    current_spec = unknown_specs[0]
    prompt = (
        f"Your role is to ask a question to a user, as would an employee at a car delearship, to get them to chose a car, eventually, you are going to have to asked about all specs in {unknown_specs}, buf for now you need to ask about {current_spec}."
        f"You should return a question that should allow a user to make a choice between {specOptions[current_spec]}, and nothing else, be enthusiastic! Just as a nice dealer would be")


    message = {"role": "system","content": prompt}
    main_conversation.append(message)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=main_conversation,
        max_tokens=100,
        temperature=0.7  # allows for creative answers
    )

    return response.choices[0].message.content

def generateDefinition(currentSpec, options, reply) :
    global client, main_conversation

    prompt = (
        f"Your role is to ask a help a user, as would an employee at a car delearship, and eventually get them to chose a car, however the customer needs an explanation as to what {currentSpec} is."
        f"You should return a definition, or explanation that should allow a user to make a choice between {options}, and nothing else, be enthusiastic! Just as a nice dealer would be"
        f"By the way, the reply from the customer was {reply}")

    message = {"role": "system", "content": prompt}
    main_conversation.append(message)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=main_conversation,
        max_tokens=100,
        temperature=0.7
    )

    return response.choices[0].message.content

def steerBackOnTrack(currentSpec, options, reply) :
    global client, main_conversation

    prompt = (
        f"The user just replied {reply}, and is not relevant to the conversation to get them to pick a particular {currentSpec} among {options}."
        f"What you should do is entertain them a bit in your first half of your response, but steer them back on track in your second half"
        f"Remember, be enthusiastic! But keep it professional")

    message = {"role": "system", "content": prompt}
    main_conversation.append(message)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=main_conversation,
        max_tokens=250,
        temperature=0.8  # allows for creative answers
    )

    return response.choices[0].message.content

def matchSpecToList(customerInput) :
    global user_spec_list, client, unknown_specs,specOptions

    current_spec = unknown_specs[0]
    options = specOptions[current_spec]



    prompt = (f"Your role is to match a user's input one of the provided specs, as would an employee at a car delearship, you are going to be given a list of available options, amd you should pick whichever of the avaiable options most closely relates to what the user wants, if nothing matches, return an empty string"
              f"You should return nothing else, just the selected option. "
              f"The user input is : {customerInput}"
              f"The available options are : {options}")

    optional_extra = (f"additionally, for this spec return one of the following ['veryLow', 'low', 'medium', 'high', 'veryHigh'] instead of the available options, as it makes more sense, to map the given number to a range"
                   f", you are going to be given a dictionary with ranges that dictate with range it should go in, you must absolutely only return one of those 5 string values, the mappings are :")

    if current_spec == "Miles" :
        mileageRange = {"veryLow": (0, 20000), "low": (20001, 40000), "medium": (40001, 60000), "high": (60001, 80000),"veryHigh": (80001, float('inf'))}
        prompt += optional_extra
        prompt += f"{mileageRange}"
    elif current_spec == "CityMPG" :
        cityRange = {"veryLow": (0, 20), "low": (21, 40), "medium": (41, 60), "high": (61, 80),"veryHigh": (81, float('inf'))}
        prompt += optional_extra
        prompt += f"{cityRange}"
    elif current_spec == "HighwayMPG" :
        highwayRange = {"veryLow": (0, 25), "low": (26, 50), "medium": (51, 75), "high": (76, 100),"veryHigh": (101, float('inf'))}
        prompt += optional_extra
        prompt += f"{highwayRange}"
    elif current_spec == "SellingPrice" :
        priceRange = {"veryLow": (0, 10000), "low": (10001, 25000), "medium": (25001, 50000), "high": (50001, 75000),"veryHigh": (75001, float('inf'))}
        prompt += optional_extra
        prompt += f"{priceRange}"


    conversation = [{"role": "system","content": prompt}]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=conversation,
        max_tokens=100,
        temperature=0.7  # allows for creative answers
    )

    chatReply = response.choices[0].message.content.strip()
    user_spec_list.append(chatReply)
    return chatReply

@app.route("/firstQuestion/", methods=["GET"])
def firstQuestion() :
    global conversation
    global questions
    global unknown_specs
    conversation.append({"role": "assistant", "content": questions[unknown_specs[0]]})
    return generateQuirkyQuestion()

@app.route("/replies/<reply>", methods=["POST"])
def postReply(reply) :
    global conversation
    global questions
    global unknown_specs
    global questionCounter
    global DataCollected
    global usingRecommendation
    global finalExtractedList
    global finalDataCollected
    

    user_reply = request.view_args['reply']
    conversation.append({"role": "user", "content": user_reply})
    usingRecommendation = 0
    if usingRecommendation : #user wants to use the recomendation software, returns DataCollected
        question = questions[unknown_specs[questionCounter]]
        relevance = checkRelevance(user_reply, question)
        if relevance == "no" :
            return steerTowardsResponse(user_reply, question)
        else :
            DataCollected[unknown_specs[questionCounter]] = user_reply
            questionCounter += 1
            if questionCounter < (len(unknown_specs) -1):
                conversation.append({"role": "assistant", "content": questions[unknown_specs[questionCounter]]})
                return generateQuirkyQuestion()
            else:
                summarizeAnswers()
                return "Please wait while I find the best car for you"
    else : #returns finalExtractedList
        user_spec = user_reply
        extractedList = []
        
        # this block will determine the specs that were not extracted from the user's prompt and get you a list of specs that were not scraped from user prommpt
        for i in range(0, len(unknown_specs)):
            what_to_do = (
                f"The input from the user '{user_spec}' is their desired car description. I want you to look at the input and determine if the input has any information about '{unknown_specs[i]}'"
                f"If yes, then generate a one work answer that will cover the user's wants for that specific spec. If no information in the input is given for '{unknown_specs[i]}', then set that element as None."
                "You must return a single word for every element. No comments are allowed.")
            extracted_info = ask_gpt(what_to_do)
            extractedList.append(extracted_info)
        print(extractedList)

        for index in range(0, len(extractedList)):
            summarize_answers = (f" I have a user input '{extractedList[index]}', to the spec of a car '{unknown_specs[index]}' I gave them freedom to write in any format they want"
                            "Now you need to make the DataCollected[key] a one word answer. If you determine that the user input does not care for that option, make the answer None."
                            " Your response must only contain one-word, without any additional text, characters, explanation, or comments. You must return that response as a string.  Examples are below:"
                            f"So: 'Are you looking for a new or used car?' the answer should be either new, used, or None"
                            f"'What year does the car need to be at minimum?' the answer should be a year or None"
                            f"'Do you have a favorite car brand or a specific manufacturer in mind?' the answer should be a car brand name, or None"
                            f"'What model are you interested in, if any?' the answer should be a car model name, or None"
                            f"'What body type are you looking for? (e.g., sedan, SUV, truck)' the answer should be SUV, Sedan, Coupe, Truck, or None"
                            f"'Do you prefer a car with easy access, like a four-door sedan, or would a two-door coupe be more your style?' the answer should be 4, 2, or None"
                            f"'What exterior color are you looking for, if any?' the answer should return a color or None"
                            f"'What interior color do you prefer for the car?' the answer should be light interior, dark interior, or None"
                            f"'Do you prefer a car with a certain number of cylinders in the engine?' the answer should be a number (e.g., 4, 6, 8) or None"
                            f"'Do you want the car to have a specific engine description or configuration?' the answer should be an engine description (e.g., V6, I4) or None"
                            f"'What kind of transmission do you prefer? Automatic or manual?' the answer should be automatic, manual, or None"
                            f"'Do you have a preferred engine type, like petrol or diesel?' the answer should be electric, hybrid, fuel, diesel, or None"
                            f"'Do you have a preference for drivetrain type, such as front-wheel drive or all-wheel drive?' the answer should be FWD, AWD, RWD, or None"
                            f"'Are you looking for a specific market class, such as compact, luxury, or sports car?' the answer should be compact, luxury, or None"
                            f"'What is the minimum passenger capacity you need in the car?' the answer should be a number (e.g., 4, 5) or None"
                            f"'What is the maximum mileage the car can have?' the answer should be either 'veryLow','low','medium','high','veryHigh, or None. Respect theses ranges 'veryLow'=(0,20000), 'low'=(20001,40000),'medium'=(40001,60000),'high'=(60001,80000),'veryHigh'=(80001,). If the user seems to not care how much mileage the car should have, then return as None."
                            f"'What kind of fuel efficiency are you looking for in terms of miles per gallon?' the answer should be a number (e.g., 25 mpg) or None"
                            "'What kind of budget are you thinking about for your car? Do you have a price range in mind?' the answer should be either 'veryLow','low','medium','high','veryHigh. Respect theses ranges: 'veryLow'=(0,10000), 'low'=(10001,25000),'medium'=(25001,50000),'high'=(500001,75000),'veryHigh'=(1000000,). If the user seems to not care how much the car will cost, then return as None.") 
            final_extraction_info = ask_gpt(summarize_answers)
            finalExtractedList.append(final_extraction_info)

        none_count = 0
        for i in range(len(finalExtractedList)):
            if finalExtractedList[i] == "None":
                # Ask a question for the missing spec
                question = questions[unknown_specs[i]]
                response = ask_gpt(f"{question}. User said: {user_reply}")
                
                # Check if a valid response was received
                if response and response.lower() != "none":
                    finalExtractedList[i] = response
                    DataCollected[unknown_specs[i]] = response
                else:
                    none_count += 1  # Track how many are still unanswered

        # Check if all "None" values are replaced
        if none_count == 0:
            summarizeAnswers()
            return "Please wait while I find the best car for you"  # All specs are filled

        # If there are still unanswered specs then ask the next missing one
        next_missing_index = finalExtractedList.index("None")
        next_question = questions[unknown_specs[next_missing_index]]
        conversation.append({"role": "assistant", "content": next_question})
        return generateQuirkyQuestion()
    

def handleConverstaion(reply) :
    global main_conversation, client, unknown_specs, specOptions, usingRecommendation

    if len(unknown_specs) == 0 :
        return "We hope you are happy with your choice"
    if (usingRecommendation):
        choice = checkRelevance(reply)
        json_choice = json.load(choice)
        choice = json_choice["choice"]

        if (choice == 0) :
            matchSpecToList(reply)
            unknown_specs.pop(0)
            if len(unknown_specs) == 0:
                return "We hope you are happy with your choice"
            return generateQuestion()

        elif (choice == 1) :
            return generateDefinition(unknown_specs[0],specOptions[unknown_specs[0]],reply)

        elif (choice == 2) :
            return steerBackOnTrack(unknown_specs[0],specOptions[unknown_specs[0]],reply)






def steerTowardsResponse(user_reply, question) :
    global client
    off_topic_response_prompt = (
        f"The user gave an off-topic answer: '{user_reply}'. "
        "Politely acknowledge their comment, provide a helpful or relevant reply, "
        f"and then steer the conversation back to the original question: '{question}'."
    )
    off_topic_response = client.chat.completions.create(
        model="gpt-4",
        messages=conversation + [{"role": "assistant", "content": off_topic_response_prompt}],
        max_tokens=100,
        temperature=0.7
    )
    chatbot_reply_off_topic = off_topic_response["choices"][0]["message"]["content"].strip()
    conversation.append({"role": "assistant", "content": chatbot_reply_off_topic})
    return chatbot_reply_off_topic

# returns choice : 0 is relevant, 1 is needs a definition or 2 if conversation steering is needed
def checkRelevance(user_reply) :
    global client,unknown_specs

    current_spec = unknown_specs[0]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": f"The user is currently being asked about {current_spec}, you should be able to differentiate if the user : gave a relevant response (having no preference is relevant), is unsure and needs clarification about {current_spec}, or is simply irrelevant."
                       f"If the response is relevant, return 0 as an integer in the 'choice' member of a json object, 1 if clarifications are necessary, 2 if it is irrelevant."
                       f"Do not add anything that is not necessary, the user reply is : {user_reply}"
        }]

    )

    return response.choices[0].message.content

def ask_gpt(string):
    global client
    # Ask ChatGPT
    prompt = f"'{string}'"

    try:
        completion = client.chat.completions.create(
            model="gpt-4",  # Use gpt-4
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.7
        )
        # Access the response safely
        return completion["choices"][0]["message"]["content"].strip()
    except KeyError:
        print("Error: Invalid response format")
        return "Sorry, something went wrong."
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

def load_rules_from_csv(questions):
    
    csv_file_list = ['years.csv','makes.csv','models.csv','bodies.csv','doors.csv','extColors.csv','intColors.csv','engineCylinders.csv','engineDescs.csv','transmissions.csv','engineBlocks.csv','driveTrain.csv','mktClasses.csv','capacity.csv','mileage.csv','fuels.csv']
    global rules
  
    for i, question in enumerate(questions):
        file_path = csv_file_list[i]
        
        # Load options from the CSV file
        options = []
        with open(file_path, mode='r') as file:
            for line in file:
                option = line.strip()  # Remove whitespace and newlines
                if option:  # Skip empty lines
                    options.append(option)
        
        # Add "None" as a default option
        options.append("None")
        
        # Map the question to the options
        rules[question] = options

    return rules



def summarizeAnswers():
    global DataCollected
    global finalDataCollected
    load_rules_from_csv(questions)
    
    for index, key in enumerate(DataCollected):
        summarize_answers = (f" I have a user input '{DataCollected[key]}', to the spec of a car '{unknown_specs[index]}' I gave them freedom to write in any format they want"
                            "Now you need to make the DataCollected[key] a one word answer. If you determine that the user input does not care for that option, make the answer None."
                            " Your response must only contain one-word, without any additional text, characters, explanation, or comments. You must return that response as a string. "
                            f"The set of rules that you must use to know what to return is '{rules}'. So questions that are similar to the the keys from '{rules}' will use values from '{rules}' only."
                            f"You must also return for mileage:'veryLow','low','medium','high','veryHigh, or None. Respect theses ranges 'veryLow'=(0,20000), 'low'=(20001,40000),'medium'=(40001,60000),'high'=(60001,80000),'veryHigh'=(80001,). If the user seems to not care how much mileage the car should have, then return as 'None'. "
                            f"'What kind of fuel efficiency are you looking for in terms of miles per gallon?' the answer should be a number (e.g., 25 mpg) or None"
                            "'What kind of budget are you thinking about for your car? Do you have a price range in mind?' the answer should be either 'veryLow','low','medium','high','veryHigh. Respect theses ranges: 'veryLow'=(0,10000), 'low'=(10001,25000),'medium'=(25001,50000),'high'=(500001,75000),'veryHigh'=(1000000,). If the user seems to not care how much the car will cost, then return as None." 
                            f"You must also return for price:'veryLow','low','medium','high','veryHigh, or None. Respect theses ranges 'veryLow','low','medium','high','veryHigh. Respect theses ranges: 'veryLow'=(0,10000), 'low'=(10001,25000),'medium'=(25001,50000),'high'=(500001,75000),'veryHigh'=(1000000,). If the user seems to not care how much the car will cost, then return as None.") 
        final_extraction_info = ask_gpt(summarize_answers)
        if final_extraction_info == "None":
            finalDataCollected.append(None)
        finalDataCollected.append(final_extraction_info)

    print(finalDataCollected) #for mathis
    print("Please wait while I search for the dealership's recommendations.")





# File paths for data
CSV_DATA = "vehicles.csv"
JSON_DATA = "vehicles.json"

# Load the CSV file and create a hash map
def create_hash_map(file_path):
    df = pd.read_csv(file_path)
    # Replace NaN with None (to be converted to null in JSON)
    df = df.replace({np.nan: None})
    vin_hash_map = {}
    for _, row in df.iterrows():
        vin = row['VIN']
        vin_hash_map[vin] = row.to_dict()
    return vin_hash_map

vin_hash_map = create_hash_map(CSV_DATA)

# Recommendation Engine Functions
def increase_score(score, car):
    if car['VIN'] in score:
        score[car['VIN']] += 1
    else:
        score[car['VIN']] = 1

def filter_cars(car_data, filters):
    score = {}
    for car in car_data:
        for key, value in filters.items():
            car_value = car.get(key)
            if isinstance(value, tuple):
                if car_value is not None and value[0] <= car_value <= value[1]:
                    increase_score(score, car)
            elif car_value == value:
                increase_score(score, car)
    ranked_cars = sorted(car_data, key=lambda car: score.get(car['VIN'], 0), reverse=True)
    return ranked_cars, score

def recommend(features):
    mileageRange = {"veryLow": (0, 20000), "low": (20001, 40000), "medium": (40001, 60000), "high": (60001, 80000), "veryHigh": (80001, float('inf'))}
    cityRange = {"veryLow": (0, 20), "low": (21, 40), "medium": (41, 60), "high": (61, 80), "veryHigh": (81, float('inf'))}
    highwayRange = {"veryLow": (0, 25), "low": (26, 50), "medium": (51, 75), "high": (76, 100), "veryHigh": (101, float('inf'))}
    priceRange = {"veryLow": (0, 10000), "low": (10001, 25000), "medium": (25001, 50000), "high": (50001, 75000), "veryHigh": (75001, float('inf'))}

    with open(JSON_DATA, 'r') as file:
        car_data = json.load(file)

    filters = {}
    keys = [
        "Type", "Year", "Make", "Model", "Body", "Doors",
        "Ext_Color_Generic", "Int_Color_Generic", "EngineCylinders",
        "Transmission", "Engine_Block_Type", "Engine_Description",
        "Fuel_Type", "Drivetrain", "MarketClass", "PassengerCapacity",
        "Miles", "CityMPG", "HighwayMPG", "SellingPrice"
    ]
    ranges = {
        "Miles": mileageRange,
        "CityMPG": cityRange,
        "HighwayMPG": highwayRange,
        "SellingPrice": priceRange
    }
    intList = ["Year", "Doors", "EngineCylinders", "Miles", "SellingPrice", "CityMPG", "HighwayMPG", "PassengerCapacity"]
    filter_count = 0

    for idx, value in enumerate(features):
        if value is not None:
            filter_count += 1
            if keys[idx] in ranges:
                filters[keys[idx]] = ranges[keys[idx]].get(value, None)
            else:
                filters[keys[idx]] = int(value) if keys[idx] in intList else value

    recommended_cars, scores = filter_cars(car_data, filters)
    topCars = {}
    for car in recommended_cars[:6]:
        topCars[car['VIN']] = ((scores[car['VIN']] / filter_count) * 100)

    return topCars

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the VIN Lookup API! Use /vehicle?vin=<VIN_NUMBER> to search for a vehicle or /recommend to get car recommendations."})

@app.route('/vehicle', methods=['GET'])
def get_vehicle():
    vin = request.args.get('vin')
    if not vin:
        return jsonify({'error': 'VIN parameter is required'}), 400

    vehicle_info = vin_hash_map.get(vin, None)
    if vehicle_info:
        # Ensure all values in 'features' are strings
        vehicle_info['features'] = {key: str(value) for key, value in vehicle_info.items() if key != 'VIN'}
        return jsonify(vehicle_info)

    return jsonify({'error': 'Vehicle not found'}), 404

@app.route('/recommend', methods=['GET'])
def recommend_api():
    test_features = returnFinalExtractedData()  #['Used', None, 'Toyota', 'Yaris', None, None, None, None, None, None, None, None, None, None, None, None, None, None, '10000']
    recommendations = recommend(test_features)
    response = [{"VIN": vin, "matchPercentage": match_percentage} for vin, match_percentage in recommendations.items()]
    return jsonify(response)


def start_conversation():
    global specOptions, unknown_specs, main_conversation
    specOptions["Type"] = ["Used", "New"]

    with open("bodies.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Body"] = list(csv.reader(csvfile))

    with open("capacity.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["PassengerCapacity"] = list(csv.reader(csvfile))

    with open("doors.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Doors"] = list(csv.reader(csvfile))

    with open("driveTrain.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Drivetrain"] = list(csv.reader(csvfile))

    with open("engineBlocks.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Engine_Block_Type"] = list(csv.reader(csvfile))

    with open("engineCylinders.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["EngineCylinders"] = list(csv.reader(csvfile))

    with open("engineDescs.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Engine_Description"] = list(csv.reader(csvfile))

    with open("extColors.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Ext_Color_Generic"] = list(csv.reader(csvfile))

    with open("fuels.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Fuel_Type"] = list(csv.reader(csvfile))

    with open("intColors.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Int_Color_Generic"] = list(csv.reader(csvfile))

    with open("makes.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Make"] = list(csv.reader(csvfile))

    with open("mileage.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Miles"] = list(csv.reader(csvfile))

    with open("mktClasses.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["MarketClass"] = list(csv.reader(csvfile))

    with open("models.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Model"] = list(csv.reader(csvfile))

    with open("Price.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["SellingPrice"] = list(csv.reader(csvfile))

    with open("transmissions.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Transmission"] = list(csv.reader(csvfile))

    with open("years.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Year"] = list(csv.reader(csvfile))

    with open("cityMileage.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["CityMPG"] = list(csv.reader(csvfile))

    with open("highwayMileage.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["HighwayMPG"] = list(csv.reader(csvfile))


    reset_probed_specs()

    #setup the bot to answer to questions
    start_prompt = (
        f"You are going to be acting as a kind employee at a car dealership, you want to elicit particular specs out of a customer through a series of questions, someone else will make sure all the specs are correctly identified"
        f", but all you need to make sure to do is ask the correct sequence of questions, the specs themselves are {unknown_specs}")

    message = {"role": "system","content": start_prompt}
    main_conversation.append(message)

    client.chat.completions.create(
        model="gpt-4o",
        messages=main_conversation,
        max_tokens=100,
        temperature=0.7)





if __name__ == "__main__" :
    #app.run(debug=True)
    #firstPrompt("i am interested")
    start_conversation()
    print(unknown_specs[0])
    print(generateQuestion())







