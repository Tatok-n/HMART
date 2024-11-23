import 'package:flutter/material.dart';
import 'dart:ui';

void main() {
  runApp(const MyApp());
}

double screenWidth = 0;
double screenHeight = 0;

Color gradientStartBot = Color.fromARGB(255, 153, 0, 255);
Color gradientEndBot = Color.fromARGB(255, 143, 45, 255);

Color gradientStartUser = Color.fromARGB(255, 255, 255, 255);
Color gradientEndUser = Color.fromARGB(255, 187, 187, 187);


class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    screenWidth = MediaQuery.of(context).size.width;
    screenHeight = MediaQuery.of(context).size.height;
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color.fromARGB(255, 100, 4, 255)),
        useMaterial3: true, 
      ),
      home: ChatScreen()
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

  void _sendMessage() {
    if (_controller.text.isNotEmpty) {
      setState(() {
        _messages.add(_controller.text);
        _isUserMsg.add(true);
        sendChat(_controller.text); //just for now :)
        _controller.clear();
      });
    }
    
  }

  void sendChat(String messageContent) {
    setState(() {
      _messages.add(messageContent);
      _isUserMsg.add(false);
    });
  }

  Widget bubble(String content, bool isUserMessage,index) {
    MainAxisAlignment alignment;
    Color bubbleColor;
    Color textColor;
    double position = index/_messages.length;


    if (isUserMessage) {
      alignment = MainAxisAlignment.end;
      bubbleColor = Color.lerp(gradientStartUser, gradientEndUser, position)!;
      textColor = Colors.black;

    } else {
      alignment = MainAxisAlignment.start;
       bubbleColor = Color.lerp(gradientStartBot, gradientStartBot, position)!;
       textColor = Colors.white;
    }
    return Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      mainAxisAlignment : alignment,
                      children: [Container(
                        constraints: BoxConstraints(
                          maxWidth: screenWidth*0.8
                        ),
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                        decoration: BoxDecoration(borderRadius: BorderRadius.circular(25),
                          color: bubbleColor,
                          border: Border.all(color: Color.fromARGB(255, 70, 0, 201)),
                          ),
                        child: Text(content,  style: TextStyle(color: textColor)))]
                    ),
                  );
  }

  @override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      title: Text('Chatbot'),
      flexibleSpace: Container(decoration: 
      BoxDecoration( gradient: LinearGradient( begin: Alignment.topRight, end: Alignment.bottomLeft, colors: <Color>[Colors.black, gradientStartBot, gradientEndBot]))),),
    body: Stack(
      children: [
        // Background (chat messages)
        Column(
          children: [
            // Messages List
            Expanded(
              child: Container(
                color: Colors.black,
                child: ListView.builder(
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    return bubble(_messages[index], _isUserMsg[index], index);
                  },
                ),
              ),
            ),
          ],
        ),

        Positioned(
          bottom: 8,
          left: 8,
          right: 8,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(25.0),
              child: BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 10.0, sigmaY: 10.0),
                child: Container(
                  padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(26.0),
                    border: Border.all(
                      color: Colors.white.withOpacity(0.3), 
                      width: 1.0,
                    ),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _controller,
                          decoration: InputDecoration(
                            hintText: 'Type a message',
                            border: InputBorder.none, 
                          ),
                          onEditingComplete: _sendMessage,
                          style: TextStyle(color: Colors.white),
                        ),
                      ),
                      IconButton(
                        icon: Icon(Icons.send, color: const Color.fromARGB(255, 153, 0, 255)),
                        onPressed: _sendMessage,
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
