import 'dart:math';
import 'package:flutter/material.dart';

class Product {
  final String name;
  final String imageUrl;
  final Map<String, String> features;
  final double price;

  Product({
    required this.name,
    required this.imageUrl,
    required this.features,
    required this.price,
  });
}

class ProductComparisonPage extends StatefulWidget {
  final List<Product> products;

  ProductComparisonPage({required this.products});

  @override
  _ProductComparisonPageState createState() => _ProductComparisonPageState();
}

class _ProductComparisonPageState extends State<ProductComparisonPage> {
  int? selectedProductIndex; // Track the selected product
  bool pageLoaded = false; // Track if the page is loaded for initial animation

  final Color cardColor = Color(0xFF1E1E1E).withOpacity(0.9);
  final Color textColor = Colors.white;
  final Color secondaryTextColor = Colors.white70;

  @override
  void initState() {
    super.initState();
    // Trigger the animation when the page loads
    Future.delayed(Duration(milliseconds: 200), () {
      setState(() {
        pageLoaded = true;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    // Collect all unique features from all products
    final Set<String> allFeatures = {};
    for (var product in widget.products) {
      allFeatures.addAll(product.features.keys);
    }

    return Scaffold(
      backgroundColor: Colors.transparent,
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: Text(
          'Vehicle Comparison',
          style: TextStyle(color: textColor, fontSize: 35),
        ),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Stack(
        children: [
          // Background Image
          Container(
            width: MediaQuery.of(context).size.width,
            height: MediaQuery.of(context).size.height,
            decoration: const BoxDecoration(
              image: DecorationImage(
                image: AssetImage('images/galaxy4.jpg'),
                fit: BoxFit.cover,
              ),
            ),
          ),
          // Main Content
          SingleChildScrollView(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 80, left: 16, right: 16, bottom: 16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: widget.products.asMap().entries.map((entry) {
                      int index = entry.key;
                      Product product = entry.value;

                      bool isSelected = selectedProductIndex == index;

                      return Expanded(
                        flex: isSelected ? 3 : 2, // Adjust flex based on selection
                        child: TweenAnimationBuilder<double>(
                          duration: const Duration(milliseconds: 800),
                          tween: Tween<double>(begin: 0, end: pageLoaded ? 1 : 0),
                          curve: Curves.easeInOut,
                          builder: (context, value, child) {
                            return Opacity(
                              opacity: value,
                              child: Transform.translate(
                                offset: Offset(0, 50 * (1 - value)),
                                child: GestureDetector(
                                  onTap: () {
                                    setState(() {
                                      selectedProductIndex = index; // Update selected product
                                    });
                                  },
                                  child: AnimatedContainer(
                                    duration: const Duration(milliseconds: 500),
                                    curve: Curves.easeInOut,
                                    margin: EdgeInsets.all(isSelected ? 8 : 16),
                                    decoration: BoxDecoration(
                                      color: cardColor,
                                      borderRadius: BorderRadius.circular(15),
                                      border: Border.all(
                                        color: isSelected ? Colors.blueAccent : Colors.white.withOpacity(0.3),
                                        width: isSelected ? 2 : 1,
                                      ),
                                      boxShadow: isSelected
                                          ? [
                                              BoxShadow(
                                                color: Colors.blueAccent.withOpacity(0.4),
                                                blurRadius: 10,
                                                spreadRadius: 2,
                                              )
                                            ]
                                          : [],
                                    ),
                                    child: Padding(
                                      padding: const EdgeInsets.all(12.0),
                                      child: Column(
                                        children: [
                                          Container(
                                            decoration: BoxDecoration(
                                              borderRadius: BorderRadius.circular(12),
                                              boxShadow: [
                                                BoxShadow(
                                                  color: Colors.black.withOpacity(0.3),
                                                  blurRadius: 10,
                                                  spreadRadius: 2,
                                                ),
                                              ],
                                            ),
                                            child: ClipRRect(
                                              borderRadius: BorderRadius.circular(12),
                                              child: Image.network(
                                                product.imageUrl,
                                                height: isSelected ? 150 : 120, // Grow image size
                                                fit: BoxFit.contain,
                                              ),
                                            ),
                                          ),
                                          const SizedBox(height: 12),
                                          Text(
                                            product.name,
                                            style: TextStyle(
                                              color: textColor,
                                              fontWeight: FontWeight.bold,
                                              fontSize: isSelected ? 20 : 18, // Adjust text size
                                            ),
                                            textAlign: TextAlign.center,
                                          ),
                                          const SizedBox(height: 8),
                                          Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 12,
                                              vertical: 6,
                                            ),
                                            decoration: BoxDecoration(
                                              color: Colors.black54,
                                              borderRadius: BorderRadius.circular(20),
                                              boxShadow: [
                                                BoxShadow(
                                                  color: Colors.black.withOpacity(0.3),
                                                  blurRadius: 8,
                                                  offset: const Offset(0, 2),
                                                ),
                                              ],
                                            ),
                                            child: Text(
                                              '\$${product.price.toStringAsFixed(2)}',
                                              style: TextStyle(
                                                color: textColor,
                                                fontWeight: FontWeight.bold,
                                                fontSize: isSelected ? 18 : 16, // Adjust price font size
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                      );
                    }).toList(),
                  ),
                ),
                // Feature Comparison Table
                TweenAnimationBuilder<double>(
                  duration: const Duration(milliseconds: 800),
                  tween: Tween<double>(begin: 0, end: pageLoaded ? 1 : 0),
                  curve: Curves.easeInOut,
                  builder: (context, value, child) {
                    return Opacity(
                      opacity: value,
                      child: Transform.translate(
                        offset: Offset(0, 50 * (1 - value)),
                        child: Container(
                          margin: const EdgeInsets.symmetric(horizontal: 16),
                          decoration: BoxDecoration(
                            color: cardColor,
                            borderRadius: BorderRadius.circular(15),
                            border: Border.all(
                              color: Colors.white.withOpacity(0.3),
                              width: 1,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.2),
                                blurRadius: 15,
                                offset: const Offset(0, 5),
                              ),
                            ],
                          ),
                          child: Column(
                            children: [
                              ...allFeatures.map((feature) => Container(
                                    decoration: BoxDecoration(
                                      border: Border(
                                        bottom: BorderSide(
                                          color: Colors.white.withOpacity(0.1),
                                          width: 1,
                                        ),
                                      ),
                                    ),
                                    padding: const EdgeInsets.symmetric(
                                      vertical: 16,
                                      horizontal: 16,
                                    ),
                                    child: Row(
                                      children: [
                                        Expanded(
                                          child: Text(
                                            feature,
                                            style: TextStyle(
                                              color: textColor,
                                              fontWeight: FontWeight.w500,
                                            ),
                                          ),
                                        ),
                                        ...widget.products.map((product) {
                                          return Expanded(
                                            flex: 2,
                                            child: Text(
                                              product.features[feature] ?? '-',
                                              style: TextStyle(
                                                color: secondaryTextColor,
                                              ),
                                              textAlign: TextAlign.center,
                                            ),
                                          );
                                        }).toList(),
                                      ],
                                    ),
                                  )),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
