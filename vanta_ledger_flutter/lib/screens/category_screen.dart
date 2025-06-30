import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/category_provider.dart';
import '../models/category.dart';
import 'package:flutter_svg/flutter_svg.dart';

class CategoryScreen extends StatefulWidget {
  const CategoryScreen({super.key});

  @override
  State<CategoryScreen> createState() => _CategoryScreenState();
}

class _CategoryScreenState extends State<CategoryScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<CategoryProvider>(context, listen: false).loadCategories();
    });
  }

  Future<void> _showAddCategoryDialog() async {
    final _formKey = GlobalKey<FormState>();
    String name = '';
    int iconCode = Icons.category.codePoint;
    await showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Category'),
        content: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                decoration: const InputDecoration(labelText: 'Name'),
                validator: (val) => val == null || val.isEmpty ? 'Enter name' : null,
                onSaved: (val) => name = val ?? '',
              ),
              // For simplicity, just use default icon
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (_formKey.currentState?.validate() ?? false) {
                _formKey.currentState?.save();
                final cat = CategoryModel(
                  name: name,
                  icon: IconData(iconCode, fontFamily: 'MaterialIcons'),
                  isCustom: true,
                );
                await Provider.of<CategoryProvider>(context, listen: false).addCategory(cat);
                if (mounted) Navigator.pop(context);
              }
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final categories = context.watch<CategoryProvider>().categories;
    return Scaffold(
      appBar: AppBar(
        leading: Padding(
          padding: const EdgeInsets.all(8.0),
          child: SvgPicture.asset(
            'assets/images/app_logo_placeholder.svg',
            height: 32,
            width: 32,
            semanticsLabel: 'Vanta Ledger Logo',
          ),
        ),
        title: const Text('Categories'),
      ),
      body: categories.isEmpty
          ? const Center(child: Text('No categories yet.'))
          : ListView.builder(
              itemCount: categories.length,
              itemBuilder: (context, index) {
                final cat = categories[index];
                return Dismissible(
                  key: ValueKey(cat.id),
                  direction: categories.length > 1 ? DismissDirection.endToStart : DismissDirection.none,
                  background: Container(
                    color: Colors.red,
                    alignment: Alignment.centerRight,
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: const Icon(Icons.delete, color: Colors.white),
                  ),
                  confirmDismiss: (direction) async {
                    if (categories.length <= 1) return false;
                    return await showDialog(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Delete Category'),
                        content: Text('Are you sure you want to delete "${cat.name}"?'),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
                          ElevatedButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete')),
                        ],
                      ),
                    );
                  },
                  onDismissed: (_) async {
                    await Provider.of<CategoryProvider>(context, listen: false).deleteCategory(cat.id!);
                  },
                  child: ListTile(
                    leading: Icon(cat.icon),
                    title: Text(cat.name),
                    subtitle: cat.isCustom ? const Text('Custom') : const Text('Default'),
                    trailing: IconButton(
                      icon: const Icon(Icons.edit),
                      onPressed: () async {
                        final _formKey = GlobalKey<FormState>();
                        String name = cat.name;
                        await showDialog(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: const Text('Rename Category'),
                            content: Form(
                              key: _formKey,
                              child: TextFormField(
                                initialValue: name,
                                validator: (val) => val == null || val.isEmpty ? 'Enter name' : null,
                                onSaved: (val) => name = val ?? '',
                              ),
                            ),
                            actions: [
                              TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
                              ElevatedButton(
                                onPressed: () async {
                                  if (_formKey.currentState?.validate() ?? false) {
                                    _formKey.currentState?.save();
                                    await Provider.of<CategoryProvider>(context, listen: false).updateCategory(
                                      cat.copyWith(name: name),
                                    );
                                    Navigator.pop(context);
                                  }
                                },
                                child: const Text('Save'),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  ),
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddCategoryDialog,
        child: const Icon(Icons.add),
      ),
    );
  }
} 