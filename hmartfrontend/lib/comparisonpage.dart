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

class _ProductComparisonPageState extends State<ProductComparisonPage> with SingleTickerProviderStateMixin {
  int currentPageIndex = 0; // Tracks the current page index
  int? selectedProductIndex; // Tracks the selected product index
  late AnimationController _backgroundController;
  late Animation<Color?> _backgroundAnimation;

  @override
  void initState() {
    super.initState();

    // Background gradient animation
    _backgroundController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 5),
    )..repeat(reverse: true);

    _backgroundAnimation = ColorTween(
      begin: Colors.deepPurple[900],
      end: Colors.blueGrey[900],
    ).animate(_backgroundController);
  }

  @override
  void dispose() {
    _backgroundController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Divide products into groups of 3
    final List<List<Product>> groupedProducts = [];
    for (var i = 0; i < widget.products.length; i += 3) {
      groupedProducts.add(widget.products.sublist(
          i, i + 3 > widget.products.length ? widget.products.length : i + 3));
    }

    // Get the products for the current page
    final visibleProducts = groupedProducts[currentPageIndex];

    return Scaffold(
      backgroundColor: Colors.transparent,
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text(
          'Vehicle Comparison',
          style: TextStyle(color: Colors.white, fontSize: 30, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: AnimatedBuilder(
        animation: _backgroundAnimation,
        builder: (context, child) {
          return Container(
            width: MediaQuery.of(context).size.width,
            height: MediaQuery.of(context).size.height,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [_backgroundAnimation.value!, Colors.black],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
            ),
            child: child,
          );
        },
        child: Column(
          children: [
            // Scrollable Product Pages
            Expanded(
              child: PageView.builder(
                itemCount: groupedProducts.length,
                physics: const BouncingScrollPhysics(),
                onPageChanged: (index) {
                  setState(() {
                    currentPageIndex = index; // Update the current page index
                    selectedProductIndex = null; // Reset selection when page changes
                  });
                },
                itemBuilder: (context, pageIndex) {
                  return Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: groupedProducts[pageIndex].asMap().entries.map((entry) {
                      int productIndex = entry.key + pageIndex * 3;
                      return _buildProductCard(entry.value, productIndex);
                    }).toList(),
                  );
                },
              ),
            ),
            // Comparison Table for the Current Page
            Expanded(
              child: SingleChildScrollView(
                child: Container(
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.7),
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
                    children: _getAllFeatures(visibleProducts).map((feature) {
                      return Container(
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: BorderSide(
                              color: Colors.white.withOpacity(0.1),
                              width: 1,
                            ),
                          ),
                        ),
                        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
                        child: Row(
                          children: [
                            // Feature Name
                            Expanded(
                              child: Text(
                                feature,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            // Feature Values for Visible Products
                            ...visibleProducts.asMap().entries.map((entry) {
                              bool isSelected =
                                  selectedProductIndex == (entry.key + currentPageIndex * 3);
                              return Expanded(
                                child: Container(
                                  decoration: isSelected
                                      ? BoxDecoration(
                                          border: Border.all(
                                            color: Colors.blueAccent,
                                            width: 2,
                                          ),
                                          borderRadius: BorderRadius.circular(8),
                                        )
                                      : null,
                                  padding: const EdgeInsets.all(8),
                                  child: Text(
                                    entry.value.features[feature] ?? '-',
                                    style: TextStyle(
                                      color: isSelected ? Colors.blue : Colors.white70,
                                      fontSize: 14,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ),
                              );
                            }).toList(),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildProductCard(Product product, int productIndex) {
  bool isSelected = selectedProductIndex == productIndex;

  return GestureDetector(
    onTap: () {
      setState(() {
        selectedProductIndex = productIndex;
      });
    },
    child: AnimatedContainer(
      duration: const Duration(milliseconds: 500),
      curve: Curves.easeInOut,
      margin: const EdgeInsets.all(8),
      width: isSelected ? 220 : 180, // Grow width if selected
      height: isSelected ? 300 : 250, // Adjust height as image is removed
      decoration: BoxDecoration(
        color: Colors.deepPurple[800]?.withOpacity(0.9),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(
          color: isSelected ? Colors.blueAccent : Colors.purpleAccent,
          width: isSelected ? 3 : 1,
        ),
        boxShadow: [
          BoxShadow(
            color: isSelected ? Colors.blueAccent.withOpacity(0.5) : Colors.purpleAccent.withOpacity(0.5),
            blurRadius: 15,
            spreadRadius: 3,
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center, // Center content vertically
          children: [
            // Product Name
            Text(
              product.name,
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: isSelected ? 22 : 18, // Grow font size if selected
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            // Product Price
            Text(
              '\$${product.price.toStringAsFixed(2)}',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: isSelected ? 20 : 16, // Grow font size if selected
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

  // Collect all unique features for visible products
  Set<String> _getAllFeatures(List<Product> products) {
    final Set<String> allFeatures = {};
    for (var product in products) {
      allFeatures.addAll(product.features.keys);
    }
    return allFeatures;
  }
}
