"""
Charts component for Vanta Ledger Enhanced.

This module provides reusable chart components for data visualization.
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, StringProperty, NumericProperty, ObjectProperty
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

class BarChart(BoxLayout):
    """
    Bar chart component for visualizing categorical data.
    
    Features:
    - Customizable colors and labels
    - Value labels on bars
    - Responsive sizing
    """
    
    data = ListProperty([])
    categories = ListProperty([])
    title = StringProperty("")
    x_label = StringProperty("")
    y_label = StringProperty("")
    colors = ListProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the bar chart."""
        super(BarChart, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Default colors if none provided
        if not self.colors:
            self.colors = ['#00b366', '#e64d4d', '#3399ff', '#ff9933', '#9966ff']
        
        # Create initial chart
        self._update_chart()
        
        # Bind properties for updates
        self.bind(data=self._update_chart)
        self.bind(categories=self._update_chart)
        self.bind(title=self._update_chart)
        self.bind(x_label=self._update_chart)
        self.bind(y_label=self._update_chart)
        self.bind(colors=self._update_chart)
    
    def _update_chart(self, *args):
        """Update the chart with current data."""
        self.clear_widgets()
        
        if not self.data or not self.categories or len(self.data) != len(self.categories):
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
        
        # Create bar chart
        bars = ax.bar(
            self.categories,
            self.data,
            color=self.colors[:len(self.categories)]
        )
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{height:.1f}',
                ha='center',
                va='bottom'
            )
        
        # Add labels and title
        if self.x_label:
            ax.set_xlabel(self.x_label)
        if self.y_label:
            ax.set_ylabel(self.y_label)
        if self.title:
            ax.set_title(self.title)
        
        # Adjust layout
        fig.tight_layout()
        
        # Add to layout
        chart = FigureCanvasKivyAgg(fig)
        self.add_widget(chart)


class LineChart(BoxLayout):
    """
    Line chart component for visualizing trends over time.
    
    Features:
    - Multiple series support
    - Customizable colors and labels
    - Legend for multiple series
    - Responsive sizing
    """
    
    data_series = ListProperty([])
    labels = ListProperty([])
    series_names = ListProperty([])
    title = StringProperty("")
    x_label = StringProperty("")
    y_label = StringProperty("")
    colors = ListProperty(None)
    
    def __init__(self, **kwargs):
        """Initialize the line chart."""
        super(LineChart, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Default colors if none provided
        if not self.colors:
            self.colors = ['#00b366', '#e64d4d', '#3399ff', '#ff9933', '#9966ff']
        
        # Create initial chart
        self._update_chart()
        
        # Bind properties for updates
        self.bind(data_series=self._update_chart)
        self.bind(labels=self._update_chart)
        self.bind(series_names=self._update_chart)
        self.bind(title=self._update_chart)
        self.bind(x_label=self._update_chart)
        self.bind(y_label=self._update_chart)
        self.bind(colors=self._update_chart)
    
    def _update_chart(self, *args):
        """Update the chart with current data."""
        self.clear_widgets()
        
        if not self.data_series or not self.labels:
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
        
        # Plot each series
        for i, series in enumerate(self.data_series):
            if len(series) != len(self.labels):
                continue
                
            color = self.colors[i % len(self.colors)]
            name = self.series_names[i] if i < len(self.series_names) else f"Series {i+1}"
            
            ax.plot(
                self.labels,
                series,
                marker='o',
                color=color,
                label=name
            )
        
        # Add labels and title
        if self.x_label:
            ax.set_xlabel(self.x_label)
        if self.y_label:
            ax.set_ylabel(self.y_label)
        if self.title:
            ax.set_title(self.title)
        
        # Add legend if multiple series
        if len(self.data_series) > 1:
            ax.legend()
        
        # Adjust layout
        fig.tight_layout()
        
        # Add to layout
        chart = FigureCanvasKivyAgg(fig)
        self.add_widget(chart)


class PieChart(BoxLayout):
    """
    Pie chart component for visualizing proportions.
    
    Features:
    - Percentage labels
    - Customizable colors
    - Explode slices for emphasis
    - Legend with categories
    """
    
    data = ListProperty([])
    categories = ListProperty([])
    title = StringProperty("")
    colors = ListProperty(None)
    explode = ListProperty([])
    
    def __init__(self, **kwargs):
        """Initialize the pie chart."""
        super(PieChart, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Default colors if none provided
        if not self.colors:
            self.colors = ['#00b366', '#e64d4d', '#3399ff', '#ff9933', '#9966ff']
        
        # Create initial chart
        self._update_chart()
        
        # Bind properties for updates
        self.bind(data=self._update_chart)
        self.bind(categories=self._update_chart)
        self.bind(title=self._update_chart)
        self.bind(colors=self._update_chart)
        self.bind(explode=self._update_chart)
    
    def _update_chart(self, *args):
        """Update the chart with current data."""
        self.clear_widgets()
        
        if not self.data or not self.categories or len(self.data) != len(self.categories):
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=80)
        
        # Create explode array if needed
        explode = self.explode if self.explode and len(self.explode) == len(self.data) else None
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            self.data,
            explode=explode,
            labels=self.categories,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90,
            colors=self.colors[:len(self.categories)]
        )
        
        # Style the percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
        
        # Add title
        if self.title:
            ax.set_title(self.title)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Adjust layout
        fig.tight_layout()
        
        # Add to layout
        chart = FigureCanvasKivyAgg(fig)
        self.add_widget(chart)


