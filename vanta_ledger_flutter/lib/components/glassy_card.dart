import 'package:flutter/material.dart';
import 'dart:ui';

class GlassyCard extends StatelessWidget {
  final Widget child;
  final double borderRadius;
  final bool accent;
  final double? width;
  final double? height;
  final EdgeInsetsGeometry? padding;
  final Gradient? gradient;
  final BoxBorder? border;

  const GlassyCard({
    Key? key,
    required this.child,
    this.borderRadius = 24,
    this.accent = false,
    this.width,
    this.height,
    this.padding,
    this.gradient,
    this.border,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final defaultGradient = accent
        ? LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.redAccent.withOpacity(0.10),
              Colors.white.withOpacity(0.08),
              Colors.transparent,
            ],
          )
        : LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white.withOpacity(0.10),
              Colors.deepPurple.withOpacity(0.08),
              Colors.transparent,
            ],
          );
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: Container(
          width: width,
          height: height,
          padding: padding,
          decoration: BoxDecoration(
            gradient: gradient ?? defaultGradient,
            borderRadius: BorderRadius.circular(borderRadius),
            border: border ?? Border.all(color: Colors.white.withOpacity(0.07), width: 1.0),
          ),
          child: child,
        ),
      ),
    );
  }
} 