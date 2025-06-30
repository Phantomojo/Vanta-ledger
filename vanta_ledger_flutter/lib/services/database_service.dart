import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/transaction.dart';
import '../models/category.dart';
import '../models/account.dart';
import '../models/budget.dart';
import '../models/bill.dart';
import '../models/investment.dart';
import 'package:flutter/material.dart';

class DatabaseService {
  static final DatabaseService _instance = DatabaseService._internal();
  factory DatabaseService() => _instance;
  DatabaseService._internal();

  Database? _db;

  Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await _initDb();
    return _db!;
  }

  Future<Database> _initDb() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'vanta_ledger.db');
    return await openDatabase(
      path,
      version: 1,
      onCreate: _onCreate,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL,
        description TEXT,
        date TEXT,
        categoryId INTEGER,
        accountId INTEGER,
        type INTEGER,
        recurrence INTEGER,
        cleared INTEGER DEFAULT 0
      )
    ''');
    await db.execute('''
      CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        icon INTEGER,
        isCustom INTEGER
      )
    ''');
    await db.execute('''
      CREATE TABLE accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        balance REAL
      )
    ''');
    await db.execute('''
      CREATE TABLE budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoryId INTEGER,
        limit REAL,
        period TEXT,
        spent REAL
      )
    ''');
    await db.execute('''
      CREATE TABLE bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        amount REAL,
        dueDate TEXT,
        isPaid INTEGER,
        repeat TEXT,
        notes TEXT,
        remindDaysBefore INTEGER
      )
    ''');
    await db.execute('''
      CREATE TABLE investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        amount REAL,
        currency TEXT,
        date TEXT,
        notes TEXT
      )
    ''');

    // Insert default categories
    final defaultCategories = [
      {'name': 'Food', 'icon': Icons.fastfood.codePoint, 'isCustom': 0},
      {'name': 'Travel', 'icon': Icons.directions_car.codePoint, 'isCustom': 0},
      {'name': 'Office', 'icon': Icons.business.codePoint, 'isCustom': 0},
      {'name': 'Utilities', 'icon': Icons.lightbulb.codePoint, 'isCustom': 0},
      {'name': 'Salary', 'icon': Icons.attach_money.codePoint, 'isCustom': 0},
      {'name': 'Misc', 'icon': Icons.category.codePoint, 'isCustom': 0},
    ];
    for (final cat in defaultCategories) {
      await db.insert('categories', cat);
    }

    // Insert default company accounts
    final defaultAccounts = [
      {'name': 'Company 1', 'balance': 0.0},
      {'name': 'Company 2', 'balance': 0.0},
      {'name': 'Company 3', 'balance': 0.0},
    ];
    for (final acc in defaultAccounts) {
      await db.insert('accounts', acc);
    }
  }

  // Transaction CRUD
  Future<int> insertTransaction(TransactionModel tx) async {
    final db = await database;
    return await db.insert('transactions', tx.toMap());
  }

  Future<List<TransactionModel>> getTransactions() async {
    final db = await database;
    final maps = await db.query('transactions', orderBy: 'date DESC');
    return maps.map((m) => TransactionModel.fromMap(m)).toList();
  }

  Future<int> updateTransaction(TransactionModel tx) async {
    final db = await database;
    return await db.update('transactions', tx.toMap(), where: 'id = ?', whereArgs: [tx.id]);
  }

  Future<int> deleteTransaction(int id) async {
    final db = await database;
    return await db.delete('transactions', where: 'id = ?', whereArgs: [id]);
  }

  // Category CRUD
  Future<int> insertCategory(CategoryModel cat) async {
    final db = await database;
    return await db.insert('categories', {
      'name': cat.name,
      'icon': cat.icon.codePoint,
      'isCustom': cat.isCustom ? 1 : 0,
    });
  }

  Future<List<CategoryModel>> getCategories() async {
    final db = await database;
    final maps = await db.query('categories');
    return maps.map((m) => CategoryModel(
      id: m['id'] as int?,
      name: m['name'] as String,
      icon: IconData(m['icon'] as int, fontFamily: 'MaterialIcons'),
      isCustom: (m['isCustom'] as int) == 1,
    )).toList();
  }

  Future<int> updateCategory(CategoryModel cat) async {
    final db = await database;
    return await db.update('categories', {
      'name': cat.name,
      'icon': cat.icon.codePoint,
      'isCustom': cat.isCustom ? 1 : 0,
    }, where: 'id = ?', whereArgs: [cat.id]);
  }

  Future<int> deleteCategory(int id) async {
    final db = await database;
    return await db.delete('categories', where: 'id = ?', whereArgs: [id]);
  }

  // Account CRUD
  Future<int> insertAccount(AccountModel acc) async {
    final db = await database;
    return await db.insert('accounts', acc.toMap());
  }

  Future<List<AccountModel>> getAccounts() async {
    final db = await database;
    final maps = await db.query('accounts');
    return maps.map((m) => AccountModel(
      id: m['id'] as int?,
      name: m['name'] as String,
      balance: m['balance'] as double,
    )).toList();
  }

  Future<int> updateAccount(AccountModel acc) async {
    final db = await database;
    return await db.update('accounts', acc.toMap(), where: 'id = ?', whereArgs: [acc.id]);
  }

  Future<int> deleteAccount(int id) async {
    final db = await database;
    return await db.delete('accounts', where: 'id = ?', whereArgs: [id]);
  }

  // Budget CRUD
  Future<int> insertBudget(BudgetModel budget) async {
    final db = await database;
    return await db.insert('budgets', budget.toMap());
  }

  Future<List<BudgetModel>> getBudgets() async {
    final db = await database;
    final maps = await db.query('budgets');
    return maps.map((m) => BudgetModel.fromMap(m)).toList();
  }

  Future<int> updateBudget(BudgetModel budget) async {
    final db = await database;
    return await db.update('budgets', budget.toMap(), where: 'id = ?', whereArgs: [budget.id]);
  }

  Future<int> deleteBudget(int id) async {
    final db = await database;
    return await db.delete('budgets', where: 'id = ?', whereArgs: [id]);
  }

  // Bill CRUD
  Future<int> insertBill(BillModel bill) async {
    final db = await database;
    return await db.insert('bills', bill.toMap());
  }

  Future<List<BillModel>> getBills() async {
    final db = await database;
    final maps = await db.query('bills');
    return maps.map((m) => BillModel.fromMap(m)).toList();
  }

  Future<int> updateBill(BillModel bill) async {
    final db = await database;
    return await db.update('bills', bill.toMap(), where: 'id = ?', whereArgs: [bill.id]);
  }

  Future<int> deleteBill(int id) async {
    final db = await database;
    return await db.delete('bills', where: 'id = ?', whereArgs: [id]);
  }

  // Investment CRUD
  Future<int> insertInvestment(InvestmentModel investment) async {
    final db = await database;
    return await db.insert('investments', investment.toMap());
  }

  Future<List<InvestmentModel>> getInvestments() async {
    final db = await database;
    final maps = await db.query('investments');
    return maps.map((m) => InvestmentModel.fromMap(m)).toList();
  }

  Future<int> updateInvestment(InvestmentModel investment) async {
    final db = await database;
    return await db.update('investments', investment.toMap(), where: 'id = ?', whereArgs: [investment.id]);
  }

  Future<int> deleteInvestment(int id) async {
    final db = await database;
    return await db.delete('investments', where: 'id = ?', whereArgs: [id]);
  }
} 