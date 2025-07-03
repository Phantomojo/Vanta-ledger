import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:ui';

class AppTheme {
  static final ColorScheme darkColorScheme = ColorScheme(
    brightness: Brightness.dark,
    primary: Color(0xFF9B5CFF), // Vibrant purple
    onPrimary: Colors.white,
    secondary: Color(0xFF6C47B6), // Deep purple
    onSecondary: Colors.white,
    background: Color(0xFF13111A), // Deep black
    onBackground: Colors.white,
    surface: Color(0xCC23203B), // Glassy surface (with opacity)
    onSurface: Colors.white,
    error: Color(0xFFFF5370),
    onError: Colors.white,
  );

  static final ThemeData darkTheme = ThemeData(
    colorScheme: darkColorScheme,
    useMaterial3: true,
    scaffoldBackgroundColor: darkColorScheme.background,
    textTheme: GoogleFonts.montserratTextTheme(ThemeData.dark().textTheme).copyWith(
      headlineLarge: GoogleFonts.montserrat(
        fontWeight: FontWeight.bold,
        fontSize: 36,
        color: Colors.white,
        letterSpacing: 0.5,
      ),
      headlineMedium: GoogleFonts.montserrat(
        fontWeight: FontWeight.bold,
        fontSize: 28,
        color: Colors.white,
      ),
      titleLarge: GoogleFonts.montserrat(
        fontWeight: FontWeight.w600,
        fontSize: 22,
        color: Colors.white,
      ),
      bodyLarge: GoogleFonts.montserrat(
        fontWeight: FontWeight.w400,
        fontSize: 16,
        color: Colors.white,
      ),
      bodyMedium: GoogleFonts.montserrat(
        fontWeight: FontWeight.w400,
        fontSize: 14,
        color: Colors.white70,
      ),
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: darkColorScheme.background.withOpacity(0.95),
      foregroundColor: darkColorScheme.onSurface,
      elevation: 0,
      titleTextStyle: GoogleFonts.montserrat(
        color: darkColorScheme.onSurface,
        fontWeight: FontWeight.bold,
        fontSize: 24,
      ),
    ),
    floatingActionButtonTheme: FloatingActionButtonThemeData(
      backgroundColor: darkColorScheme.primary,
      foregroundColor: darkColorScheme.onPrimary,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      elevation: 8,
    ),
    cardTheme: CardThemeData(
      color: darkColorScheme.surface.withOpacity(0.85),
      shadowColor: darkColorScheme.primary.withOpacity(0.15),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24),
        side: BorderSide(color: Colors.white.withOpacity(0.04), width: 1.5),
      ),
      elevation: 10,
      margin: const EdgeInsets.symmetric(vertical: 14, horizontal: 18),
      clipBehavior: Clip.antiAlias,
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: darkColorScheme.surface.withOpacity(0.7),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(16),
        borderSide: BorderSide.none,
      ),
      labelStyle: TextStyle(color: darkColorScheme.onSurface.withOpacity(0.8)),
      hintStyle: TextStyle(color: Colors.white38),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: darkColorScheme.background.withOpacity(0.95),
      selectedItemColor: darkColorScheme.primary,
      unselectedItemColor: Colors.white54,
      showUnselectedLabels: true,
      type: BottomNavigationBarType.fixed,
      elevation: 12,
    ),
    dialogTheme: DialogThemeData(
      backgroundColor: darkColorScheme.surface.withOpacity(0.95),
      titleTextStyle: GoogleFonts.montserrat(
        color: darkColorScheme.onSurface,
        fontWeight: FontWeight.bold,
        fontSize: 22,
      ),
      contentTextStyle: GoogleFonts.montserrat(
        color: darkColorScheme.onSurface,
        fontSize: 16,
      ),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: darkColorScheme.primary,
        foregroundColor: darkColorScheme.onPrimary,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        textStyle: GoogleFonts.montserrat(fontWeight: FontWeight.w600, fontSize: 16),
        elevation: 4,
        shadowColor: darkColorScheme.primary.withOpacity(0.18),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: darkColorScheme.primary,
        textStyle: GoogleFonts.montserrat(fontWeight: FontWeight.w500, fontSize: 16),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: darkColorScheme.primary,
        side: BorderSide(color: darkColorScheme.primary, width: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        textStyle: GoogleFonts.montserrat(fontWeight: FontWeight.w500, fontSize: 16),
      ),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: darkColorScheme.surface.withOpacity(0.7),
      selectedColor: darkColorScheme.primary.withOpacity(0.8),
      labelStyle: GoogleFonts.montserrat(color: darkColorScheme.onSurface),
      secondaryLabelStyle: GoogleFonts.montserrat(color: darkColorScheme.onPrimary),
      brightness: Brightness.dark,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: darkColorScheme.surface.withOpacity(0.95),
      contentTextStyle: GoogleFonts.montserrat(color: darkColorScheme.onSurface),
      actionTextColor: darkColorScheme.primary,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
    ),
    dividerTheme: DividerThemeData(
      color: Colors.white.withOpacity(0.08),
      thickness: 1.2,
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
    cardTheme: CardThemeData(
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
    dialogTheme: DialogThemeData(
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