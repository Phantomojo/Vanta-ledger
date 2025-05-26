"""
Transactions screen for Vanta Ledger Enhanced.

This module provides the transactions management screen for the application.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty

from frontend.components.transaction_card import TransactionCard

class TransactionsScreen(Screen):
    """
    Transactions management screen showing all transactions with filtering options.
    
    Features:
    - List of all transactions
    - Filter by transaction type
    - Filter by owner (for bookkeeper)
    - Add new transaction button
    """
    
    api_client = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the transactions screen."""
        super(TransactionsScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        # Add header section with filters
        self.header_section = self._create_header_section()
        self.layout.add_widget(self.header_section)
        
        # Add transactions list
        self.transactions_section = self._create_transactions_section()
        self.layout.add_widget(self.transactions_section)
        
        self.add_widget(self.layout)
        
        # Initialize filters
        self.current_type_filter = "All"
        self.current_owner_filter = None
    
    def on_enter(self):
        """Called when the screen is entered."""
        # Get API client from app
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load transactions data with current filters."""
        if not self.api_client:
            return
        
        # Get owners for filter
        owners = self.api_client.get_owners()
        self._update_owner_filter(owners)
        
        # Load transactions with filters
        self._load_transactions()
    
    def _create_header_section(self):
        """Create the header section with title and filters."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5)
        
        # Title row
        title_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        
        title = Label(
            text="Transactions",
            size_hint=(0.7, 1),
            halign='left',
            valign='middle',
            font_size='22sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        
        add_button = Button(
            text="+ Add New",
            size_hint=(0.3, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        add_button.bind(on_press=self._on_add_transaction)
        
        title_row.add_widget(title)
        title_row.add_widget(add_button)
        section.add_widget(title_row)
        
        # Filters row
        filters_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.5), spacing=10)
        
        # Type filter
        type_label = Label(
            text="Type:",
            size_hint=(0.15, 1),
            halign='right',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        type_label.bind(size=type_label.setter('text_size'))
        
        self.type_spinner = Spinner(
            text='All',
            values=('All', 'Income', 'Expense'),
            size_hint=(0.35, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.3, 0.3, 0.3, 1)
        )
        self.type_spinner.bind(text=self._on_type_filter_change)
        
        # Owner filter (for bookkeeper)
        owner_label = Label(
            text="Owner:",
            size_hint=(0.15, 1),
            halign='right',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        owner_label.bind(size=owner_label.setter('text_size'))
        
        self.owner_spinner = Spinner(
            text='All Owners',
            values=['All Owners'],
            size_hint=(0.35, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.3, 0.3, 0.3, 1)
        )
        self.owner_spinner.bind(text=self._on_owner_filter_change)
        
        filters_row.add_widget(type_label)
        filters_row.add_widget(self.type_spinner)
        filters_row.add_widget(owner_label)
        filters_row.add_widget(self.owner_spinner)
        
        section.add_widget(filters_row)
        return section
    
    def _create_transactions_section(self):
        """Create the transactions list section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.8))
        
        # Transactions list
        self.transactions_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 1))
        
        # Wrap in scroll view
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.transactions_layout)
        
        section.add_widget(scroll)
        return section
    
    def _update_transactions_list(self, transactions):
        """Update the transactions list with data."""
        self.transactions_layout.clear_widgets()
        
        if not transactions:
            empty_label = Label(
                text="No transactions found",
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
    
    def _update_owner_filter(self, owners):
        """Update the owner filter spinner with available owners."""
        values = ['All Owners']
        
        for owner in owners:
            values.append(owner.get('name', f"Owner {owner.get('id')}"))
        
        self.owner_spinner.values = values
    
    def _load_transactions(self):
        """Load transactions with current filters."""
        if not self.api_client:
            return
        
        # Apply type filter
        type_filter = None
        if self.current_type_filter == 'Income':
            type_filter = 'sale'
        elif self.current_type_filter == 'Expense':
            type_filter = 'expenditure'
        
        # Apply owner filter
        owner_id = self.current_owner_filter
        
        # Get transactions with filters
        transactions = self.api_client.get_transactions(owner_id=owner_id)
        
        # Apply type filter client-side if needed
        if type_filter:
            transactions = [t for t in transactions if t.get('type') == type_filter]
        
        # Update the list
        self._update_transactions_list(transactions)
    
    def _on_type_filter_change(self, spinner, text):
        """Handle type filter change."""
        self.current_type_filter = text
        self._load_transactions()
    
    def _on_owner_filter_change(self, spinner, text):
        """Handle owner filter change."""
        if text == 'All Owners':
            self.current_owner_filter = None
        else:
            # Find owner ID by name
            owners = self.api_client.get_owners()
            for owner in owners:
                if owner.get('name') == text:
                    self.current_owner_filter = owner.get('id')
                    break
        
        self._load_transactions()
    
    def _on_add_transaction(self, instance):
        """Handle add transaction button press."""
        # In a real implementation, this would open a form to add a transaction
        # For now, we'll just print a message
        print("Add transaction pressed")
    
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
