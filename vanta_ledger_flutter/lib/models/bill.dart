class BillModel {
  final int? id;
  final String name;
  final double amount;
  final DateTime dueDate;
  final bool isPaid;
  final String? repeat; // e.g. 'monthly', 'weekly', null
  final String? notes;
  final int? remindDaysBefore; // days before due date to remind

  BillModel({
    this.id,
    required this.name,
    required this.amount,
    required this.dueDate,
    this.isPaid = false,
    this.repeat,
    this.notes,
    this.remindDaysBefore,
  });

  BillModel copyWith({
    int? id,
    String? name,
    double? amount,
    DateTime? dueDate,
    bool? isPaid,
    String? repeat,
    String? notes,
    int? remindDaysBefore,
  }) {
    return BillModel(
      id: id ?? this.id,
      name: name ?? this.name,
      amount: amount ?? this.amount,
      dueDate: dueDate ?? this.dueDate,
      isPaid: isPaid ?? this.isPaid,
      repeat: repeat ?? this.repeat,
      notes: notes ?? this.notes,
      remindDaysBefore: remindDaysBefore ?? this.remindDaysBefore,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'amount': amount,
      'dueDate': dueDate.toIso8601String(),
      'isPaid': isPaid ? 1 : 0,
      'repeat': repeat,
      'notes': notes,
      'remindDaysBefore': remindDaysBefore,
    };
  }

  factory BillModel.fromMap(Map<String, dynamic> map) {
    return BillModel(
      id: map['id'] as int?,
      name: map['name'] as String,
      amount: map['amount'] as double,
      dueDate: DateTime.parse(map['dueDate'] as String),
      isPaid: (map['isPaid'] as int) == 1,
      repeat: map['repeat'] as String?,
      notes: map['notes'] as String?,
      remindDaysBefore: map['remindDaysBefore'] as int?,
    );
  }
} 