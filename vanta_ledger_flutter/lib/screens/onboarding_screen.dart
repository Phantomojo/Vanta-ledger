import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_svg/flutter_svg.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({Key? key}) : super(key: key);

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _controller = PageController();
  int _page = 0;

  final List<Map<String, String>> _pages = [
    {
      'title': 'Welcome to Vanta Ledger',
      'body': 'A modern, private, offline-first finance app for everyone.'
    },
    {
      'title': 'Track Everything',
      'body': 'Manage transactions, budgets, bills, and more with ease.'
    },
    {
      'title': 'Your Data, Your Privacy',
      'body': 'All data is stored locally. You control your backups.'
    },
    {
      'title': 'Get Started!',
      'body': "Let's build your financial future together."
    },
  ];

  Future<void> _finishOnboarding() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('onboarding_complete', true);
    if (mounted) {
      Navigator.of(context).pushNamedAndRemoveUntil('/', (route) => false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 32),
            Center(
              child: SvgPicture.asset(
                'assets/images/app_logo_placeholder.svg',
                height: 120,
                width: 120,
                semanticsLabel: 'Vanta Ledger Logo',
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: PageView.builder(
                controller: _controller,
                itemCount: _pages.length,
                onPageChanged: (i) => setState(() => _page = i),
                itemBuilder: (context, i) => Padding(
                  padding: const EdgeInsets.all(32),
                  child: Semantics(
                    label: _pages[i]['title'],
                    hint: _pages[i]['body'],
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(_pages[i]['title']!, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
                        const SizedBox(height: 24),
                        Text(_pages[i]['body']!, style: const TextStyle(fontSize: 18, color: Colors.white70)),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(_pages.length, (i) => Semantics(
                label: i == _page ? 'Current page' : 'Page',
                child: Container(
                  margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 16),
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: i == _page ? Theme.of(context).colorScheme.primary : Colors.grey,
                  ),
                ),
              )),
            ),
            if (_page == _pages.length - 1)
              Padding(
                padding: const EdgeInsets.only(bottom: 32),
                child: ElevatedButton(
                  onPressed: _finishOnboarding,
                  child: const Text('Get Started'),
                ),
              )
            else
              Padding(
                padding: const EdgeInsets.only(bottom: 32),
                child: TextButton(
                  onPressed: () => _controller.nextPage(duration: const Duration(milliseconds: 300), curve: Curves.easeInOut),
                  child: const Text('Next'),
                ),
              ),
          ],
        ),
      ),
    );
  }
} 