class BudgetModel {
  final int? id;
  final int categoryId;
  final double limit;
  final String period; // e.g. 'monthly', 'weekly', 'custom'
  final double spent;

  BudgetModel({
    this.id,
    required this.categoryId,
    required this.limit,
    required this.period,
    this.spent = 0.0,
  });

  BudgetModel copyWith({
    int? id,
    int? categoryId,
    double? limit,
    String? period,
    double? spent,
  }) {
    return BudgetModel(
      id: id ?? this.id,
      categoryId: categoryId ?? this.categoryId,
      limit: limit ?? this.limit,
      period: period ?? this.period,
      spent: spent ?? this.spent,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'categoryId': categoryId,
      'limit': limit,
      'period': period,
      'spent': spent,
    };
  }

  factory BudgetModel.fromMap(Map<String, dynamic> map) {
    return BudgetModel(
      id: map['id'] as int?,
      categoryId: map['categoryId'] as int,
      limit: map['limit'] as double,
      period: map['period'] as String,
      spent: map['spent'] as double,
    );
  }
} 