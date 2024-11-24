import 'dart:math';
import 'dart:ui';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import 'vinlookuppage.dart'; // Import the VINLookupPage
import 'package:hmartfrontend/apiCaller.dart'; // Import Apicaller

double screenWidth = 0;
double screenHeight = 0;

final player = AudioPlayer();

double _size1 = 24;
double _size2 = 20;
double _size3 = 18;

Color gradientStartBot = Color.fromARGB(255, 64, 0, 255);
Color gradientEndBot = Color.fromARGB(255, 143, 45, 255);

Color gradientStartUser = Color.fromARGB(255, 223, 189, 255);
Color gradientEndUser = Color.fromARGB(255, 255, 255, 255);

bool _SHREK = false;
Apicaller apicaller = Apicaller();
int questionCounter = 0;
bool quizReccomendation = false;

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    screenWidth = MediaQuery.of(context).size.width;
    screenHeight = MediaQuery.of(context).size.height;

    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
      fontFamily: 'Roboto', // Apply the custom font globally
      textTheme: TextTheme(
        bodyLarge: TextStyle(fontSize: 16, fontWeight: FontWeight.normal),
        bodyMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
        titleLarge: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
      ),
      colorScheme: ColorScheme.fromSeed(seedColor: Color.fromARGB(255, 100, 4, 255)),
      useMaterial3: true,
    ),
      home: ChatScreen(),
      routes: {
        '/vin-lookup': (context) => VINLookupPage(apiUrl: 'http://127.0.0.1:5000/vehicle'),
      },
    );
  }
}

class ChatScreen extends StatefulWidget {
  @override
  _ChatScreenState createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  List<String> _messages = [];
  List<bool> _isUserMsg = [];
  final ScrollController _scrollController = ScrollController();

     @override
   void initState() {
     _greet("Do you want to use our car recommendation software or would you like to tell me what type of car you are looking for?");
     super.initState();
     //firstResponse();
   }

  void _sendMessage(bool isUserMsg, String message) async {
    if (_controller.text.isNotEmpty || !isUserMsg) {
      setState(() {
        _messages.add(message);
        _isUserMsg.add(isUserMsg);
        _controller.clear();
        _scrollToBottom();
      });
    }
  }

  void _greet(String message) async {
    setState(() {
      _messages.add(message);
      _isUserMsg.add(false);
    });
  }

  void _scrollToBottom() {
    _scrollController.animateTo(
      _scrollController.position.maxScrollExtent,
      duration: Duration(milliseconds: 300),
      curve: Curves.easeOut,
    );
  }

  void processResponse(String messageContent) async {
    String response = "";
    String displayMsg = "";
    if (questionCounter == 0) { //if no questions have been asked before, then greet the user with the fisrt question
        response = await apicaller.acceptRest(messageContent, "/firstReply/");
        if (response == "1") {
          quizReccomendation = false;
          displayMsg = "There is a couple more information that I need before we can find you the right car. I will ask you some more questions to help filter the options ";
        } else {
          quizReccomendation = true;
          displayMsg = await apicaller.acceptRest("", "/firstQuestion/");
        }
        questionCounter++;
    } else { //otherwise accept user input and process
      displayMsg = await apicaller.acceptRest(messageContent, "/replies/");
    }

    _sendMessage(false, displayMsg);
  }

  void firstResponse() async {
    String response = await apicaller.acceptRest("", "http://localhost:5000/prompts/first");
    _greet(response);
  }

  void showShrek(BuildContext context) async {
    await showDialog(
      context: context,
      builder: (_) => ImagePrompt(),
    ).then((_) {
      _SHREK = false;
      player.stop();
    });
  }

  void playShrek() async {
    await player.play(AssetSource("sounds/580590_All-Star-8bit-Remix.mp3"));
  }