class FinancialSummaryChart(BoxLayout):
    """
    Combined chart for financial summary visualization.
    
    Features:
    - Income vs Expenses bar chart
    - Balance trend line chart
    - Customizable time period
    """
    
    income_data = ListProperty([])
    expense_data = ListProperty([])
    balance_data = ListProperty([])
    time_labels = ListProperty([])
    title = StringProperty("Financial Summary")
    
    def __init__(self, **kwargs):
        """Initialize the financial summary chart."""
        super(FinancialSummaryChart, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create initial chart
        self._update_chart()
        
        # Bind properties for updates
        self.bind(income_data=self._update_chart)
        self.bind(expense_data=self._update_chart)
        self.bind(balance_data=self._update_chart)
        self.bind(time_labels=self._update_chart)
        self.bind(title=self._update_chart)
    
    def _update_chart(self, *args):
        """Update the chart with current data."""
        self.clear_widgets()
        
        if not self.income_data or not self.expense_data or not self.time_labels:
            return
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), dpi=80)
        
        # Income vs Expenses bar chart
        x = range(len(self.time_labels))
        width = 0.35
        
        income_bars = ax1.bar(
            [i - width/2 for i in x],
            self.income_data,
            width,
            label='Income',
            color='#00b366'
        )
        
        expense_bars = ax1.bar(
            [i + width/2 for i in x],
            self.expense_data,
            width,
            label='Expenses',
            color='#e64d4d'
        )
        
        # Add labels and title to first subplot
        ax1.set_xlabel('Period')
        ax1.set_ylabel('Amount')
        ax1.set_title('Income vs Expenses')
        ax1.set_xticks(x)
        ax1.set_xticklabels(self.time_labels)
        ax1.legend()
        
        # Balance trend line chart
        if self.balance_data:
            ax2.plot(
                self.time_labels,
                self.balance_data,
                marker='o',
                color='#3399ff',
                label='Balance'
            )
            
            # Add horizontal line at zero
            ax2.axhline(y=0, color='#999999', linestyle='-', alpha=0.3)
            
            # Color the area based on positive/negative values
            for i in range(len(self.balance_data) - 1):
                if self.balance_data[i] >= 0 and self.balance_data[i+1] >= 0:
                    ax2.fill_between(
                        self.time_labels[i:i+2],
                        self.balance_data[i:i+2],
                        0,
                        alpha=0.2,
                        color='#00b366'
                    )
                elif self.balance_data[i] < 0 and self.balance_data[i+1] < 0:
                    ax2.fill_between(
                        self.time_labels[i:i+2],
                        self.balance_data[i:i+2],
                        0,
                        alpha=0.2,
                        color='#e64d4d'
                    )
        
        # Add labels and title to second subplot
        ax2.set_xlabel('Period')
        ax2.set_ylabel('Balance')
        ax2.set_title('Balance Trend')
        
        # Add main title
        fig.suptitle(self.title, fontsize=16)
        
        # Adjust layout
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        
        # Add to layout
        chart = FigureCanvasKivyAgg(fig)
        self.add_widget(chart)
