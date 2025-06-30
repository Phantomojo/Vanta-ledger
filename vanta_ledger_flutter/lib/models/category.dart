import 'package:flutter/material.dart';

class CategoryModel {
  final int? id;
  final String name;
  final IconData icon;
  final bool isCustom;

  CategoryModel({
    this.id,
    required this.name,
    required this.icon,
    this.isCustom = false,
  });

  CategoryModel copyWith({
    int? id,
    String? name,
    IconData? icon,
    bool? isCustom,
  }) {
    return CategoryModel(
      id: id ?? this.id,
      name: name ?? this.name,
      icon: icon ?? this.icon,
      isCustom: isCustom ?? this.isCustom,
    );
  }
} 