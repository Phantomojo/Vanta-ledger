import 'package:flutter/material.dart';
import '../models/category.dart';
import '../services/database_service.dart';

class CategoryProvider extends ChangeNotifier {
  List<CategoryModel> _categories = [];
  List<CategoryModel> get categories => _categories;

  final DatabaseService _db = DatabaseService();

  Future<void> loadCategories() async {
    _categories = await _db.getCategories();
    notifyListeners();
  }

  Future<void> addCategory(CategoryModel cat) async {
    await _db.insertCategory(cat);
    await loadCategories();
  }

  Future<void> updateCategory(CategoryModel cat) async {
    await _db.updateCategory(cat);
    await loadCategories();
  }

  Future<void> deleteCategory(int id) async {
    await _db.deleteCategory(id);
    await loadCategories();
  }
} 