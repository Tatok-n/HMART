import json, os
import numpy as np
from openai import OpenAI
import pandas as pd
import csv
from flask_cors import CORS
from flask import Flask, request, jsonify

rules = {"Are you interested in a brand new car, a used car, or you don't mind?": ['new','used','None']}
conversation = [{"role": "system", "content": "You are a helpful car salesman chatbot. If the user responds off-topic, acknowledge their comment politely and guide them back to answering the question at hand."}]


specOptions = {}
user_spec_list = [None]*20
made_decision = False
main_conversation = []
spec_count = 0
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
    return user_spec_list

def get_yes_no(reply):
    global client, made_decision
    made_decision = True
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
    reply = request.view_args['reply']
    choice = get_yes_no(reply)
    jsonResponse = json.loads(choice)
    usingRecommendation = jsonResponse["interested"]
    start_conversation()
    return generateQuestion()


def generateQuestion() :
    global client, main_conversation, unknown_specs, specOptions

    current_spec = unknown_specs[0]
    prompt = (
        f"Your role is to ask a question to a user, as would an employee at a car delearship, to get them to chose a car, eventually, you are going to have to asked about all specs in {unknown_specs}, "
        f"but for now you need to ask about {current_spec}. There is no need to enumerate all the available options, just show what would be needed for the user to get an idea"
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
        f"Your role is to ask a help a user, as would an employee at a car delearship, and eventually get them to chose a car, however the customer needs an explanation as to what the current spec is."
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
    global user_spec_list, client, unknown_specs,specOptions,spec_count

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

    chatReply = response.choices[0].message.content.strip("'")

    if spec_count == 1 or spec_count == 5 or spec_count == 8 or spec_count == 15:
        chatReply = int(chatReply)
    else :
        chatReply = chatReply
    user_spec_list[spec_count] = chatReply
    print(user_spec_list)
    return chatReply

@app.route("/replies/<reply>", methods=["POST"])
def handleConverstaion(reply) :
    reply = request.view_args['reply']
    global main_conversation, client, unknown_specs, specOptions, usingRecommendation,spec_count, made_decision


    print("Current unknown specs are : ")
    print(unknown_specs)
    if not made_decision:
        usingRecommendation = get_yes_no(reply)


    if len(unknown_specs) == 0 :
        return "We hope you are happy with your choice"

    if (usingRecommendation):
        choice = checkRelevance(reply)
        print(choice)

        if (choice == 0) :
            matchSpecToList(reply)
            spec_count+=1
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
            "content": f"The user is currently being asked about {current_spec}, you should be able to differentiate if the user : gave a relevant response, seems to have made a choice to a particular option"
                       f",(having no preference is relevant), is unsure and needs clarification about {current_spec}, or is simply irrelevant."
                       f"If the response is relevant or the user displays any level of interest in an option, return 0 as an integer in the 'choice' member of a json object, 1 if clarifications are necessary, 2 if it is irrelevant."
                       f"Do not add anything that is not necessary, the user reply is : {user_reply}"
        }],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "relevance",
                "schema": {
                    "type": "object",
                    "properties": {
                        "choice": {
                            "description": "if the user response is relevant, unsure or in need of clarification",
                            "type": "integer"
                        },
                        "additionalProperties": False
                    }
                }
            }
        }

    )
    bot_reply = response.choices[0].message.content
    return json.loads(bot_reply)["choice"]


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
        specOptions["Body"] = [item for row in csv.reader(csvfile) for item in row]

    with open("capacity.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["PassengerCapacity"] = [item for row in csv.reader(csvfile) for item in row]

    with open("doors.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Doors"] = [item for row in csv.reader(csvfile) for item in row]

    with open("driveTrain.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Drivetrain"] = [item for row in csv.reader(csvfile) for item in row]

    with open("engineBlocks.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Engine_Block_Type"] = [item for row in csv.reader(csvfile) for item in row]

    with open("engineCylinders.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["EngineCylinders"] = [item for row in csv.reader(csvfile) for item in row]

    with open("engineDescs.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Engine_Description"] = [item for row in csv.reader(csvfile) for item in row]

    with open("extColors.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Ext_Color_Generic"] = [item for row in csv.reader(csvfile) for item in row]

    with open("fuels.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Fuel_Type"] = [item for row in csv.reader(csvfile) for item in row]

    with open("intColors.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Int_Color_Generic"] = [item for row in csv.reader(csvfile) for item in row]

    with open("makes.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Make"] = [item for row in csv.reader(csvfile) for item in row]

    with open("mileage.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Miles"] = [item for row in csv.reader(csvfile) for item in row]

    with open("mktClasses.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["MarketClass"] = [item for row in csv.reader(csvfile) for item in row]

    with open("models.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Model"] = [item for row in csv.reader(csvfile) for item in row]

    with open("Price.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["SellingPrice"] = [item for row in csv.reader(csvfile) for item in row]

    with open("transmissions.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Transmission"] = [item for row in csv.reader(csvfile) for item in row]

    with open("years.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["Year"] = [item for row in csv.reader(csvfile) for item in row]

    with open("cityMileage.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["CityMPG"] = [item for row in csv.reader(csvfile) for item in row]

    with open("highwayMileage.csv", newline='', encoding='utf-8') as csvfile :
        specOptions["HighwayMPG"] = [item for row in csv.reader(csvfile) for item in row]



    print(specOptions)


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
    app.run(debug=True)
    #start_conversation()
    print(specOptions["Body"])
    #firstPrompt("i am interested")







