#import Chatbot
from flask import Flask,request
app = Flask(__name__)

@app.route("/response", methods=["GET"])
def hello_world():
    #eventually link this to the ChatGPT controller
    return "Hello, World!"


@app.route("/prompt/<message>", methods=["POST"])
def prompt(message):
    prompt = request.view_args['message']
    if prompt == "hello":
        return "Hi there my good sir!"
    elif prompt == "shrek":
        return "SHREK SHREK SHREK SHREK SHREK SHREK SHREK SHREK SHREK SHREK "
    else :
        return "That is not very nice of you :C"
