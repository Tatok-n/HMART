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

  @override
  void initState() {
    super.initState();
    fetchProducts();
  }

  Future<void> fetchProducts() async {
  try {
    List<Product> fetchedProducts = [];

    // Fetch recommended VINs dynamically from the backend
    final vinResponse = await http.get(Uri.parse('${widget.apiUrl}/recommend'));
    if (vinResponse.statusCode == 200) {
      // Decode recommended VINs and match percentages
      final List<dynamic> recommendations = jsonDecode(vinResponse.body);

      // Fetch details for each VIN
      for (var recommendation in recommendations) {
        String vin = recommendation['VIN'];
        double matchPercentage = recommendation['matchPercentage'].toDouble();

        final response = await http.get(Uri.parse('${widget.apiUrl}/vehicle?vin=$vin'));
        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          fetchedProducts.add(
        Product(
          name: '${data['Make'] ?? 'Unknown'} ${data['Model'] ?? ''}',
          imageUrl: 'https://via.placeholder.com/150',
          features: {
            'Type': data['Type'] ?? 'N/A',
            'Stock': data['Stock'] ?? 'N/A',
            'VIN': data['VIN'] ?? 'N/A',
            'Year': data['Year']?.toString() ?? 'N/A',
            'Body': data['Body'] ?? 'N/A',
            'Doors': data['Doors']?.toString() ?? 'N/A',
            'Exterior Color': data['ExteriorColor'] ?? 'N/A',
            'Interior Color': data['InteriorColor'] ?? 'N/A',
            'Engine Cylinders': data['EngineCylinders']?.toString() ?? 'N/A',
            'Engine Displacement': data['EngineDisplacement']?.toString() ?? 'N/A',
            'Transmission': data['Transmission'] ?? 'N/A',
            'Miles': data['Miles']?.toString() ?? 'N/A',
            'Selling Price': data['SellingPrice']?.toString() ?? 'N/A',
            'MSRP': data['MSRP']?.toString() ?? 'N/A',
            'Drivetrain': data['Drivetrain'] ?? 'N/A',
            'Fuel Type': data['Fuel_Type'] ?? 'N/A',
            'City MPG': data['CityMPG']?.toString() ?? 'N/A',
            'Highway MPG': data['HighwayMPG']?.toString() ?? 'N/A',
            'Passenger Capacity': data['PassengerCapacity']?.toString() ?? 'N/A',
          },
          price: data['SellingPrice']?.toDouble() ?? 0.0,
          matchPercentage: recommendation['matchPercentage']?.toDouble() ?? 0.0,
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
    } else {
      print('Error fetching recommended VINs: ${vinResponse.statusCode}');
      setState(() {
        isLoading = false; // Stop loading spinner if no VINs fetched
      });
    }
  } catch (e) {
    print('Error fetching data: $e');
    setState(() {
      isLoading = false; // Stop loading spinner in case of error
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
        body: Center(child: Text('Cannot calculate a good recommendation at the moment. Please return to collect more info. ')),
      );
    }

    return ProductComparisonPage(products: products); // Pass products to the comparison page
  }
}
