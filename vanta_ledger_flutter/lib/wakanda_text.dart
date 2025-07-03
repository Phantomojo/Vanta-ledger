import 'package:flutter/material.dart';
import 'dart:async';

/// Wakanda alphabet mapping (A-Z, a-z, 0-9) based on provided image
const Map<String, String> _wakandaMap = {
  // Uppercase
  'A': 'ᔑ', 'B': 'ᓵ', 'C': 'ᒷ', 'D': '⎓', 'E': '⊣', 'F': '⍑', 'G': '╎', 'H': '⋮', 'I': 'ꖌ', 'J': 'ꖎ', 'K': 'ᒲ', 'L': 'リ', 'M': '𝙹',
  'N': '!¡', 'O': 'ᑑ', 'P': '∷', 'Q': 'ᓭ', 'R': 'ℸ', 'S': '⚍', 'T': '⍊', 'U': '∴', 'V': '̇/', 'W': '||', 'X': '⨅', 'Y': 'ꖘ', 'Z': 'ꖳ',
  // Lowercase
  'a': 'ᔑ', 'b': 'ᓵ', 'c': 'ᒷ', 'd': '⎓', 'e': '⊣', 'f': '⍑', 'g': '╎', 'h': '⋮', 'i': 'ꖌ', 'j': 'ꖎ', 'k': 'ᒲ', 'l': 'リ', 'm': '𝙹',
  'n': '!¡', 'o': 'ᑑ', 'p': '∷', 'q': 'ᓭ', 'r': 'ℸ', 's': '⚍', 't': '⍊', 'u': '∴', 'v': '̇/', 'w': '||', 'x': '⨅', 'y': 'ꖘ', 'z': 'ꖳ',
  // Numbers
  '0': 'ᓭ', '1': 'リ', '2': 'ᒲ', '3': '⍑', '4': '⍊', '5': '𝙹', '6': 'ᔑ', '7': 'ꖌ', '8': 'ꖎ', '9': '⨅',
};

String _toWakanda(String text) {
  return text.split('').map((c) => _wakandaMap[c] ?? c).join();
}

class WakandaText extends StatefulWidget {
  final String text;
  final TextStyle? style;
  final Duration waveDuration;
  final Duration morphDuration;
  final Duration loopInterval;
  final bool enableLoop;
  final bool playOnBuild;
  final VoidCallback? onMorphComplete;

  const WakandaText({
    Key? key,
    required this.text,
    this.style,
    this.waveDuration = const Duration(milliseconds: 900),
    this.morphDuration = const Duration(milliseconds: 1200),
    this.loopInterval = const Duration(seconds: 12),
    this.enableLoop = true,
    this.playOnBuild = false,
    this.onMorphComplete,
  }) : super(key: key);

  @override
  State<WakandaText> createState() => _WakandaTextState();
}

class _WakandaTextState extends State<WakandaText> with SingleTickerProviderStateMixin {
  late List<String> _displayChars;
  late List<String> _targetChars;
  bool _isWakanda = false;
  Timer? _loopTimer;

  @override
  void initState() {
    super.initState();
    _displayChars = widget.text.split('');
    _targetChars = _toWakanda(widget.text).split('');
    if (widget.enableLoop) {
      _startLoop();
    } else if (widget.playOnBuild) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _playWave());
    }
  }

  @override
  void didUpdateWidget(covariant WakandaText oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.playOnBuild && !oldWidget.playOnBuild) {
      _playWave();
    }
  }

  void _startLoop() {
    _loopTimer?.cancel();
    _loopTimer = Timer.periodic(widget.loopInterval, (_) => _playWave());
  }

  @override
  void dispose() {
    _loopTimer?.cancel();
    super.dispose();
  }

  void _playWave() async {
    if (!mounted) return;
    setState(() => _isWakanda = true);
    for (int i = 0; i < _displayChars.length; i++) {
      await Future.delayed(widget.waveDuration ~/ (_displayChars.length + 1));
      if (!mounted) return;
      setState(() {
        _displayChars[i] = _targetChars[i];
      });
    }
    await Future.delayed(widget.morphDuration);
    for (int i = 0; i < _displayChars.length; i++) {
      await Future.delayed(widget.waveDuration ~/ (_displayChars.length + 1));
      if (!mounted) return;
      setState(() {
        _displayChars[i] = widget.text[i];
      });
    }
    setState(() => _isWakanda = false);
    if (widget.onMorphComplete != null) widget.onMorphComplete!();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _playWave,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: List.generate(_displayChars.length, (i) {
            return AnimatedDefaultTextStyle(
              duration: widget.waveDuration ~/ (_displayChars.length + 1),
              style: widget.style ?? DefaultTextStyle.of(context).style,
              child: Text(_displayChars[i]),
            );
          }),
        ),
      ),
    );
  }
} 