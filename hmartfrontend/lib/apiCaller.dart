import 'dart:developer';

import 'package:http/http.dart' as http;

 String baseUrl = 'http://localhost:5000/';
 String promptUrl = 'prompt/';
 String responseUrl = 'response';






class Apicaller {
  Future<String?> getResponse(String prompt) async {
    try {
      var uri = Uri.parse(baseUrl + promptUrl + prompt);
      var response = await http.post(uri);
      if (response.statusCode == 200) {
        return response.body;
      } else {
        return "oopsie happened";
      }
    }  catch (e) {
    print(e.toString());
  }
    
  }


  Future<String> getResponseString(String prompt) 
    async { 
      String? response = await getResponse(prompt);
      if (response!=null) {
          return response;
      } else {
        return "";
      }
    }
    
  }
