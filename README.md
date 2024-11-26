# HMART
 HMART's submission for Codejam 14!



 ## How to run :
 This project is organized into a frontend in Flutter and a backend in python, both must be running in order to use the app

 ### Start backend :
To start the backend, navigate to the Chatbot.py file, and run :  ```flask --app Chatbot run```, note that you may run into issues for one of the following reasons :
- If you do not have an openai api key in the file, the code will not execute properly
- You may need to migrate to an older version of the openai package in python (run ```openai migrate```

### Start frontend :
Once the backend is running, the project can now parse HTTP requests from the frontend, find main.dart and run that file, note that you may need to install some flutter packages before running the file

 
