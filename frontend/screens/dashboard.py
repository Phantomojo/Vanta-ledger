"""
Dashboard screen for Vanta Ledger Enhanced.

This module provides the main dashboard/home screen for the application.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.properties import ObjectProperty

from frontend.components.transaction_card import TransactionCard

class DashboardScreen(Screen):
    """
    Main dashboard screen showing financial overview and recent transactions.
    
    Features:
    - Financial summary at the top
    - Recent transactions list
    - Quick action buttons
    """
    
    api_client = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the dashboard screen."""
        super(DashboardScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        # Add summary section
        self.summary_section = self._create_summary_section()
        self.layout.add_widget(self.summary_section)
        
        # Add recent transactions section
        self.transactions_section = self._create_transactions_section()
        self.layout.add_widget(self.transactions_section)
        
        # Add quick actions section
        self.actions_section = self._create_actions_section()
        self.layout.add_widget(self.actions_section)
        
        self.add_widget(self.layout)
    
    def on_enter(self):
        """Called when the screen is entered."""
        # Get API client from app
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load dashboard data."""
        if not self.api_client:
            return
        
        # Load recent transactions
        transactions = self.api_client.get_transactions(limit=5)
        self._update_transactions_list(transactions)
        
        # Update summary
        self._update_summary()
    
    def _create_summary_section(self):
        """Create the financial summary section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.3), spacing=5)
        
        # Title
        title = Label(
            text="Financial Summary",
            size_hint=(1, 0.3),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Summary content
        content = BoxLayout(orientation='horizontal', size_hint=(1, 0.7))
        
        # Income column
        income_col = BoxLayout(orientation='vertical', size_hint=(0.33, 1))
        income_label = Label(
            text="Income",
            size_hint=(1, 0.4),
            halign='center',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        income_label.bind(size=income_label.setter('text_size'))
        
        self.income_value = Label(
            text="$0.00",
            size_hint=(1, 0.6),
            halign='center',
            valign='middle',
            font_size='20sp',
            color=(0, 0.7, 0.4, 1)
        )
        self.income_value.bind(size=self.income_value.setter('text_size'))
        
        income_col.add_widget(income_label)
        income_col.add_widget(self.income_value)
        
        # Expenses column
        expenses_col = BoxLayout(orientation='vertical', size_hint=(0.33, 1))
        expenses_label = Label(
            text="Expenses",
            size_hint=(1, 0.4),
            halign='center',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        expenses_label.bind(size=expenses_label.setter('text_size'))
        
        self.expenses_value = Label(
            text="$0.00",
            size_hint=(1, 0.6),
            halign='center',
            valign='middle',
            font_size='20sp',
            color=(0.9, 0.3, 0.3, 1)
        )
        self.expenses_value.bind(size=self.expenses_value.setter('text_size'))
        
        expenses_col.add_widget(expenses_label)
        expenses_col.add_widget(self.expenses_value)
        
        # Balance column
        balance_col = BoxLayout(orientation='vertical', size_hint=(0.33, 1))
        balance_label = Label(
            text="Balance",
            size_hint=(1, 0.4),
            halign='center',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        balance_label.bind(size=balance_label.setter('text_size'))
        
        self.balance_value = Label(
            text="$0.00",
            size_hint=(1, 0.6),
            halign='center',
            valign='middle',
            font_size='20sp',
            color=(0, 0.6, 0.9, 1)
        )
        self.balance_value.bind(size=self.balance_value.setter('text_size'))
        
        balance_col.add_widget(balance_label)
        balance_col.add_widget(self.balance_value)
        
        # Add columns to content
        content.add_widget(income_col)
        content.add_widget(expenses_col)
        content.add_widget(balance_col)
        
        section.add_widget(content)
        return section
    
    def _create_transactions_section(self):
        """Create the recent transactions section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.5), spacing=5)
        
        # Title with view all button
        title_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        
        title = Label(
            text="Recent Transactions",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        
        view_all = Button(
            text="View All",
            size_hint=(0.3, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        view_all.bind(on_press=self._on_view_all_pressed)
        
        title_row.add_widget(title)
        title_row.add_widget(view_all)
        section.add_widget(title_row)
        
        # Transactions list
        self.transactions_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.85))
        
        # Wrap in scroll view
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.transactions_layout)
        
        section.add_widget(scroll)
        return section
    
    def _create_actions_section(self):
        """Create the quick actions section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5)
        
        # Title
        title = Label(
            text="Quick Actions",
            size_hint=(1, 0.3),
            halign='left',
            valign='middle',
            font_size='18sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Action buttons
        actions = BoxLayout(orientation='horizontal', size_hint=(1, 0.7), spacing=10)
        
        add_income = Button(
            text="Add Income",
            size_hint=(0.5, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0.7, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        add_income.bind(on_press=self._on_add_income_pressed)
        
        add_expense = Button(
            text="Add Expense",
            size_hint=(0.5, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        add_expense.bind(on_press=self._on_add_expense_pressed)
        
        actions.add_widget(add_income)
        actions.add_widget(add_expense)
        
        section.add_widget(actions)
        return section
    
    def _update_transactions_list(self, transactions):
        """Update the transactions list with data."""
        self.transactions_layout.clear_widgets()
        
        if not transactions:
            empty_label = Label(
                text="No recent transactions",
                size_hint=(1, 1),
                halign='center',
                valign='middle',
                color=(0.5, 0.5, 0.5, 1)
            )
            empty_label.bind(size=empty_label.setter('text_size'))
            self.transactions_layout.add_widget(empty_label)
            return
        
        for transaction in transactions:
            card = TransactionCard(
                transaction_id=transaction.get('id', 0),
                transaction_type=transaction.get('type', ''),
                amount=transaction.get('amount', 0),
                description=transaction.get('description', ''),
                date=transaction.get('date', ''),
                on_edit=self._on_edit_transaction,
                on_delete=self._on_delete_transaction
            )
            self.transactions_layout.add_widget(card)
    
    def _update_summary(self):
        """Update the financial summary with calculated values."""
        if not self.api_client:
            return
        
        # In a real implementation, we would get this from the API
        # For now, we'll calculate from the transactions
        transactions = self.api_client.get_transactions()
        
        total_income = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'sale')
        total_expenses = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'expenditure')
        balance = total_income - total_expenses
        
        self.income_value.text = f"${total_income:.2f}"
        self.expenses_value.text = f"${total_expenses:.2f}"
        self.balance_value.text = f"${balance:.2f}"
        
        # Update balance color based on value
        if balance > 0:
            self.balance_value.color = (0, 0.7, 0.4, 1)  # Green for positive
        elif balance < 0:
            self.balance_value.color = (0.9, 0.3, 0.3, 1)  # Red for negative
        else:
            self.balance_value.color = (0, 0.6, 0.9, 1)  # Blue for zero
    
    def _on_view_all_pressed(self, instance):
        """Handle view all button press."""
        if hasattr(self.manager, 'current') and hasattr(self.manager.parent.parent, 'change_screen'):
            self.manager.parent.parent.change_screen('transactions')
    
    def _on_add_income_pressed(self, instance):
        """Handle add income button press."""
        # In a real implementation, this would open a form to add income
        # For now, we'll just print a message
        print("Add income pressed")
    
    def _on_add_expense_pressed(self, instance):
        """Handle add expense button press."""
        # In a real implementation, this would open a form to add expense
        # For now, we'll just print a message
        print("Add expense pressed")
    
    def _on_edit_transaction(self, transaction_id):
        """Handle edit transaction action."""
        # In a real implementation, this would open a form to edit the transaction
        # For now, we'll just print a message
        print(f"Edit transaction {transaction_id}")
    
    def _on_delete_transaction(self, transaction_id):
        """Handle delete transaction action."""
        # In a real implementation, this would confirm and delete the transaction
        # For now, we'll just print a message
        print(f"Delete transaction {transaction_id}")
