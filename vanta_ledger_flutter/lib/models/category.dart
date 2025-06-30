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

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'icon': icon.codePoint,
    };
  }

  factory CategoryModel.fromMap(Map<String, dynamic> map) {
    return CategoryModel(
      id: map['id'] as int?,
      name: map['name'] as String,
      icon: IconData(map['icon'] as int, fontFamily: 'MaterialIcons'),
    );
  }
} 