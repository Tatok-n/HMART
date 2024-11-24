import openai

from flask import Flask, request

conversation = [{"role": "system", "content": "You are a helpful car salesman chatbot. If the user responds off-topic, acknowledge their comment politely and guide them back to answering the question at hand."}]

DataCollected ={}
finalDataCollected = []
finalExtractedList = []

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

probed_specs = [
   "type", "year", "make", "model", "body", "door", "extColor", "intColor",
   "engineCylinder", "transmission", "engineBlock", "engineDesc", "fuel",
   "driveTrain", "mktClass", "capacity", "mileage", "mpg", "price"
]


questionCounter = 0
app = Flask(__name__)
chosenPath = 0


def returnFinalExtractedData():
    global finalDataCollected
    return finalDataCollected


@app.route("/firstReply/<reply>", methods=["POST"])
def firstPrompt(reply):
    global chosenPath
    response = request.view_args['reply']
    choice_of_model = (
        f"From the user's input {response} I want you to determine what there answer to the question: "
        "'Do you want to use our car recommendation software or would you like to tell me what type of car you are looking for?"
        " I want you to return an integer, return 0 if the user wants to use the recommendation software"
        "and return 1 if the user does not want to use the recommendation software."
        "Do not povide any additional explanation, text, or characters only return the integer."
        "Do not give a sentemce, give a single digit response.")
    choice = ask_gpt(choice_of_model)
    chosenPath = int(choice)
    try:
          # Convert the string response to an integer
        return choice  # Return the integer value
    except ValueError:
        print(f"Unexpected response from GPT: {choice}")
        return -1

def generateQuirkyQuestion() :
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=100,
        temperature=0.7  # allows for creative answers
    )
    return response["choices"][0]["message"]["content"].strip()



@app.route("/firstQuestion/", methods=["GET"])
def firstQuestion() :
    global conversation
    global questions
    global probed_specs
    conversation.append({"role": "assistant", "content": questions[probed_specs[0]]})
    return generateQuirkyQuestion()

@app.route("/replies/<reply>", methods=["POST"])
def postReply(reply) :
    global conversation
    global questions
    global probed_specs
    global questionCounter
    global DataCollected
    global chosenPath
    global finalExtractedList
    global finalDataCollected
    

    user_reply = request.view_args['reply']
    conversation.append({"role": "user", "content": user_reply})

    if (chosenPath == 0) : #user wants to use the recomendation software, returns DataCollected
        question = questions[probed_specs[questionCounter]]
        relevance = checkRelevance(user_reply, question)
        if relevance == "no" :
            return steerTowardsResponse(user_reply, question)
        else :
            DataCollected[probed_specs[questionCounter]] = user_reply
            questionCounter += 1
            if questionCounter < (len(probed_specs) -1):
                conversation.append({"role": "assistant", "content": questions[probed_specs[questionCounter]]})
                return generateQuirkyQuestion()
            else:
                summarizeAnswers()
                return "Please wait while I find the best car for you"
    else : #returns finalExtractedList
        user_spec = user_reply
        extractedList = []
        
        # this block will determine the specs that were not extracted from the user's prompt and get you a list of specs that were not scraped from user prommpt
        for i in range(0, len(probed_specs)):
            what_to_do = (
                f"The input from the user '{user_spec}' is their desired car description. I want you to look at the input and determine if the input has any information about '{probed_specs[i]}'"
                f"If yes, then generate a one work answer that will cover the user's wants for that specific spec. If no information in the input is given for '{probed_specs[i]}', then set that element as None."
                "You must return a single word for every element. No comments are allowed.")
            extracted_info = ask_gpt(what_to_do)
            extractedList.append(extracted_info)
        print(extractedList)

        for index in range(0, len(extractedList)):
            summarize_answers = (f" I have a user input '{extractedList[index]}', to the spec of a car '{probed_specs[index]}' I gave them freedom to write in any format they want"
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
                question = questions[probed_specs[i]]
                response = ask_gpt(f"{question}. User said: {user_reply}")
                
                # Check if a valid response was received
                if response and response.lower() != "none":
                    finalExtractedList[i] = response
                    DataCollected[probed_specs[i]] = response
                else:
                    none_count += 1  # Track how many are still unanswered

        # Check if all "None" values are replaced
        if none_count == 0:
            summarizeAnswers()
            return "Please wait while I find the best car for you"  # All specs are filled

        # If there are still unanswered specs then ask the next missing one
        next_missing_index = finalExtractedList.index("None")
        next_question = questions[probed_specs[next_missing_index]]
        conversation.append({"role": "assistant", "content": next_question})
        return generateQuirkyQuestion()
    

        



def steerTowardsResponse(user_reply, question) :
    off_topic_response_prompt = (
        f"The user gave an off-topic answer: '{user_reply}'. "
        "Politely acknowledge their comment, provide a helpful or relevant reply, "
        f"and then steer the conversation back to the original question: '{question}'."
    )
    off_topic_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation + [{"role": "assistant", "content": off_topic_response_prompt}],
        max_tokens=100,
        temperature=0.7
    )
    chatbot_reply_off_topic = off_topic_response["choices"][0]["message"]["content"].strip()
    conversation.append({"role": "assistant", "content": chatbot_reply_off_topic})
    return chatbot_reply_off_topic


def checkRelevance(user_reply, question) :
    relevance_check_prompt = (
        f"The user answered: '{user_reply}' to the question: '{question}'. "
        "Is the response relevant to the question? Reply with 'yes' or 'no' only."
    )
    relevance_check_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation + [{"role": "assistant", "content": relevance_check_prompt}],
        max_tokens=10,
        temperature=0
    )
    return relevance_check_response["choices"][0]["message"]["content"].strip().lower()


def ask_gpt(string):
    # Ask ChatGPT
    prompt = f"'{string}'"

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use gpt-3.5-turbo
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.7
        )
        # Access the response safely
        return completion['choices'][0]['message']['content'].strip()
    except KeyError:
        print("Error: Invalid response format")
        return "Sorry, something went wrong."
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

def summarizeAnswers():
    global DataCollected
    global finalDataCollected

    for index, key in enumerate(DataCollected):
        summarize_answers = (f" I have a user input '{DataCollected[key]}', to the spec of a car '{probed_specs[index]}' I gave them freedom to write in any format they want"
                            "Now you need to make the user input a one word answer. If you determine that the user input does not care for that option, make the answer None."
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
                            "'What kind of budget are you thinking about for your car? Do you have a price range in mind?' the answer should be either 'veryLow','low','medium','high','veryHigh. Respect theses ranges: 'veryLow'=(0,10000), 'low'=(10001,25000),'medium'=(25001,50000),'high'=(500001,75000),'veryHigh'=(1000000,). If the user seems to not care how much the car will cost, then return as None."   ) 
        
        final_extraction_info = ask_gpt(summarize_answers)
        if final_extraction_info == "None":
            finalDataCollected.append(None)
        finalDataCollected.append(final_extraction_info)


    print(finalDataCollected) #for mathis
    print("Please wait while I search for the dealership's recommendations.")


















