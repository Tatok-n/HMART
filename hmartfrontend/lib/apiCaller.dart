import 'dart:developer';
import 'package:http/http.dart' as http;

const String baseUrl = 'http://localhost:5000';

class ApiCaller {
  // General method for POST requests
  Future<String?> postRequest(String path, {String? prompt}) async {
    try {
      final uri = Uri.parse('$baseUrl$path${prompt ?? ""}');
      log('POST Request URL: $uri');
      final response = await http.post(uri);

      if (response.statusCode == 200) {
        log('POST Response: ${response.body}');
        return response.body;
      } else {
        log('POST Error ${response.statusCode}: ${response.body}');
        return "Error: ${response.statusCode}";
      }
    } catch (e) {
      log('Exception in POST Request: $e');
      return null;
    }
  }

  // General method for GET requests
  Future<String?> getRequest(String path) async {
    try {
      final uri = Uri.parse('$baseUrl$path');
      log('GET Request URL: $uri');
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        log('GET Response: ${response.body}');
        return response.body;
      } else {
        log('GET Error ${response.statusCode}: ${response.body}');
        return "Error: ${response.statusCode}";
      }
    } catch (e) {
      log('Exception in GET Request: $e');
      return null;
    }
  }

  // Method to accept REST calls based on input
  Future<String> acceptRest(String prompt, String path) async {
    try {
      String? response;
      if (prompt.isNotEmpty) {
        response = await postRequest(path, prompt: prompt);
      } else {
        response = await getRequest(path);
      }

      if (response != null) {
        return response;
      } else {
        log('No response received');
        return "";
      }
    } catch (e) {
      log('Exception in acceptRest: $e');
      return "";
    }
  }

  // Specific response fetcher for prompts
  Future<String?> getResponse(String prompt) async {
    return postRequest('/prompt/', prompt: prompt);
  }

  // Wrapper to return a string response for a given prompt
  Future<String> getResponseString(String prompt) async {
    final response = await getResponse(prompt);
    return response ?? "";
  }
}
