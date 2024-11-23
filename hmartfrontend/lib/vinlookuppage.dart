import 'package:flutter/material.dart';
import 'comparisonpage.dart'; // Import your comparison page
import 'package:http/http.dart' as http;
import 'dart:convert';

class VINLookupPage extends StatefulWidget {
  final String apiUrl;

  VINLookupPage({required this.apiUrl});

  @override
  _VINLookupPageState createState() => _VINLookupPageState();
}

class _VINLookupPageState extends State<VINLookupPage> {
  List<Product> products = [];
  bool isLoading = true;

  // Hardcoded VINs for testing
  List<String> vinList = [
    'A9FGFF8ST43CEFJ3Y', // Make sure this matches your CSV
    '3RCKVP1GRJK1F6A8A', // Replace with real VINs from your CSV
    'W0XGHYEYHC5PZWWHR'  // Replace with real VINs from your CSV
  ];

  @override
  void initState() {
    super.initState();
    fetchProducts();
  }

  Future<void> fetchProducts() async {
    try {
      List<Product> fetchedProducts = [];
      for (String vin in vinList) {
        // Make API call for each VIN
        final response = await http.get(Uri.parse('${widget.apiUrl}?vin=$vin'));
        if (response.statusCode == 200) {
          // Parse the JSON response
          final data = jsonDecode(response.body);
          // Convert to a Product object
          fetchedProducts.add(
            Product(
              name: '${data['Make'] ?? 'Unknown'} ${data['Model'] ?? ''}', // Combine Make and Model
              imageUrl: 'https://via.placeholder.com/150', // Placeholder image
              features: {
                'Year': data['Year']?.toString() ?? 'N/A',
                'Body': data['Body']?.toString() ?? 'N/A',
                'Passenger Capacity': data['PassengerCapacity']?.toString() ?? 'N/A',
                'Fuel Type': data['Fuel_Type']?.toString() ?? 'N/A',
                'Drivetrain': data['Drivetrain']?.toString() ?? 'N/A',
                'Transmission': data['Transmission_Description']?.toString() ?? 'N/A',
              },
              price: data['SellingPrice']?.toDouble() ?? 0.0, // Default to 0.0 if no price
            ),
          );
        } else {
          print('Error fetching data for VIN $vin: ${response.statusCode}');
        }
      }
      setState(() {
        products = fetchedProducts; // Update the products list
        isLoading = false; // Stop the loading spinner
      });
    } catch (e) {
      print('Error fetching VIN data: $e');
      setState(() {
        isLoading = false; // Stop the loading spinner in case of error
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (products.isEmpty) {
      return const Scaffold(
        body: Center(child: Text('No products found.')),
      );
    }

    return ProductComparisonPage(products: products);
  }
}
