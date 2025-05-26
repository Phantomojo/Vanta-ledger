"""
Transaction card component for Vanta Ledger Enhanced.

This component displays a single transaction in a card-based UI inspired by Instagram posts.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty, NumericProperty, ObjectProperty

class TransactionCard(BoxLayout):
    """
    Card-based UI component for displaying a transaction.
    
    Features:
    - Instagram-inspired card design
    - Color coding for transaction types
    - Quick action buttons
    - Support for swipe gestures (to be implemented)
    """
    
    transaction_id = NumericProperty(0)
    transaction_type = StringProperty('')
    amount = NumericProperty(0)
    description = StringProperty('')
    date = StringProperty('')
    on_edit = ObjectProperty(None)
    on_delete = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the transaction card."""
        super(TransactionCard, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, None)
        self.height = 150
        self.padding = [15, 10, 15, 10]
        self.spacing = 5
        
        # Create card background
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[10,])
        
        # Bind size and position updates
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Create card content
        self._create_card_content()
    
    def _update_bg(self, instance, value):
        """Update the background rectangle position and size."""
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def _create_card_content(self):
        """Create the content layout for the transaction card."""
        # Header with date and type
        header = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        
        type_label = Label(
            text=self.transaction_type.capitalize(),
            size_hint=(0.5, 1),
            halign='left',
            valign='middle',
            color=self._get_type_color()
        )
        type_label.bind(size=type_label.setter('text_size'))
        
        date_label = Label(
            text=self.date,
            size_hint=(0.5, 1),
            halign='right',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        date_label.bind(size=date_label.setter('text_size'))
        
        header.add_widget(type_label)
        header.add_widget(date_label)
        self.add_widget(header)
        
        # Amount
        amount_label = Label(
            text=f"${self.amount:.2f}",
            size_hint=(1, 0.4),
            halign='left',
            valign='middle',
            font_size='24sp',
            color=self._get_amount_color()
        )
        amount_label.bind(size=amount_label.setter('text_size'))
        self.add_widget(amount_label)
        
        # Description
        desc_label = Label(
            text=self.description,
            size_hint=(1, 0.3),
            halign='left',
            valign='top',
            color=(0.3, 0.3, 0.3, 1)
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        self.add_widget(desc_label)
        
        # Actions
        actions = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=10)
        
        edit_btn = Button(
            text="Edit",
            size_hint=(0.5, 1),
            background_normal='',
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0.3, 0.3, 0.3, 1)
        )
        edit_btn.bind(on_press=self._on_edit_pressed)
        
        delete_btn = Button(
            text="Delete",
            size_hint=(0.5, 1),
            background_normal='',
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0.8, 0.2, 0.2, 1)
        )
        delete_btn.bind(on_press=self._on_delete_pressed)
        
        actions.add_widget(edit_btn)
        actions.add_widget(delete_btn)
        self.add_widget(actions)
    
    def _get_type_color(self):
        """Get the color based on transaction type."""
        if self.transaction_type.lower() == 'sale':
            return (0, 0.7, 0, 1)  # Green for sales
        elif self.transaction_type.lower() == 'expenditure':
            return (0.8, 0.2, 0.2, 1)  # Red for expenditures
        return (0.3, 0.3, 0.3, 1)  # Default gray
    
    def _get_amount_color(self):
        """Get the color based on amount (positive/negative)."""
        if self.transaction_type.lower() == 'sale':
            return (0, 0.7, 0, 1)  # Green for sales
        elif self.transaction_type.lower() == 'expenditure':
            return (0.8, 0.2, 0.2, 1)  # Red for expenditures
        return (0.3, 0.3, 0.3, 1)  # Default gray
    
    def _on_edit_pressed(self, instance):
        """Handle edit button press."""
        if self.on_edit:
            self.on_edit(self.transaction_id)
    
    def _on_delete_pressed(self, instance):
        """Handle delete button press."""
        if self.on_delete:
            self.on_delete(self.transaction_id)
    
    def update_transaction(self, transaction_data):
        """Update the transaction data displayed in the card."""
        self.transaction_id = transaction_data.get('id', 0)
        self.transaction_type = transaction_data.get('type', '')
        self.amount = transaction_data.get('amount', 0)
        self.description = transaction_data.get('description', '')
        self.date = transaction_data.get('date', '')
        
        # Refresh the card content
        self.clear_widgets()
        self._create_card_content()
