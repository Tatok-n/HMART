import openai
import csv
import pandas as pd

openai.api_key = "my api key but i dont want people to see it rn lol"

'''def analyze_personality(response):
    #Ask ChatGPT 
    prompt = (
        f"The user answered '{response}' to the question '{question}', determine the personality trait that comes from this response. You must choose something, you cannot say that it answers none"
        "Choose from: Adventurous, Eco-conscious, Luxury-loving, Practical, Tech-savvy, Show-off, or Performance-Oriented"
    )
    # Generates a response from ChatGPT
    try:
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50,
            temperature=0.7
        )
        #chooses the first response generated
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return "Unknown"

'''

''' CODE FOR PERSONALITY ANALYSIS
    trait_counts = {trait: 0 for trait in ["Adventurous", "Eco-conscious", "Luxury-loving", "Practical", "Tech-savvy", "Show-off"," Performance-Oriented" ]}
    for response in responses:
        trait = analyze_personality(response)
        print(
            f"The trait for this sentence is {trait}"
        )
        if trait in trait_counts:
            trait_counts[trait] +=1
    

    sorted_traits = sorted(trait_counts.items(), key = lambda x: x[1], reverse=True)
    top_traits = sorted_traits[:2]
    print(top_traits)
    '''



def ask_gpt():
    #Ask ChatGPT 
    prompt = (
        f"The user answered '{response}' to the question '{question}', determine the personality trait that comes from this response. You must choose something, you cannot say that it answers none"
        "Choose from: Adventurous, Eco-conscious, Luxury-loving, Practical, Tech-savvy, Show-off, or Performance-Oriented"
    )
    # Generates a response from ChatGPT
    try:
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50,
            temperature=0.7
        )
        #chooses the first response generated
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return "Unknown"

    
    


def is_full(dictionary, required_keys):
    #check if all the info we're looking for are present in the dictionary
    return all(key in dictionary and dictionary[key] not in [None, ""] for key in required_keys)


questions = {
    "new_or_used": "Are you looking for a new or used car?",
    "minimum_year": "What year does the car need to be at minimum?",
    "favorite_brand": "Do you have a favorite car brand or a specific manufacturer in mind?",
    "car_shape": "Would you prefer a sleek, sporty design or something more spacious like an SUV or sedan?",
    "door_preference": "Do you prefer a car with easy access, like a four-door sedan, or would a two-door coupe be more your style?",
    "color_preference": "Is there a specific color that catches your eye when you're looking for a car?",
    "interior_style": "When sitting inside a car, do you like a lighter, airy feel or something darker and more elegant?",
    "transmission_type": "Do you prefer a car that shifts gears manually, or are you more comfortable with automatic transmission?",
    "max_mileage": "What is the maximum mileage the car can have?",
    "budget": "What kind of budget are you thinking about for your car? Do you have a price range in mind?",
    "fuel_type": "Are you leaning toward an eco-friendly car (electric or hybrid) or prefer a traditional petrol/diesel vehicle?",
    "passenger_capacity": "How many people do you usually travel with? Do you need a car that fits the family or a smaller one for personal trips?"
}

required_keys = list(questions.keys()) #this will make the keys into a list to input to is_full function
user_answers = {}
while not is_full(user_answers, required_keys):
    for key, question in questions.items():
        # Skip if already answered
        if key in user_answers and user_answers[key] not in [None, ""]: # [None,""] notation is used to check if the dictionary has a NULL spot 
            continue

    conversation = [{"role": "system", "content": "You are a helpful car salesman chatbot. If the user responds off-topic, acknowledge their comment politely and guide them back to answering the question at hand."}]

    for question in questions:
        #track convo history and add to history
        conversation.append({"role": "user", "content": question})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
            max_tokens=100,
            temperature=0.7
        )
        chatbot_reply = response["choices"][0]["message"]["content"]
        print(chatbot_reply)

        user_input = input("Type here: ")
        conversation.append({"role": "assistant", "content": chatbot_reply})
        conversation.append({"role": "user", "content": user_input})

        # Check if the user's input is off-topic
        response_check = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation + [{"role": "user", "content": f"Is the response '{user_input}' relevant to the question '{question}'? Answer yes or no."}],
            max_tokens=10,
            temperature=0
        )
        relevance_check = response_check["choices"][0]["message"]["content"].strip().lower()

        if relevance_check == "no":
            # Acknowledge the off-topic response and provide a relevant reply
            conversation.append({"role": "assistant", "content": "Let me answer that for you!"})
            off_topic_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=conversation + [{"role": "user", "content": f"Reply directly to this off-topic comment: {user_input}"}],
                max_tokens=100,
                temperature=0.7
            )
            off_topic_reply = off_topic_response["choices"][0]["message"]["content"]
            print(off_topic_reply)

            # Add the off-topic reply to the conversation history
            conversation.append({"role": "assistant", "content": off_topic_reply})

            # Politely steer back to the original question
            conversation.append({"role": "assistant", "content": f"Now, going back to the question: {question}"})
            print(f"Now, going back to the question: {question}")
        user_answers[question] = user_input



print("Please wait while I give you the dealership's recommendations.")
print("Press the button to view the recommendations")
print(user_answers)
