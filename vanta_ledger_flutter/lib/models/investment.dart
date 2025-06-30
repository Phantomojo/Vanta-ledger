class InvestmentModel {
  final int? id;
  final String name;
  final String type; // e.g. 'Stock', 'Bond', 'Crypto', etc.
  final double amount;
  final String currency;
  final DateTime date;
  final String? notes;

  InvestmentModel({
    this.id,
    required this.name,
    required this.type,
    required this.amount,
    required this.currency,
    required this.date,
    this.notes,
  });

  InvestmentModel copyWith({
    int? id,
    String? name,
    String? type,
    double? amount,
    String? currency,
    DateTime? date,
    String? notes,
  }) {
    return InvestmentModel(
      id: id ?? this.id,
      name: name ?? this.name,
      type: type ?? this.type,
      amount: amount ?? this.amount,
      currency: currency ?? this.currency,
      date: date ?? this.date,
      notes: notes ?? this.notes,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'type': type,
      'amount': amount,
      'currency': currency,
      'date': date.toIso8601String(),
      'notes': notes,
    };
  }

  factory InvestmentModel.fromMap(Map<String, dynamic> map) {
    return InvestmentModel(
      id: map['id'] as int?,
      name: map['name'] as String,
      type: map['type'] as String,
      amount: map['amount'] as double,
      currency: map['currency'] as String,
      date: DateTime.parse(map['date'] as String),
      notes: map['notes'] as String?,
    );
  }
} 