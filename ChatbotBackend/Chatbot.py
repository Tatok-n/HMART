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
currentResponse = ""
chosenPath = 0


def printToReturn(string):
    return (string)



def recommendationController(userReply) :
    global questionCounter
    global questions
    global currentResponse
    currentResponse = userReply
    return ask_user_with_gpt(questions[questionCounter])



currentResponse = ""
@app.route("/firstReply/<reply>", methods=["POST"])
def firstPrompt(reply):
    global chosenPath
    response = request.view_args['reply']
    choice_of_model = (
        f"From the user's input {response} I want you to determine what there answer to the question: "
        "'Do you want to use our car recommendation software or would you like to tell me what type of car you are looking for?"
        " I want you to return an integer, return 0 if the user wants to use the recommendation software"
        "and return 1 if the user does not want to use the recommendation software."
        "Do not povide any additional explanation, text, or characters only return the integer.")
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
    noneCount = 0

    user_reply = request.view_args['reply']
    conversation.append({"role": "user", "content": user_reply})

    if (chosenPath == 0) : #user wants to use the recomendation software
        question = questions[probed_specs[questionCounter]]
        relevance = checkRelevance(user_reply, question)
        if relevance == "no" :
            return steerTowardsResponse(user_reply, question)
        else :
            DataCollected[probed_specs[questionCounter]] = user_reply
            questionCounter += 1
            if questionCounter < (len(questions[probed_specs[questionCounter]]) -1):
                conversation.append({"role": "assistant", "content": questions[probed_specs[questionCounter]]})
                return generateQuirkyQuestion()
            else:
                summarizeAnswers()
                return "Please wait while I find the best car for you"
    else :
        user_spec = currentResponse
        extractedList = []
        
        # this block will determine the specs that were not extracted from the user's prompt and get you a list of specs that were not scraped from user prommpt
        for i in range(0, len(probed_specs)):
            what_to_do = (
                f"The input from the user '{user_spec}' is their desired car description. I want you to look at the input and determine if the input has any information about '{probed_specs[i]}'"
                "If yes, then generate a one work answer that will cover the user's wants for that specific spec. If no information in the input is given for '{probed_specs[i]}', then set that element as None."
                "You must return a single word for every element. No comments are allowed.")
            extracted_info = ask_gpt(what_to_do)
            extractedList.append(extracted_info)

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

            if finalExtractedList[index] == "None":
                noneCount += 1 # used to count how many Nones we have 
                question = questions[probed_specs[index]]
                relevance = checkRelevance(user_reply, question)
                if relevance == "no":
                    return steerTowardsResponse(user_reply, question)
                else:
                    finalExtractedList[index] = user_reply
                    conversation.append({"role": "assistant", "content": question})
                    questionCounter += 1 

                    if noneCount < questionCounter:
                        conversation.append({"role": "assistant", "content": question})
                        return generateQuirkyQuestion()
                    else:
                        summarizeAnswers()
                        return "Please wait while I find the best car for you"

        



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



def ask_user_with_gpt(question):
    # Use OpenAI API to ask the user a question, handle off-topic responses, and circle back to the original question.
    global conversation
    conversation.append({"role": "assistant", "content": question})
    try:
        response = generateQuirkyQuestion()

        user_reply = currentResponse  # chat gpt response is the string at the ask and user_reply is user input
        conversation.append({"role": "user", "content": user_reply})

        # Check if the user's response is on-topic
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
        is_relevant = relevance_check_response["choices"][0]["message"]["content"].strip().lower()

        if is_relevant == "no":
            # Generate a polite response to the off-topic answer
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
            print(chatbot_reply_off_topic)  # ui display

            # ask the original question again
            return ask_user_with_gpt(question, conversation)

        # If the response is relevant, return it and add to history
        conversation.append({"role": "user", "content": user_reply})
        return user_reply

    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return "Error code "

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
                            "'What kind of budget are you thinking about for your car? Do you have a price range in mind?' the answer should be either 'veryLow','low','medium','high','veryHigh. Respect theses ranges: 'veryLow'=(0,10000), 'low'=(10001,25000),'medium'=(25001,50000),'high'=(500001,75000),'veryHigh'=(1000000,). If the user seems to not care how much the car will cost, then return as None."   ) 
        
        final_extraction_info = ask_gpt(summarize_answers)
        if final_extraction_info == "None":
            finalDataCollected.append(None)
        finalDataCollected.append(final_extraction_info)


    print(finalDataCollected) #for mathis
    print("Please wait while I search for the dealership's recommendations.")