  Widget bubble(String content, bool isUserMessage, int index) {
    MainAxisAlignment alignment;
    Color bubbleColor;
    Color textColor;

    double position = _messages.length > 1
        ? (index == (_messages.length - 1) ? 0.0 : index / (_messages.length - 1).toDouble())
        : .0;

    if (isUserMessage) {
      alignment = MainAxisAlignment.end;
      bubbleColor = Color.lerp(gradientStartUser, gradientEndUser, position)!;
      textColor = const Color.fromARGB(255, 21, 0, 46);
    } else {
      alignment = MainAxisAlignment.start;
      bubbleColor = Color.lerp(gradientStartBot, gradientEndBot, position)!;
      textColor = const Color.fromARGB(255, 233, 213, 255);
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        mainAxisAlignment: alignment,
        children: [
          Container(
            constraints: BoxConstraints(maxWidth: screenWidth * 0.8),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(25),
              color: bubbleColor,
            ),
            child: Text(content, style: TextStyle(color: textColor, fontSize: _size3)),
          )
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Chatbot',
          style: TextStyle(color: Colors.white), // Customize the app bar title color
        ),
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topRight,
              end: Alignment.bottomLeft,
              colors: <Color>[
                Colors.black,
                Colors.black,
                gradientStartBot,
                Color.fromARGB(255, 184, 122, 255)
              ],
            ),
          ),
        ),
      ),
      body: Stack(
        children: [
          Column(
            children: [
              Expanded(
                child: Container(
                  color: Colors.black,
                  child: ListView.builder(
                    controller: _scrollController,
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      int length = _messages.length;
                      if (index == length - 2 && _messages[index] == "shrek") {
                        _SHREK = true;
                        WidgetsBinding.instance.addPostFrameCallback((_) {
                          playShrek();
                          showShrek(context);
                        });
                      }
                      if (index == length - 1) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 200),
                          child: bubble(_messages[index], _isUserMsg[index], index),
                        );
                      } else {
                        return bubble(_messages[index], _isUserMsg[index], length - index);
                      }
                    },
                  ),
                ),
              ),
            ],
          ),

          Positioned(
            bottom: 20, // Adjusted to make space for the new button
            left: 400,
            right: 400,
            child: SizedBox(
            width: 100, // Set desired width
            height: 50, // Set desired height
            child: ElevatedButton(
              onPressed: () {
                Navigator.pushNamed(context, '/vin-lookup');
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepPurple, // Button background color
                foregroundColor: Colors.white, // Button text color
                textStyle: TextStyle(
                  fontFamily: 'Roboto', // Apply custom font
                  fontSize: 18, // Font size
                  fontWeight: FontWeight.bold, // Optional: Make the text bold
                ),
              ),
              child: const Text('Select a Car'),
            ),
          )
          ),

          Positioned(
            bottom: 70,
            left: 8,
            right: 8,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(25.0),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 10.0, sigmaY: 10.0),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(26.0),
                      border: Border.all(
                        color: const Color.fromARGB(255, 244, 207, 255).withOpacity(0.3),
                        width: 1.0,
                      ),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: TextField(
                          controller: _controller,
                          decoration: const InputDecoration(
                            hintText: 'Type a message',
                            border: InputBorder.none,
                          ),
                          onEditingComplete: () {
                            String prompt = _controller.text;
                            _sendMessage(true, _controller.text);
                            processResponse(prompt);
                          },
                          style: const TextStyle(
                            fontFamily: 'Roboto', // Apply custom font
                            fontSize: 16, // Font size for input
                            color: Colors.white, // Input text color
                            controller: _controller,
                            decoration: const InputDecoration(
                              hintText: 'Type a message',
                              border: InputBorder.none,
                            ),
                            onEditingComplete: () {
                              String prompt = _controller.text;
                              _sendMessage(true, _controller.text);
                              processResponse(prompt);
                            },
                            style: const TextStyle(color: Color.fromARGB(255, 163, 110, 255)),
                          ),
                        ),

                        ),
                        IconButton(
                          icon: const Icon(Icons.send, color: Color.fromARGB(255, 153, 0, 255)),
                          onPressed: () {
                            String text = _controller.text;
                            _sendMessage(true, _controller.text);
                            processResponse(text);
                          },
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}


class ImagePrompt extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Container(
        width: 600,
        height: 600,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(26.0),
          image: DecorationImage(
            image: ExactAssetImage('assets/SUPER_SECRET_ASSET.png'),
            fit: BoxFit.cover,
          ),
        ),
      ),
    );
  }
}
