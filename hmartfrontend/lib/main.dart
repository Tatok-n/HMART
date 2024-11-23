import 'dart:math';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import 'dart:ui';

import 'package:hmartfrontend/apiCaller.dart';

void main() {
  runApp(const MyApp());
}


double screenWidth = 0;
double screenHeight = 0;

final player=AudioPlayer();

double _size1 = 24;
double _size2 = 20;
double _size3 = 18;

Color gradientStartBot = Color.fromARGB(255, 64, 0, 255);
Color gradientEndBot = Color.fromARGB(255, 143, 45, 255);

Color gradientStartUser = Color.fromARGB(255, 223, 189, 255);
Color gradientEndUser = Color.fromARGB(255, 255, 255, 255);

bool _SHREK= false;
Apicaller apicaller = Apicaller();

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
   final ScrollController _scrollController = ScrollController();

  void _sendMessage() async{
    String response = await apicaller.getResponseString(_controller.text);
    if (_controller.text.isNotEmpty) {
      setState(() {
        _messages.add(_controller.text);
        _isUserMsg.add(true);
        sendChat(response);
        _controller.clear();
          _scrollToBottom();
      });
    } 
  }



   void _scrollToBottom() {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: Duration(milliseconds: 300), // Smooth scrolling
        curve: Curves.easeOut,
      );
    
  }

  void sendChat(String messageContent) {
    setState(() {
      _messages.add(messageContent);
      _isUserMsg.add(false);
        _scrollToBottom();
    });
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

  Widget bubble(String content, bool isUserMessage,index) {
    MainAxisAlignment alignment;
    Color bubbleColor;
    Color textColor;
    
          double position = _messages.length > 1
      ? (index==(_messages.length-1) ? 0.0 : index / (_messages.length - 1).toDouble())
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
                      mainAxisAlignment : alignment,
                      children: [Container(
                        constraints: BoxConstraints(
                          maxWidth: screenWidth*0.8
                        ),
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                        decoration: BoxDecoration(borderRadius: BorderRadius.circular(25),
                          color: bubbleColor,
                          ),
                        child: Text(content,  style: TextStyle(color: textColor, fontSize: _size3)))]
                    ),
                  );
  }

  @override
Widget build(BuildContext context) {
  return Scaffold(
    appBar: AppBar(
      title: const Text('Chatbot'),
      flexibleSpace: Container(decoration: 
      BoxDecoration( gradient: LinearGradient( begin: Alignment.topRight, end: Alignment.bottomLeft, colors: <Color>[Colors.black,Colors.black, gradientStartBot, Color.fromARGB(255, 184, 122, 255)]))),),
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
                  controller: _scrollController,
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                         int length = _messages.length;
                          if (index== length-2 && _messages[index] == "shrek" ) 
                          {
                            _SHREK = true;
                            WidgetsBinding.instance.addPostFrameCallback((_) {
                            playShrek();
                            showShrek(context);
                            });
                            }
                         if (index == length-1) {
                             return Padding(
                               padding: const EdgeInsets.only(bottom: 200),
                               child: bubble(_messages[index], _isUserMsg[index], index),
                             );
                         } else {
                             return bubble(_messages[index], _isUserMsg[index], length-index);
                         }
                  }
                ),
              ),
            ), 
          ],
        ),
        //text box
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
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(26.0),
                    border: Border.all(
                      color: const Color.fromARGB(255, 244, 207, 255).withOpacity(0.3), 
                      width: 1.0,
                    ),
                  ),
                  //Text field
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _controller,
                          decoration: const InputDecoration(
                            hintText: 'Type a message',
                            border: InputBorder.none, 
                          ),
                          onEditingComplete: _sendMessage,
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),IconButton(
                        icon: const Icon(Icons.send, color: Color.fromARGB(255, 153, 0, 255)),
                        onPressed: () {
                          _sendMessage();
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
            fit: BoxFit.cover
          )
        ),
      ),
    );
  }
  }
