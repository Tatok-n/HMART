import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

double screenWidth = 0;
double screenHeight = 0;

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



  Widget bubble(String content, bool isUserMessage) {
    MainAxisAlignment alignment;
    Color bubbleColor;
    if (isUserMessage) {
      alignment = MainAxisAlignment.end;
      bubbleColor = Colors.white;
    } else {
      alignment = MainAxisAlignment.start;
      bubbleColor = Color.fromARGB(255, 70, 0, 201);
    }
    return Padding(
                    padding: const EdgeInsets.all(4.0),
                    child: Row(
                      mainAxisAlignment : alignment,
                      children: [Container(
                        constraints: BoxConstraints(
                          maxWidth: screenWidth*0.6
                        ),
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                        decoration: BoxDecoration(borderRadius: BorderRadius.circular(25),
                          color: bubbleColor,
                          border: Border.all(color: Color.fromARGB(255, 70, 0, 201)),
                          ),
                        child: Text(content,  style: TextStyle(color: const Color.fromARGB(255, 0, 0, 0))))]
                    ),
                  );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Chatbot')),
      body: Column(
        children: [
          Expanded(
            child: Container(
              color: Color(0xFF000000),
              child: ListView.builder(
                itemCount: _messages.length,
                itemBuilder: (context, index) {
                  bool userMessage = _isUserMsg[index];
                  return bubble(_messages[index],_isUserMsg[index]);
                  }
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(hintText: 'Type a message'),
                    onEditingComplete: _sendMessage,
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.send),
                  onPressed: _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
