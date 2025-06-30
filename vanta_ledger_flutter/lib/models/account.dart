class AccountModel {
  final int? id;
  final String name;
  final double balance;

  AccountModel({
    this.id,
    required this.name,
    this.balance = 0.0,
  });

  AccountModel copyWith({
    int? id,
    String? name,
    double? balance,
  }) {
    return AccountModel(
      id: id ?? this.id,
      name: name ?? this.name,
      balance: balance ?? this.balance,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'balance': balance,
    };
  }

  factory AccountModel.fromMap(Map<String, dynamic> map) {
    return AccountModel(
      id: map['id'] as int?,
      name: map['name'] as String,
      balance: map['balance'] as double,
    );
  }
} 