"""
Analytics screen for Vanta Ledger Enhanced.

This module provides the financial analytics and reporting screen for the application.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

class AnalyticsScreen(Screen):
    """
    Financial analytics screen showing charts and reports.
    
    Features:
    - Income vs. Expenses chart
    - Transaction trends over time
    - Category breakdown
    - Export options for reports
    """
    
    api_client = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the analytics screen."""
        super(AnalyticsScreen, self).__init__(**kwargs)
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        
        # Add header section
        self.header_section = self._create_header_section()
        self.layout.add_widget(self.header_section)
        
        # Add charts section
        self.charts_section = self._create_charts_section()
        self.layout.add_widget(self.charts_section)
        
        # Add export section
        self.export_section = self._create_export_section()
        self.layout.add_widget(self.export_section)
        
        self.add_widget(self.layout)
        
        # Initialize period filter
        self.current_period = "This Month"
        self.current_owner_filter = None
    
    def on_enter(self):
        """Called when the screen is entered."""
        # Get API client from app
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load analytics data with current filters."""
        if not self.api_client:
            return
        
        # Get owners for filter
        owners = self.api_client.get_owners()
        self._update_owner_filter(owners)
        
        # Load transactions and update charts
        self._update_charts()
    
    def _create_header_section(self):
        """Create the header section with title and filters."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=5)
        
        # Title
        title = Label(
            text="Financial Analytics",
            size_hint=(1, 0.6),
            halign='left',
            valign='middle',
            font_size='22sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        title.bind(size=title.setter('text_size'))
        section.add_widget(title)
        
        # Filters row
        filters_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.4), spacing=10)
        
        # Period filter
        period_label = Label(
            text="Period:",
            size_hint=(0.15, 1),
            halign='right',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        period_label.bind(size=period_label.setter('text_size'))
        
        self.period_spinner = Spinner(
            text='This Month',
            values=('This Month', 'Last Month', 'This Quarter', 'This Year', 'All Time'),
            size_hint=(0.35, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.3, 0.3, 0.3, 1)
        )
        self.period_spinner.bind(text=self._on_period_filter_change)
        
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
        
        filters_row.add_widget(period_label)
        filters_row.add_widget(self.period_spinner)
        filters_row.add_widget(owner_label)
        filters_row.add_widget(self.owner_spinner)
        
        section.add_widget(filters_row)
        return section
    
    def _create_charts_section(self):
        """Create the charts section."""
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.7), spacing=10)
        
        # Income vs Expenses chart
        income_vs_expenses = BoxLayout(orientation='vertical', size_hint=(1, 0.5))
        
        income_vs_expenses_title = Label(
            text="Income vs Expenses",
            size_hint=(1, 0.2),
            halign='left',
            valign='middle',
            font_size='16sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        income_vs_expenses_title.bind(size=income_vs_expenses_title.setter('text_size'))
        
        self.income_vs_expenses_chart = BoxLayout(size_hint=(1, 0.8))
        
        income_vs_expenses.add_widget(income_vs_expenses_title)
        income_vs_expenses.add_widget(self.income_vs_expenses_chart)
        
        # Transactions over time chart
        transactions_over_time = BoxLayout(orientation='vertical', size_hint=(1, 0.5))
        
        transactions_over_time_title = Label(
            text="Transactions Over Time",
            size_hint=(1, 0.2),
            halign='left',
            valign='middle',
            font_size='16sp',
            color=(0.3, 0.3, 0.3, 1)
        )
        transactions_over_time_title.bind(size=transactions_over_time_title.setter('text_size'))
        
        self.transactions_over_time_chart = BoxLayout(size_hint=(1, 0.8))
        
        transactions_over_time.add_widget(transactions_over_time_title)
        transactions_over_time.add_widget(self.transactions_over_time_chart)
        
        section.add_widget(income_vs_expenses)
        section.add_widget(transactions_over_time)
        
        return section
    
    def _create_export_section(self):
        """Create the export section."""
        section = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        export_label = Label(
            text="Export Report:",
            size_hint=(0.3, 1),
            halign='right',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        export_label.bind(size=export_label.setter('text_size'))
        
        export_pdf = Button(
            text="PDF",
            size_hint=(0.2, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        export_pdf.bind(on_press=self._on_export_pdf)
        
        export_excel = Button(
            text="Excel",
            size_hint=(0.2, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0.7, 0.4, 1),
            color=(1, 1, 1, 1)
        )
        export_excel.bind(on_press=self._on_export_excel)
        
        export_csv = Button(
            text="CSV",
            size_hint=(0.2, 0.8),
            pos_hint={'center_y': 0.5},
            background_normal='',
            background_color=(0, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        export_csv.bind(on_press=self._on_export_csv)
        
        section.add_widget(export_label)
        section.add_widget(export_pdf)
        section.add_widget(export_excel)
        section.add_widget(export_csv)
        
        return section
    
    def _update_owner_filter(self, owners):
        """Update the owner filter spinner with available owners."""
        values = ['All Owners']
        
        for owner in owners:
            values.append(owner.get('name', f"Owner {owner.get('id')}"))
        
        self.owner_spinner.values = values
    
    def _update_charts(self):
        """Update charts with current data and filters."""
        if not self.api_client:
            return
        
        # Get transactions with filters
        transactions = self._get_filtered_transactions()
        
        # Update income vs expenses chart
        self._update_income_vs_expenses_chart(transactions)
        
        # Update transactions over time chart
        self._update_transactions_over_time_chart(transactions)
    
    def _get_filtered_transactions(self):
        """Get transactions with current filters applied."""
        # Apply owner filter
        owner_id = self.current_owner_filter
        
        # Get transactions
        transactions = self.api_client.get_transactions(owner_id=owner_id)
        
        # Apply period filter (in a real implementation, this would be done server-side)
        # For now, we'll just return all transactions
        return transactions
    
    def _update_income_vs_expenses_chart(self, transactions):
        """Update the income vs expenses chart."""
        self.income_vs_expenses_chart.clear_widgets()
        
        # Calculate totals
        total_income = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'sale')
        total_expenses = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'expenditure')
        
        # Create figure
        fig, ax = plt.subplots()
        
        # Create bar chart
        categories = ['Income', 'Expenses']
        values = [total_income, total_expenses]
        colors = ['#00b366', '#e64d4d']
        
        ax.bar(categories, values, color=colors)
        ax.set_ylabel('Amount ($)')
        ax.set_title('Income vs Expenses')
        
        # Add value labels on top of bars
        for i, v in enumerate(values):
            ax.text(i, v + 0.1, f"${v:.2f}", ha='center')
        
        # Add to layout
        chart = FigureCanvasKivyAgg(fig)
        self.income_vs_expenses_chart.add_widget(chart)
    
    def _update_transactions_over_time_chart(self, transactions):
        """Update the transactions over time chart."""
        self.transactions_over_time_chart.clear_widgets()
        
        # In a real implementation, we would group transactions by date
        # For now, we'll create a simple line chart with dummy data
        
        # Create figure
        fig, ax = plt.subplots()
        
        # Create line chart with dummy data
        dates = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        income = [500, 600, 550, 700, 650, 800]
        expenses = [300, 400, 350, 450, 500, 400]
        
        ax.plot(dates, income, marker='o', color='#00b366', label='Income')
        ax.plot(dates, expenses, marker='o', color='#e64d4d', label='Expenses')
        
        ax.set_xlabel('Month')
        ax.set_ylabel('Amount ($)')
        ax.set_title('Transactions Over Time')
        ax.legend()
        
        # Add to layout
        chart = FigureCanvasKivyAgg(fig)
        self.transactions_over_time_chart.add_widget(chart)
    
    def _on_period_filter_change(self, spinner, text):
        """Handle period filter change."""
        self.current_period = text
        self._update_charts()
    
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
        
        self._update_charts()
    
    def _on_export_pdf(self, instance):
        """Handle export to PDF button press."""
        # In a real implementation, this would export the report to PDF
        # For now, we'll just print a message
        print(f"Export to PDF for period: {self.current_period}, owner: {self.owner_spinner.text}")
    
    def _on_export_excel(self, instance):
        """Handle export to Excel button press."""
        # In a real implementation, this would export the report to Excel
        # For now, we'll just print a message
        print(f"Export to Excel for period: {self.current_period}, owner: {self.owner_spinner.text}")
    
    def _on_export_csv(self, instance):
        """Handle export to CSV button press."""
        # In a real implementation, this would export the report to CSV
        # For now, we'll just print a message
        print(f"Export to CSV for period: {self.current_period}, owner: {self.owner_spinner.text}")