# def recommendedAlgo():
#     global conversation
#     global probed_specs
#
#     required_specs = list(questions.keys())  # this will make the keys into a list to input to is_full function
#     user_answers = {}
#     while not is_full(user_answers, required_specs):
#         for key, question in questions.items():
#             # Skip if already answered
#             if key in user_answers and user_answers[key] not in [None, ""]:  # [None,""] notation is used to check if the dictionary has a NULL spot
#                 continue
#
#         for question in questions:
#             user_input_f = ask_user_with_gpt(question, conversation)
#             user_answers[question] = user_input_f
#
#
#     summarize_answers = (f" I have a dictionary of user input '{user_answers[question]}', to the question '{probed_specs[index]}' I gave them freedom to write in any format they want"
#                                        "Now you need to make the user_answers[question] a one word answer. If you determine that the user input does not care for that option, make the answer None."
#                                        " Your response must only contain the one-word or single-number answer, without any additional text, explanation, or comments.  Examples are below:"
#                                        "So: 'Are you looking for a new or used car?' the answer should be either new, used, or None"
#                                        "'What year does the car need to be at minimum?' the answer should be a year or None"
#                                        "'Do you have a favorite car brand or a specific manufacturer in mind?' the answer should be a car brand name, or None"
#                                        "'Would you prefer a sleek, sporty design or something more spacious like an SUV or sedan?' the answer should be SUV, Sedan, Coupe, or None"
#                                        "'Do you prefer a car with easy access, like a four-door sedan, or would a two-door coupe be more your style?' the answer should be 4,2, or None "
#                                        "'Is there a specific color that catches your eye when you're looking for a car?' the answer should return a color or None"
#                                        "'When sitting inside a car, do you like a lighter, airy feel or something darker and more elegant?' the answer should be light interior, dark interior or None"
#                                        "'Do you prefer a car that shifts gears manually, or are you more comfortable with automatic transmission?' the answer should be automatic, manual or None"
#                                        "'What is the maximum mileage the car can have?' the answer should be either 'veryLow','low','medium','high','veryHigh, or None. Respect theses ranges 'veryLow'=(0,20000), 'low'=(20001,40000),'medium'=(40001,60000),'high'=(60001,80000),'veryHigh'=(80001,). If the user seems to not care how much mileage the car should have, then return as None."
#                                        "'What kind of budget are you thinking about for your car? Do you have a price range in mind?' the answer should be either 'veryLow','low','medium','high','veryHigh. Respect theses ranges: 'veryLow'=(0,10000), 'low'=(10001,25000),'medium'=(25001,50000),'high'=(500001,75000),'veryHigh'=(1000000,). If the user seems to not care how much the car will cost, then return as None."
#                                        "'Are you leaning toward an eco-friendly car (electric or hybrid) or prefer a traditional petrol/diesel vehicle?' the answer should be electric, hybrid, fuel, diesel, or None "
#                                        "'How many people do you usually travel with? Do you need a car that fits the family or a smaller one for personal trips?' the answer should give a number or None")
#
#     final_extraction_info = ask_gpt(summarize_answers)
#     print(final_extraction_info)
#     print("Please wait while I search for the dealership's recommendations.")

def first_prompt():
    return (
        "Do you want to use our car recommendation software or would you like to tell me what type of car you are looking for?")


def is_full(dictionary, required_specs):
    # check if all the info we're looking for are present in the dictionary
    return all(key in dictionary and dictionary[key] not in [None, ""] for key in required_specs)


def tellUsCar(questions, probed_specs, conversation):
    user_spec = currentResponse
    what_to_do = (
    f"The input from the user '{user_spec}' is a car description. I want you to look at the input '{user_spec}' from the user and make an ordered list:"
    "[type,year, make, model, body, door, extColor, intColor, engineCylinder, transmission, engineBlock, engineDesc, fuel,driveTrain, mktClass, capacity, mileage, mpg, price]"
    " If you cannot determine one of these elements from the user input, then leave them as None."
    "The list must be made of one word for each element")

    # this block will determine the specs that were not extracted from the user's prompt and get you a list of specs that were not scraped from user prommpt
    final_extraction_info = ask_gpt(what_to_do)
    unfound_specs_index = []

    for i in range(len(final_extraction_info)):  # Using range to get indices
        if (final_extraction_info[i] == None):
            unfound_specs_index.append(i)

    # make sure probed_specs and final_extraction_info are the same size
    unfound_specs = []
    for i in unfound_specs_index:
        unfound_specs.append(probed_specs[i])  # Use append to add elements from probed_specs

    for spec in unfound_specs:
        if (spec in questions):
            question = questions[spec]
            conversation.append({"role": "assistant", "content": question})
            user_input = ask_user_with_gpt(question)
            conversation.append({"role": "user", "content": user_input})
            summarize_answers = (
                f" I have a user input '{user_input}', to the question '{question}' I gave them freedom to write in any format they want"
                "Now you need to make the user_input a one word or number answer. If you determine that the user input does not care for that option, make the answer None Examples are below:"
                "So: 'Are you looking for a new or used car?' the answer should be either new, used, or None"
                "'What year does the car need to be at minimum?' the answer should be a year or None"
                "'Do you have a favorite car brand or a specific manufacturer in mind?' the answer should be a car brand name, or None"
                "'Would you prefer a sleek, sporty design or something more spacious like an SUV or sedan?' the answer should be SUV, Sedan, Coupe, or None"
                "'Do you prefer a car with easy access, like a four-door sedan, or would a two-door coupe be more your style?' the answer should be 4,2, or None "
                "'Is there a specific color that catches your eye when you're looking for a car?' the answer should return a color or None"
                "'When sitting inside a car, do you like a lighter, airy feel or something darker and more elegant?' the answer should be light interior, dark interior or None"
                "'Do you prefer a car that shifts gears manually, or are you more comfortable with automatic transmission?' the answer should be automatic, manual or None"
                "'What is the maximum mileage the car can have?' the answer should be a number or None"
                "'What kind of budget are you thinking about for your car? Do you have a price range in mind?' the answer should be a number, range of numbers, or None"
                "'Are you leaning toward an eco-friendly car (electric or hybrid) or prefer a traditional petrol/diesel vehicle?' the answer should be electric, hybrid, fuel, diesel, or None "
                "'How many people do you usually travel with? Do you need a car that fits the family or a smaller one for personal trips?' the answer should give a number or None")
            final_form_Uinput = ask_gpt(summarize_answers)
            spec_index = probed_specs.index(spec)
            final_extraction_info[spec_index] = final_form_Uinput
            return question





















