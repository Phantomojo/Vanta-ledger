from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Rectangle, Color
from kivy.properties import ObjectProperty

# Placeholder for backend integration
FAILED_DOCS_SAMPLE = {
    'all': [
        {'id': 1, 'title': 'Invoice 2023.pdf', 'type': 'ocr_failure'},
        {'id': 2, 'title': 'Bank Statement.pdf', 'type': 'password_protected'},
        {'id': 3, 'title': 'Award Letter.docx', 'type': 'duplicate'},
        {'id': 4, 'title': 'Tax Cert.pdf', 'type': 'other'},
    ],
    'duplicates': [
        {'id': 3, 'title': 'Award Letter.docx', 'type': 'duplicate'},
    ],
    'password_protected': [
        {'id': 2, 'title': 'Bank Statement.pdf', 'type': 'password_protected'},
    ],
    'other': [
        {'id': 1, 'title': 'Invoice 2023.pdf', 'type': 'ocr_failure'},
        {'id': 4, 'title': 'Tax Cert.pdf', 'type': 'other'},
    ]
}

ICON_MAP = {
    'ocr_failure': '🔍',
    'duplicate': '⏸️',
    'password_protected': '🔒',
    'other': '⚠️',
}

class FailedDocumentsScreen(Screen):
    """
    Failed Document Review & Recovery Tool
    Black-and-white, high-contrast style. Custom icons and background.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tab_panel = TabbedPanel(do_default_tab=False)
        self.tab_panel.size_hint = (1, 1)
        self.tab_panel.background_color = (0, 0, 0, 1)  # Black background
        self.tab_panel.tab_width = 180
        self.build_tabs()
        self.add_widget(self.tab_panel)

    def build_tabs(self):
        for tab_name, label in [
            ('all', 'All'),
            ('duplicates', 'Duplicates'),
            ('password_protected', 'Password-Protected'),
            ('other', 'Other Failures'),
        ]:
            tab = TabbedPanelItem(text=label)
            tab.add_widget(self.build_doc_list(tab_name))
            self.tab_panel.add_widget(tab)

    def build_doc_list(self, category):
        docs = FAILED_DOCS_SAMPLE.get(category, [])
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, size_hint_y=None, spacing=10)
        grid.bind(minimum_height=grid.setter('height'))
        for doc in docs:
            icon = ICON_MAP.get(doc['type'], '⚠️')
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=20)
            row.add_widget(Label(text=icon, font_size=28, size_hint_x=0.1, color=(1,1,1,1)))
            row.add_widget(Label(text=doc['title'], font_size=18, color=(1,1,1,1)))
            if doc['type'] == 'password_protected':
                row.add_widget(Label(text='Password-Protected', color=(1,0.2,0.2,1), font_size=14))
            elif doc['type'] == 'duplicate':
                row.add_widget(Label(text='Duplicate', color=(0.7,0.7,0.7,1), font_size=14))
            else:
                retry_btn = Button(text='Retry', size_hint_x=0.2, background_color=(1,1,1,1), color=(0,0,0,1))
                retry_btn.bind(on_press=lambda btn, doc_id=doc['id']: self.retry_doc(doc_id))
                row.add_widget(retry_btn)
            grid.add_widget(row)
        scroll.add_widget(grid)
        layout.add_widget(scroll)
        export_btn = Button(text='Export/Report', size_hint=(1, None), height=40, background_color=(0,0,0,1), color=(1,1,1,1))
        export_btn.bind(on_press=self.export_report)
        layout.add_widget(export_btn)
        return layout

    def retry_doc(self, doc_id):
        # TODO: Integrate with backend retry logic
        print(f"Retrying document ID {doc_id}")

    def export_report(self, *args):
        # TODO: Integrate with backend report export
        print("Exporting failure report...")

    def on_pre_enter(self):
        # Draw black-and-white background (placeholder, replace with image asset later)
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            Rectangle(pos=self.pos, size=self.size)
        # TODO: Replace with background image asset for final version

# To use: add FailedDocumentsScreen to your ScreenManager in the app 