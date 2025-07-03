import 'package:flutter/material.dart';
import '../wakanda_text.dart';
import 'dart:async';
import 'dart:ui';

class SplashScreen extends StatefulWidget {
  final VoidCallback? onFinish;
  const SplashScreen({Key? key, this.onFinish}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with TickerProviderStateMixin {
  late AnimationController _logoController;
  late AnimationController _textController;
  bool _showWakanda = false;
  bool _morphDone = false;

  @override
  void initState() {
    super.initState();
    _logoController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );
    _textController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );
    _startAnimation();
  }

  Future<void> _startAnimation() async {
    await Future.delayed(const Duration(milliseconds: 200));
    _logoController.forward();
    await Future.delayed(const Duration(milliseconds: 700));
    _textController.forward();
    await Future.delayed(const Duration(milliseconds: 1100));
    setState(() => _showWakanda = true);
  }

  void _onMorphComplete() {
    if (!_morphDone) {
      _morphDone = true;
      if (widget.onFinish != null) widget.onFinish!();
    }
  }

  @override
  void dispose() {
    _logoController.dispose();
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          Positioned.fill(
            child: Image.asset(
              'assets/images/splash_bg.jpg',
              fit: BoxFit.cover,
            ),
          ),
          Positioned.fill(
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
              child: Container(
                color: Colors.black.withOpacity(0.55),
              ),
            ),
          ),
          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ScaleTransition(
                  scale: Tween<double>(begin: 0.7, end: 1.0).animate(
                    CurvedAnimation(parent: _logoController, curve: Curves.easeOutBack),
                  ),
                  child: FadeTransition(
                    opacity: _logoController,
                    child: Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(32),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.deepPurple.withOpacity(0.18),
                            blurRadius: 32,
                            spreadRadius: 2,
                          ),
                        ],
                      ),
                      child: Image.asset(
                        'assets/images/icon-512.png',
                        height: 84,
                        width: 84,
                        fit: BoxFit.contain,
                        semanticLabel: 'Vanta Ledger Logo',
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                FadeTransition(
                  opacity: _textController,
                  child: AnimatedSwitcher(
                    duration: const Duration(milliseconds: 700),
                    child: _showWakanda
                        ? WakandaText(
                            key: const ValueKey('wakanda'),
                            text: 'Vanta Ledger',
                            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 32,
                              letterSpacing: 1.2,
                              shadows: [Shadow(color: Colors.black.withOpacity(0.22), blurRadius: 4)],
                            ),
                            enableLoop: false,
                            playOnBuild: true,
                            onMorphComplete: _onMorphComplete,
                          )
                        : Text(
                            'Vanta Ledger',
                            key: const ValueKey('english'),
                            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 32,
                              letterSpacing: 1.2,
                              shadows: [Shadow(color: Colors.black.withOpacity(0.22), blurRadius: 4)],
                            ),
                          ),
                  ),
                ),
                const SizedBox(height: 36),
                const CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Colors.deepPurpleAccent),
                  strokeWidth: 3.2,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
} 