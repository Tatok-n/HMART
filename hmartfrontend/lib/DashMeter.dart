import 'package:flutter/material.dart';

class DashMeter extends StatelessWidget {
  final double matchPercentage;

  DashMeter({required this.matchPercentage});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: const Size(150, 75), // Increase size for larger DashMeter
      painter: DashMeterPainter(matchPercentage: matchPercentage),
    );
  }
}

class DashMeterPainter extends CustomPainter {
  final double matchPercentage;

  DashMeterPainter({required this.matchPercentage});

  @override
  void paint(Canvas canvas, Size size) {
    final double thickness = 12.0; // Increase thickness
    final Paint paint = Paint()
      ..shader = LinearGradient(
        colors: [Colors.purple, Colors.pink],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
      ..style = PaintingStyle.stroke
      ..strokeWidth = thickness
      ..strokeCap = StrokeCap.round;

    final double radius = (size.width / 2) - thickness; // Adjust radius to account for stroke width
    final Offset center = Offset(size.width / 2, size.height);
    final double startAngle = -3.14; // Start from the leftmost side
    final double sweepAngle = (2 * 3.14) * (matchPercentage / 100);

    // Draw background arc (faded grey)
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      2 * 3.14,
      false,
      paint..color = Colors.grey.withOpacity(0.3),
    );

    // Draw active arc (gradient)
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true; // Always repaint for animation
  }
}
