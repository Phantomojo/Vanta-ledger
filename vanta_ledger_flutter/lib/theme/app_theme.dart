import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static final ColorScheme darkColorScheme = ColorScheme.fromSeed(
    seedColor: const Color(0xFF8F5AFF), // Purple
    brightness: Brightness.dark,
    primary: const Color(0xFF8F5AFF),
    secondary: const Color(0xFFB388FF),
    background: const Color(0xFF18122B),
    surface: const Color(0xFF23203B),
    onPrimary: Colors.white,
    onSecondary: Colors.white,
    onBackground: Colors.white,
    onSurface: Colors.white,
  );

  static final ThemeData darkTheme = ThemeData(
    colorScheme: darkColorScheme,
    useMaterial3: true,
    scaffoldBackgroundColor: darkColorScheme.background,
    textTheme: GoogleFonts.poppinsTextTheme(ThemeData.dark().textTheme),
    appBarTheme: AppBarTheme(
      backgroundColor: darkColorScheme.surface,
      foregroundColor: darkColorScheme.onSurface,
      elevation: 0,
      titleTextStyle: GoogleFonts.poppins(
        color: darkColorScheme.onSurface,
        fontWeight: FontWeight.bold,
        fontSize: 22,
      ),
    ),
    floatingActionButtonTheme: FloatingActionButtonThemeData(
      backgroundColor: darkColorScheme.primary,
      foregroundColor: darkColorScheme.onPrimary,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
    ),
    cardTheme: CardTheme(
      color: darkColorScheme.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      elevation: 4,
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: darkColorScheme.surface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      labelStyle: TextStyle(color: darkColorScheme.onSurface),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: darkColorScheme.surface,
      selectedItemColor: darkColorScheme.primary,
      unselectedItemColor: darkColorScheme.onSurface.withOpacity(0.6),
      showUnselectedLabels: true,
      type: BottomNavigationBarType.fixed,
    ),
    dialogTheme: DialogTheme(
      backgroundColor: darkColorScheme.surface,
      titleTextStyle: GoogleFonts.poppins(
        color: darkColorScheme.onSurface,
        fontWeight: FontWeight.bold,
        fontSize: 20,
      ),
      contentTextStyle: GoogleFonts.poppins(
        color: darkColorScheme.onSurface,
        fontSize: 16,
      ),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: darkColorScheme.primary,
        foregroundColor: darkColorScheme.onPrimary,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 16),
        elevation: 2,
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: darkColorScheme.primary,
        textStyle: GoogleFonts.poppins(fontWeight: FontWeight.w500, fontSize: 16),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: darkColorScheme.primary,
        side: BorderSide(color: darkColorScheme.primary),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: GoogleFonts.poppins(fontWeight: FontWeight.w500, fontSize: 16),
      ),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: darkColorScheme.surface,
      selectedColor: darkColorScheme.primary,
      labelStyle: GoogleFonts.poppins(color: darkColorScheme.onSurface),
      secondaryLabelStyle: GoogleFonts.poppins(color: darkColorScheme.onPrimary),
      brightness: Brightness.dark,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: darkColorScheme.surface,
      contentTextStyle: GoogleFonts.poppins(color: darkColorScheme.onSurface),
      actionTextColor: darkColorScheme.primary,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
    dividerTheme: DividerThemeData(
      color: darkColorScheme.onSurface.withOpacity(0.12),
      thickness: 1,
      space: 1,
    ),
    // Add more Material 3 polish as needed
  );

  static final ColorScheme lightColorScheme = ColorScheme.fromSeed(
    seedColor: const Color(0xFF8F5AFF), // Purple
    brightness: Brightness.light,
    primary: const Color(0xFF8F5AFF),
    secondary: const Color(0xFFB388FF),
    background: const Color(0xFFF6F6F6),
    surface: const Color(0xFFFFFFFF),
    onPrimary: Colors.white,
    onSecondary: Colors.black,
    onBackground: Colors.black,
    onSurface: Colors.black,
  );

  static final ThemeData lightTheme = ThemeData(
    colorScheme: lightColorScheme,
    useMaterial3: true,
    scaffoldBackgroundColor: lightColorScheme.background,
    textTheme: GoogleFonts.poppinsTextTheme(ThemeData.light().textTheme),
    appBarTheme: AppBarTheme(
      backgroundColor: lightColorScheme.surface,
      foregroundColor: lightColorScheme.onSurface,
      elevation: 0,
      titleTextStyle: GoogleFonts.poppins(
        color: lightColorScheme.onSurface,
        fontWeight: FontWeight.bold,
        fontSize: 22,
      ),
    ),
    floatingActionButtonTheme: FloatingActionButtonThemeData(
      backgroundColor: lightColorScheme.primary,
      foregroundColor: lightColorScheme.onPrimary,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
    ),
    cardTheme: CardTheme(
      color: lightColorScheme.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      elevation: 4,
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: lightColorScheme.surface,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      labelStyle: TextStyle(color: lightColorScheme.onSurface),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: lightColorScheme.surface,
      selectedItemColor: lightColorScheme.primary,
      unselectedItemColor: lightColorScheme.onSurface.withOpacity(0.6),
      showUnselectedLabels: true,
      type: BottomNavigationBarType.fixed,
    ),
    dialogTheme: DialogTheme(
      backgroundColor: lightColorScheme.surface,
      titleTextStyle: GoogleFonts.poppins(
        color: lightColorScheme.onSurface,
        fontWeight: FontWeight.bold,
        fontSize: 20,
      ),
      contentTextStyle: GoogleFonts.poppins(
        color: lightColorScheme.onSurface,
        fontSize: 16,
      ),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: lightColorScheme.primary,
        foregroundColor: lightColorScheme.onPrimary,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: GoogleFonts.poppins(fontWeight: FontWeight.w600, fontSize: 16),
        elevation: 2,
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: lightColorScheme.primary,
        textStyle: GoogleFonts.poppins(fontWeight: FontWeight.w500, fontSize: 16),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: lightColorScheme.primary,
        side: BorderSide(color: lightColorScheme.primary),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: GoogleFonts.poppins(fontWeight: FontWeight.w500, fontSize: 16),
      ),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: lightColorScheme.surface,
      selectedColor: lightColorScheme.primary,
      labelStyle: GoogleFonts.poppins(color: lightColorScheme.onSurface),
      secondaryLabelStyle: GoogleFonts.poppins(color: lightColorScheme.onPrimary),
      brightness: Brightness.light,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: lightColorScheme.surface,
      contentTextStyle: GoogleFonts.poppins(color: lightColorScheme.onSurface),
      actionTextColor: lightColorScheme.primary,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
    dividerTheme: DividerThemeData(
      color: lightColorScheme.onSurface.withOpacity(0.12),
      thickness: 1,
      space: 1,
    ),
    // Add more Material 3 polish as needed
  );
} 