# LEGACY: This Kivy dashboard is being deprecated and will be ported to the web (React/Vite).
# See documentation for migration plan and progress.

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.graphics import Rectangle, Color
import requests
from kivy.clock import Clock
from frontend.screens.subcontractors import SubcontractorsScreen
from frontend.screens.users import UsersScreen

# Placeholder icons (replace with custom/animated icons later)
ICON_MAP = {
    'dashboard': '🏠',
    'documents': '📄',
    'ledger': '💰',
    'projects': '📁',
    'companies': '🏢',
    'subcontractors': '🤝',
    'analytics': '📊',
    'review': '📝',
    'settings': '⚙️',
}

SECTIONS = [
    ('dashboard', 'Dashboard'),
    ('documents', 'Documents'),
    ('ledger', 'Ledger'),
    ('projects', 'Projects'),
    ('companies', 'Companies'),
    ('subcontractors', 'Subcontractors'),
    ('analytics', 'Analytics'),
    ('review', 'Review Tools'),
    ('settings', 'Settings'),
]

ICON_MAP['force_scan'] = '\U0001F50E'  # Magnifying glass
SECTIONS.insert(8, ('force_scan', 'Force Scan'))  # Insert before settings
ICON_MAP['paperless'] = '\U0001F4C4'  # Page icon
SECTIONS.insert(1, ('paperless', 'Paperless'))  # After dashboard
ICON_MAP['admin'] = '\U0001F4BC'  # Briefcase icon
SECTIONS.insert(2, ('admin', 'Admin'))  # After Paperless

class CommandCenterScreen(Screen):
    """
    Notion-style unified command center UI for Vanta Ledger
    Sidebar, top bar, and main content area. Black-and-white theme.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_section = 'dashboard'
        self.layout = BoxLayout(orientation='vertical')
        self.topbar = self.build_topbar()
        self.body = BoxLayout(orientation='horizontal')
        self.sidebar = self.build_sidebar()
        self.content_area = self.build_content_area(self.selected_section)
        self.body.add_widget(self.sidebar)
        self.body.add_widget(self.content_area)
        self.layout.add_widget(self.topbar)
        self.layout.add_widget(self.body)
        self.add_widget(self.layout)
        self.bind(size=self._update_bg, pos=self._update_bg)
        with self.canvas.before:
            # Subtle background image (replace 'bg.jpg' with your asset)
            Color(1, 1, 1, 0.04)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            # self.bg_img = Rectangle(source='frontend/assets/bg.jpg', pos=self.pos, size=self.size)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        # if hasattr(self, 'bg_img'):
        #     self.bg_img.pos = self.pos
        #     self.bg_img.size = self.size

    def build_topbar(self):
        bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=64, padding=[20, 10, 20, 10], spacing=24)
        bar.add_widget(Label(text='Vanta Ledger', font_size=28, color=(1,1,1,1), size_hint_x=0.22, bold=True))
        search = TextInput(hint_text='Search...', size_hint_x=0.38, background_color=(0.15,0.15,0.15,1), foreground_color=(1,1,1,1), font_size=18, padding=[12, 8, 12, 8])
        bar.add_widget(search)
        # Topbar icons
        icon_names = ['notifications', 'ai', 'profile']
        for icon in icon_names:
            bar.add_widget(Image(source=f'frontend/assets/icons/{icon}.png', size_hint_x=None, width=32, height=32, allow_stretch=True, keep_ratio=True))
        return bar

    def build_sidebar(self):
        sidebar = BoxLayout(orientation='vertical', size_hint_x=0.18, padding=[8, 20, 8, 20], spacing=8)
        sidebar.add_widget(Label(text='', size_hint_y=None, height=10))
        for key, label in SECTIONS:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=48, spacing=10)
            icon_path = f'frontend/assets/icons/{key}.png'
            row.add_widget(Image(source=icon_path, size_hint=(None, None), width=28, height=28, allow_stretch=True, keep_ratio=True))
            btn = ToggleButton(text=label, group='sidebar', size_hint_y=None, height=48, font_size=17, background_color=(0,0,0,0), color=(1,1,1,1),
                               background_normal='', background_down='', border=(0,0,0,0))
            if key == self.selected_section:
                btn.state = 'down'
                btn.background_color = (1,1,1,0.08)
            btn.bind(on_press=lambda btn, k=key: self.switch_section(k))
            row.add_widget(btn)
            sidebar.add_widget(row)
        sidebar.add_widget(Label(text='', size_hint_y=1))
        return sidebar

    def build_content_area(self, section):
        if hasattr(self, 'content_area') and self.content_area in self.body.children:
            self.body.remove_widget(self.content_area)
        content = BoxLayout(orientation='vertical', padding=30, spacing=20)
        if section == 'paperless':
            self.paperless_status_label = Label(text='Loading Paperless status...', font_size=20, color=(1,1,1,1))
            refresh_btn = Button(text='Refresh', size_hint=(None, None), size=(120, 40))
            refresh_btn.bind(on_press=self.refresh_paperless_status)
            self.paperless_spinner = Spinner(text='Loading...', size_hint=(None, None), size=(120, 40), pos_hint={'center_x': 0.5}, color=(0,0,0,1))
            self.paperless_spinner.opacity = 1
            content.add_widget(Label(text='\U0001F4C4  Paperless-ngx System', font_size=28, color=(1,1,1,1), bold=True))
            content.add_widget(self.paperless_status_label)
            content.add_widget(refresh_btn)
            content.add_widget(self.paperless_spinner)
            self.paperless_activity_box = BoxLayout(orientation='vertical', spacing=8)
            content.add_widget(self.paperless_activity_box)
            self.load_paperless_status()
            return content
        if section == 'force_scan':
            input_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
            self.fs_id_input = TextInput(hint_text='Document ID', size_hint_x=0.3)
            self.fs_path_input = TextInput(hint_text='File Path', size_hint_x=0.5)
            scan_btn = Button(text='Force Scan', size_hint_x=0.2)
            scan_btn.bind(on_press=self.trigger_force_scan)
            input_box.add_widget(self.fs_id_input)
            input_box.add_widget(self.fs_path_input)
            input_box.add_widget(scan_btn)
            content.add_widget(Label(text='\U0001F50E  Force Scan Failed Document', font_size=28, color=(1,1,1,1), bold=True))
            content.add_widget(input_box)
            self.fs_result_label = Label(text='Result will appear here.', font_size=16, color=(0.8,0.8,0.8,1))
            content.add_widget(self.fs_result_label)
            self.fs_spinner = Spinner(text='Loading...', size_hint=(None, None), size=(120, 40), pos_hint={'center_x': 0.5}, color=(0,0,0,1))
            self.fs_spinner.opacity = 0
            content.add_widget(self.fs_spinner)
            content.add_widget(Label(text='Recent Force Scans (coming soon)', font_size=14, color=(0.6,0.6,0.6,1)))
            return content
        if section == 'admin':
            self.admin_tabs = TabbedPanel(do_default_tab=False, tab_width=160)
            # --- Analytics/Dashboard Tab ---
            analytics_tab = TabbedPanelItem(text='Dashboard')
            analytics_layout = BoxLayout(orientation='vertical', spacing=20)
            # Summary widgets row (real data)
            summary_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, spacing=20)
            # Fetch real stats
            stats = self.fetch_admin_stats()
            summary_row.add_widget(Label(text=f'🏢\nCompanies\n{stats["companies"]}', halign='center', valign='middle', font_size=20, color=(1,1,1,1)))
            summary_row.add_widget(Label(text=f'📁\nProjects\n{stats["projects"]}', halign='center', valign='middle', font_size=20, color=(1,1,1,1)))
            summary_row.add_widget(Label(text=f'📄\nDocuments\n{stats["documents"]}', halign='center', valign='middle', font_size=20, color=(1,1,1,1)))
            summary_row.add_widget(Label(text=f'💰\nLedger Balance\nKES {stats["ledger_balance"]:,}', halign='center', valign='middle', font_size=20, color=(1,1,1,1)))
            analytics_layout.add_widget(summary_row)
            # Placeholder chart area (keep as mock for now)
            chart_area = BoxLayout(orientation='horizontal', size_hint_y=0.5, spacing=20)
            chart_area.add_widget(Label(text='[Mock Chart]\nIncome vs Expenses', halign='center', valign='middle', font_size=18, color=(0.8,0.8,0.8,1)))
            chart_area.add_widget(Label(text='[Mock Chart]\nProjects by Status', halign='center', valign='middle', font_size=18, color=(0.8,0.8,0.8,1)))
            analytics_layout.add_widget(chart_area)
            # Key metrics panel (real data)
            metrics_panel = BoxLayout(orientation='vertical', spacing=10)
            metrics_panel.add_widget(Label(text='Key Metrics', font_size=22, color=(1,1,1,1), bold=True))
            metrics_panel.add_widget(Label(text=f'- Pending Documents: {stats["pending_documents"]}', font_size=16, color=(1,1,1,1)))
            metrics_panel.add_widget(Label(text=f'- Failed Documents: {stats["failed_documents"]}', font_size=16, color=(1,1,1,1)))
            metrics_panel.add_widget(Label(text=f'- Active Users: {stats["users"]}', font_size=16, color=(1,1,1,1)))
            analytics_layout.add_widget(metrics_panel)
            analytics_tab.add_widget(analytics_layout)
            self.admin_tabs.add_widget(analytics_tab, index=0)
            # --- Companies Tab ---
            companies_tab = TabbedPanelItem(text='Companies')
            companies_layout = BoxLayout(orientation='vertical', spacing=10)
            self.companies_table = GridLayout(cols=4, size_hint_y=None, spacing=8)
            self.companies_table.bind(minimum_height=self.companies_table.setter('height'))
            # Table header
            self.companies_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
            self.companies_table.add_widget(Label(text='Name', bold=True, color=(1,1,1,1)))
            self.companies_table.add_widget(Label(text='Description', bold=True, color=(1,1,1,1)))
            self.companies_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
            # Loading spinner
            self.companies_spinner = Spinner(text='Loading...', size_hint=(None, None), size=(120, 40), pos_hint={'center_x': 0.5}, color=(0,0,0,1))
            companies_layout.add_widget(self.companies_spinner)
            companies_layout.add_widget(self.companies_table)
            # Add button
            add_btn = Button(text='Add Company', size_hint=(None, None), size=(140, 40))
            add_btn.bind(on_press=self.open_add_company_popup)
            companies_layout.add_widget(add_btn)
            self.companies_status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
            companies_layout.add_widget(self.companies_status_label)
            companies_tab.add_widget(companies_layout)
            self.admin_tabs.add_widget(companies_tab)
            # --- Projects Tab ---
            projects_tab = TabbedPanelItem(text='Projects')
            projects_layout = BoxLayout(orientation='vertical', spacing=10)
            self.projects_table = GridLayout(cols=5, size_hint_y=None, spacing=8)
            self.projects_table.bind(minimum_height=self.projects_table.setter('height'))
            # Table header
            self.projects_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
            self.projects_table.add_widget(Label(text='Name', bold=True, color=(1,1,1,1)))
            self.projects_table.add_widget(Label(text='Company', bold=True, color=(1,1,1,1)))
            self.projects_table.add_widget(Label(text='Description', bold=True, color=(1,1,1,1)))
            self.projects_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
            # Loading spinner
            self.projects_spinner = Spinner(text='Loading...', size_hint=(None, None), size=(120, 40), pos_hint={'center_x': 0.5}, color=(0,0,0,1))
            projects_layout.add_widget(self.projects_spinner)
            projects_layout.add_widget(self.projects_table)
            # Add button
            add_proj_btn = Button(text='Add Project', size_hint=(None, None), size=(140, 40))
            add_proj_btn.bind(on_press=self.open_add_project_popup)
            projects_layout.add_widget(add_proj_btn)
            self.projects_status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
            projects_layout.add_widget(self.projects_status_label)
            projects_tab.add_widget(projects_layout)
            self.admin_tabs.add_widget(projects_tab)
            # --- Documents Tab ---
            documents_tab = TabbedPanelItem(text='Documents')
            documents_layout = BoxLayout(orientation='vertical', spacing=10)
            self.documents_table = GridLayout(cols=6, size_hint_y=None, spacing=8)
            self.documents_table.bind(minimum_height=self.documents_table.setter('height'))
            # Table header
            self.documents_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
            self.documents_table.add_widget(Label(text='Title', bold=True, color=(1,1,1,1)))
            self.documents_table.add_widget(Label(text='Company', bold=True, color=(1,1,1,1)))
            self.documents_table.add_widget(Label(text='Project', bold=True, color=(1,1,1,1)))
            self.documents_table.add_widget(Label(text='Type', bold=True, color=(1,1,1,1)))
            self.documents_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
            # Loading spinner
            self.documents_spinner = Spinner(text='Loading...', size_hint=(None, None), size=(120, 40), pos_hint={'center_x': 0.5}, color=(0,0,0,1))
            documents_layout.add_widget(self.documents_spinner)
            documents_layout.add_widget(self.documents_table)
            # Add button
            add_doc_btn = Button(text='Add Document', size_hint=(None, None), size=(140, 40))
            add_doc_btn.bind(on_press=self.open_add_document_popup)
            documents_layout.add_widget(add_doc_btn)
            self.documents_status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
            documents_layout.add_widget(self.documents_status_label)
            documents_tab.add_widget(documents_layout)
            self.admin_tabs.add_widget(documents_tab)
            # --- Ledger Tab ---
            ledger_tab = TabbedPanelItem(text='Ledger')
            ledger_layout = BoxLayout(orientation='vertical', spacing=10)
            self.ledger_table = GridLayout(cols=8, size_hint_y=None, spacing=8)
            self.ledger_table.bind(minimum_height=self.ledger_table.setter('height'))
            # Table header
            self.ledger_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
            self.ledger_table.add_widget(Label(text='Type', bold=True, color=(1,1,1,1)))
            self.ledger_table.add_widget(Label(text='Amount', bold=True, color=(1,1,1,1)))
            self.ledger_table.add_widget(Label(text='Date', bold=True, color=(1,1,1,1)))
            self.ledger_table.add_widget(Label(text='Company', bold=True, color=(1,1,1,1)))
            self.ledger_table.add_widget(Label(text='Project', bold=True, color=(1,1,1,1)))
            self.ledger_table.add_widget(Label(text='Description', bold=True, color=(1,1,1,1)))
            self.ledger_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
            # Loading spinner
            self.ledger_spinner = Spinner(text='Loading...', size_hint=(None, None), size=(120, 40), pos_hint={'center_x': 0.5}, color=(0,0,0,1))
            ledger_layout.add_widget(self.ledger_spinner)
            ledger_layout.add_widget(self.ledger_table)
            # Add button
            add_ledger_btn = Button(text='Add Entry', size_hint=(None, None), size=(140, 40))
            add_ledger_btn.bind(on_press=self.open_add_ledger_popup)
            ledger_layout.add_widget(add_ledger_btn)
            self.ledger_status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
            ledger_layout.add_widget(self.ledger_status_label)
            ledger_tab.add_widget(ledger_layout)
            self.admin_tabs.add_widget(ledger_tab)
            # --- Subcontractors Tab ---
            subcontractors_tab = TabbedPanelItem(text='Subcontractors')
            subcontractors_screen = SubcontractorsScreen()
            subcontractors_tab.add_widget(subcontractors_screen)
            self.admin_tabs.add_widget(subcontractors_tab)
            # --- Users Tab ---
            users_tab = TabbedPanelItem(text='Users')
            users_screen = UsersScreen()
            users_tab.add_widget(users_screen)
            self.admin_tabs.add_widget(users_tab)
            # --- Security panel ---
            security_panel = BoxLayout(orientation='vertical', spacing=8, padding=[0,20,0,0])
            security_panel.add_widget(Label(text='Security & Permissions', font_size=18, color=(1,1,1,1), bold=True))
            # Real user/role management
            users = self.fetch_users()
            user_names = [u['name'] for u in users]
            user_dropdown = Spinner(text=user_names[0] if user_names else 'No Users', values=user_names, size_hint_x=0.3)
            selected_user = users[0] if users else None
            role_dropdown = Spinner(text=selected_user['role'] if selected_user else 'Select Role', values=['admin','bookkeeper','owner'], size_hint_x=0.2)
            def update_role(instance):
                if not selected_user:
                    return
                new_role = role_dropdown.text
                if new_role != selected_user['role']:
                    self.api_client.update_user(selected_user['id'], {'role': new_role})
                    show_toast(self, f"Role updated to {new_role}", type="success")
            update_role_btn = Button(text='Update Role', size_hint_x=0.2)
            update_role_btn.bind(on_press=update_role)
            role_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
            role_row.add_widget(Label(text='Select User:', size_hint_x=0.2, color=(0.8,0.8,0.8,1)))
            role_row.add_widget(user_dropdown)
            role_row.add_widget(Label(text='Role:', size_hint_x=0.1, color=(0.8,0.8,0.8,1)))
            role_row.add_widget(role_dropdown)
            role_row.add_widget(update_role_btn)
            security_panel.add_widget(role_row)
            # Permissions checkboxes (mock for now)
            perms_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
            perms_row.add_widget(Label(text='Permissions:', size_hint_x=0.2, color=(0.8,0.8,0.8,1)))
            for perm in ['user:create','user:read','user:update','user:delete','ledger:read','ledger:update']:
                cb = Button(text=perm, size_hint_x=0.13, background_color=(0.2,0.2,0.2,1), color=(1,1,1,1))
                perms_row.add_widget(cb)
            security_panel.add_widget(perms_row)
            # Audit log (mock for now)
            security_panel.add_widget(Label(text='Audit Log', font_size=16, color=(1,1,1,1), bold=True, padding=[0,10,0,0]))
            from kivy.uix.scrollview import ScrollView
            audit_scroll = ScrollView(size_hint=(1,0.25))
            audit_box = BoxLayout(orientation='vertical', size_hint_y=None)
            audit_box.bind(minimum_height=audit_box.setter('height'))
            mock_audit = [
                '2024-06-10 10:12: User Jane Mwangi updated role to admin',
                '2024-06-10 09:55: John Kamau created new ledger entry',
                '2024-06-10 09:30: Admin deleted user Peter Otieno',
                '2024-06-09 18:22: Jane Mwangi changed password',
                '2024-06-09 17:10: System backup completed',
            ]
            for entry in mock_audit:
                audit_box.add_widget(Label(text=entry, font_size=14, color=(0.7,0.9,1,1)))
            audit_scroll.add_widget(audit_box)
            security_panel.add_widget(audit_scroll)
            users_layout.add_widget(security_panel)
            users_tab.add_widget(users_layout)
            self.admin_tabs.add_widget(users_tab)
            # --- Notifications/Alerts Tab ---
            notifications_tab = TabbedPanelItem(text='Notifications')
            notifications_layout = BoxLayout(orientation='vertical', spacing=10)
            notifications_layout.add_widget(Label(text='Notifications & Alerts', font_size=22, color=(1,1,1,1), bold=True))
            # Mock notifications list
            mock_notifications = [
                {'type': 'alert', 'message': 'Paperless-ngx: 695 documents failed OCR.'},
                {'type': 'info', 'message': 'System backup completed successfully.'},
                {'type': 'warning', 'message': 'Ledger balance for Company 3 is negative.'},
                {'type': 'info', 'message': 'New user registered: Jane Mwangi.'},
                {'type': 'alert', 'message': 'Force scan required for 12 documents.'},
                {'type': 'info', 'message': 'AI risk analysis completed for 34 documents.'},
            ]
            for n in mock_notifications:
                color = (1,0.3,0.3,1) if n['type']=='alert' else (1,0.7,0,1) if n['type']=='warning' else (0.7,0.9,1,1)
                notifications_layout.add_widget(Label(text=f"[{n['type'].capitalize()}] {n['message']}", font_size=16, color=color))
            mark_all_btn = Button(text='Mark all as read', size_hint=(None, None), size=(180, 40))
            notifications_layout.add_widget(mark_all_btn)
            notifications_tab.add_widget(notifications_layout)
            self.admin_tabs.add_widget(notifications_tab, index=1)
            # --- AI/NLP Tab ---
            ai_tab = TabbedPanelItem(text='AI/NLP')
            ai_layout = BoxLayout(orientation='vertical', spacing=10)
            ai_layout.add_widget(Label(text='AI & NLP Analysis', font_size=22, color=(1,1,1,1), bold=True))
            # Mock search input and button
            search_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
            search_input = TextInput(hint_text='Semantic search (e.g., "Show all KRA compliance risks")')
            run_btn = Button(text='Run Analysis', size_hint=(None, None), size=(140, 40))
            search_row.add_widget(search_input)
            search_row.add_widget(run_btn)
            ai_layout.add_widget(search_row)
            # Mock analysis results
            ai_layout.add_widget(Label(text='[Mock] Document: Invoice_2023_Altan.pdf', font_size=16, color=(0.7,0.9,1,1)))
            ai_layout.add_widget(Label(text='Summary: Payment overdue. Risk: MEDIUM', font_size=15, color=(1,0.7,0,1)))
            ai_layout.add_widget(Label(text='[Mock] Document: CR12_Masterbuild.pdf', font_size=16, color=(0.7,0.9,1,1)))
            ai_layout.add_widget(Label(text='Summary: Company registration valid. Risk: LOW', font_size=15, color=(0.5,1,0.5,1)))
            ai_layout.add_widget(Label(text='[Mock] Document: Tender_2024_Senaxus.pdf', font_size=16, color=(0.7,0.9,1,1)))
            ai_layout.add_widget(Label(text='Summary: Missing KRA PIN. Risk: HIGH', font_size=15, color=(1,0.3,0.3,1)))
            ai_layout.add_widget(Label(text='[Mock] Semantic Search: "Show all documents with risk > MEDIUM"', font_size=16, color=(0.8,0.8,1,1)))
            ai_layout.add_widget(Label(text='- Tender_2024_Senaxus.pdf (HIGH)', font_size=15, color=(1,0.3,0.3,1)))
            ai_tab.add_widget(ai_layout)
            self.admin_tabs.add_widget(ai_tab, index=2)
            # --- Admin/Maintenance Tools Tab ---
            maint_tab = TabbedPanelItem(text='Admin Tools')
            maint_layout = BoxLayout(orientation='vertical', spacing=16)
            maint_layout.add_widget(Label(text='Admin & Maintenance Tools', font_size=22, color=(1,1,1,1), bold=True))
            # Mock system health
            maint_layout.add_widget(Label(text='System Health: 🟢 All systems operational', font_size=16, color=(0.5,1,0.5,1)))
            maint_layout.add_widget(Label(text='Last Backup: 2024-06-10 02:15', font_size=15, color=(0.7,0.9,1,1)))
            # Action buttons row
            actions_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=20)
            backup_btn = Button(text='Run Backup', size_hint=(None, None), size=(140, 40))
            restart_btn = Button(text='Restart Services', size_hint=(None, None), size=(160, 40))
            clear_cache_btn = Button(text='Clear Cache', size_hint=(None, None), size=(140, 40))
            actions_row.add_widget(backup_btn)
            actions_row.add_widget(restart_btn)
            actions_row.add_widget(clear_cache_btn)
            maint_layout.add_widget(actions_row)
            # Manual triggers
            maint_layout.add_widget(Label(text='Manual Triggers', font_size=18, color=(1,1,1,1), bold=True))
            trigger_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=20)
            force_scan_btn = Button(text='Force Scan All', size_hint=(None, None), size=(140, 40))
            reindex_btn = Button(text='Reindex Database', size_hint=(None, None), size=(160, 40))
            trigger_row.add_widget(force_scan_btn)
            trigger_row.add_widget(reindex_btn)
            maint_layout.add_widget(trigger_row)
            maint_tab.add_widget(maint_layout)
            self.admin_tabs.add_widget(maint_tab, index=3)
            # TODO: Add similar tabs for Documents, Ledger, Subcontractors, Users
            content.add_widget(Label(text='\U0001F4BC  Database Admin', font_size=28, color=(1,1,1,1), bold=True))
            content.add_widget(self.admin_tabs)
            self.load_companies()
            self.load_projects()
            self.load_documents()
            self.load_ledger()
            self.load_subcontractors()
            self.load_users()
            return content
        content.add_widget(Label(text=f"{ICON_MAP.get(section, '')}  {dict(SECTIONS)[section]}", font_size=32, color=(1,1,1,1), bold=True))
        content.add_widget(Label(text=f"This is the {dict(SECTIONS)[section]} panel. (Feature widgets go here)", font_size=18, color=(0.8,0.8,0.8,1)))
        return content

    def switch_section(self, section):
        self.selected_section = section
        new_content = self.build_content_area(section)
        self.body.add_widget(new_content)
        if hasattr(self, 'content_area') and self.content_area in self.body.children:
            self.body.remove_widget(self.content_area)
        self.content_area = new_content 

    def trigger_force_scan(self, instance):
        doc_id = self.fs_id_input.text.strip()
        file_path = self.fs_path_input.text.strip()
        self.fs_result_label.text = '⏳ Scanning...'
        self.fs_spinner.opacity = 1
        Clock.schedule_once(lambda dt: self._do_force_scan(doc_id, file_path), 0.1)

    def _do_force_scan(self, doc_id, file_path):
        try:
            url = 'http://localhost:8000/documents/force_scan'
            payload = {}
            if doc_id:
                payload['doc_id'] = int(doc_id)
            if file_path:
                payload['file_path'] = file_path
            response = requests.post(url, params=payload)
            if response.status_code == 200:
                data = response.json()
                result_text = f"✅ Scan complete\nConfidence: {data.get('confidence', 0):.1f}\nPages: {data.get('pages', 0)}\nError: {data.get('error', '')}\n---\n{text_preview(data.get('text', ''))}"
                self.fs_result_label.text = result_text
            else:
                self.fs_result_label.text = f"❌ Error: {response.status_code} {response.text}"
        except Exception as e:
            self.fs_result_label.text = f"❌ Exception: {e}"
        self.fs_spinner.opacity = 0

    def load_paperless_status(self):
        import threading
        def fetch():
            import requests
            try:
                url = 'http://localhost:8000/system/paperless_status'
                resp = requests.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    self.paperless_status_label.text = f"Status: {'🟢 Running' if data.get('running') else '🔴 Down'}\nQueued: {data.get('queued', 0)} | Processing: {data.get('processing', 0)} | Completed: {data.get('completed', 0)} | Failed: {data.get('failed', 0)}"
                    self.paperless_spinner.opacity = 0
                    # Show recent activity
                    self.paperless_activity_box.clear_widgets()
                    self.paperless_activity_box.add_widget(Label(text='Recent Activity:', font_size=18, color=(1,1,1,1)))
                    for doc in data.get('recent', []):
                        self.paperless_activity_box.add_widget(Label(text=f"{doc['id']}: {doc['title']} [{doc['status']}] {doc['created'][:10]}", font_size=15, color=(0.9,0.9,0.9,1)))
                else:
                    self.paperless_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
                    self.paperless_spinner.opacity = 0
            except Exception as e:
                self.paperless_status_label.text = f"❌ Exception: {e}"
                self.paperless_spinner.opacity = 0
        threading.Thread(target=fetch).start()

    def refresh_paperless_status(self, instance):
        self.paperless_spinner.opacity = 1
        self.load_paperless_status()

    def load_companies(self):
        self.companies_spinner.opacity = 1
        self.companies_table.clear_widgets()
        # Table header
        from kivy.uix.label import Label
        self.companies_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
        self.companies_table.add_widget(Label(text='Name', bold=True, color=(1,1,1,1)))
        self.companies_table.add_widget(Label(text='Description', bold=True, color=(1,1,1,1)))
        self.companies_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
        def fetch():
            try:
                url = 'http://localhost:8000/companies'
                resp = requests.get(url)
                if resp.status_code == 200:
                    companies = resp.json()
                    for c in companies:
                        self.companies_table.add_widget(Label(text=str(c['id']), color=(1,1,1,1)))
                        self.companies_table.add_widget(Label(text=c['name'], color=(1,1,1,1)))
                        self.companies_table.add_widget(Label(text=c.get('description',''), color=(1,1,1,1)))
                        actions = BoxLayout(orientation='horizontal', size_hint_x=None, width=120, spacing=4)
                        edit_btn = Button(text='Edit', size_hint_x=None, width=50)
                        edit_btn.bind(on_press=lambda btn, cid=c['id']: self.open_edit_company_popup(cid))
                        del_btn = Button(text='Delete', size_hint_x=None, width=60)
                        del_btn.bind(on_press=lambda btn, cid=c['id']: self.delete_company(cid))
                        actions.add_widget(edit_btn)
                        actions.add_widget(del_btn)
                        self.companies_table.add_widget(actions)
                    self.companies_status_label.text = f"Loaded {len(companies)} companies."
                else:
                    self.companies_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                self.companies_status_label.text = f"❌ Exception: {e}"
            self.companies_spinner.opacity = 0
        import threading
        threading.Thread(target=fetch).start()

    def open_add_company_popup(self, instance):
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        name_input = TextInput(hint_text='Name')
        desc_input = TextInput(hint_text='Description')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'name': name_input.text, 'description': desc_input.text}
            try:
                url = 'http://localhost:8000/companies'
                resp = requests.post(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Company added.'
                    self.load_companies()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Add', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Add Company', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(name_input)
        box.add_widget(desc_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Add Company', content=box, size_hint=(None, None), size=(400, 350))
        popup.open()

    def open_edit_company_popup(self, company_id):
        # Fetch company details
        try:
            url = f'http://localhost:8000/companies/{company_id}'
            resp = requests.get(url)
            if resp.status_code != 200:
                return
            company = resp.json()
        except Exception:
            return
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        name_input = TextInput(text=company['name'], hint_text='Name')
        desc_input = TextInput(text=company.get('description',''), hint_text='Description')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'name': name_input.text, 'description': desc_input.text}
            try:
                url = f'http://localhost:8000/companies/{company_id}'
                resp = requests.put(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Company updated.'
                    self.load_companies()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Save', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Edit Company', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(name_input)
        box.add_widget(desc_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Edit Company', content=box, size_hint=(None, None), size=(400, 350))
        popup.open()

    def delete_company(self, company_id):
        try:
            url = f'http://localhost:8000/companies/{company_id}'
            resp = requests.delete(url)
            if resp.status_code == 200:
                self.companies_status_label.text = '✅ Company deleted.'
                self.load_companies()
            else:
                self.companies_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
        except Exception as e:
            self.companies_status_label.text = f"❌ Exception: {e}"

    def load_projects(self):
        self.projects_spinner.opacity = 1
        self.projects_table.clear_widgets()
        # Table header
        from kivy.uix.label import Label
        self.projects_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
        self.projects_table.add_widget(Label(text='Name', bold=True, color=(1,1,1,1)))
        self.projects_table.add_widget(Label(text='Company', bold=True, color=(1,1,1,1)))
        self.projects_table.add_widget(Label(text='Description', bold=True, color=(1,1,1,1)))
        self.projects_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
        def fetch():
            try:
                url = 'http://localhost:8000/projects'
                resp = requests.get(url)
                if resp.status_code == 200:
                    projects = resp.json()
                    for p in projects:
                        self.projects_table.add_widget(Label(text=str(p['id']), color=(1,1,1,1)))
                        self.projects_table.add_widget(Label(text=p['name'], color=(1,1,1,1)))
                        # Fetch company name (assume company_id is present)
                        company_name = str(p.get('company_id', ''))
                        self.projects_table.add_widget(Label(text=company_name, color=(1,1,1,1)))
                        self.projects_table.add_widget(Label(text=p.get('description',''), color=(1,1,1,1)))
                        actions = BoxLayout(orientation='horizontal', size_hint_x=None, width=120, spacing=4)
                        edit_btn = Button(text='Edit', size_hint_x=None, width=50)
                        edit_btn.bind(on_press=lambda btn, pid=p['id']: self.open_edit_project_popup(pid))
                        del_btn = Button(text='Delete', size_hint_x=None, width=60)
                        del_btn.bind(on_press=lambda btn, pid=p['id']: self.delete_project(pid))
                        actions.add_widget(edit_btn)
                        actions.add_widget(del_btn)
                        self.projects_table.add_widget(actions)
                    self.projects_status_label.text = f"Loaded {len(projects)} projects."
                else:
                    self.projects_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                self.projects_status_label.text = f"❌ Exception: {e}"
            self.projects_spinner.opacity = 0
        import threading
        threading.Thread(target=fetch).start()

    def open_add_project_popup(self, instance):
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        name_input = TextInput(hint_text='Name')
        company_input = TextInput(hint_text='Company ID')
        desc_input = TextInput(hint_text='Description')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'name': name_input.text, 'company_id': int(company_input.text), 'description': desc_input.text}
            try:
                url = 'http://localhost:8000/projects'
                resp = requests.post(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Project added.'
                    self.load_projects()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Add', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Add Project', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(name_input)
        box.add_widget(company_input)
        box.add_widget(desc_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Add Project', content=box, size_hint=(None, None), size=(400, 400))
        popup.open()

    def open_edit_project_popup(self, project_id):
        # Fetch project details
        try:
            url = f'http://localhost:8000/projects/{project_id}'
            resp = requests.get(url)
            if resp.status_code != 200:
                return
            project = resp.json()
        except Exception:
            return
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        name_input = TextInput(text=project['name'], hint_text='Name')
        company_input = TextInput(text=str(project.get('company_id','')), hint_text='Company ID')
        desc_input = TextInput(text=project.get('description',''), hint_text='Description')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'name': name_input.text, 'company_id': int(company_input.text), 'description': desc_input.text}
            try:
                url = f'http://localhost:8000/projects/{project_id}'
                resp = requests.put(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Project updated.'
                    self.load_projects()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Save', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Edit Project', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(name_input)
        box.add_widget(company_input)
        box.add_widget(desc_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Edit Project', content=box, size_hint=(None, None), size=(400, 400))
        popup.open()

    def delete_project(self, project_id):
        try:
            url = f'http://localhost:8000/projects/{project_id}'
            resp = requests.delete(url)
            if resp.status_code == 200:
                self.projects_status_label.text = '✅ Project deleted.'
                self.load_projects()
            else:
                self.projects_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
        except Exception as e:
            self.projects_status_label.text = f"❌ Exception: {e}"

    def load_documents(self):
        self.documents_spinner.opacity = 1
        self.documents_table.clear_widgets()
        # Table header
        from kivy.uix.label import Label
        self.documents_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
        self.documents_table.add_widget(Label(text='Title', bold=True, color=(1,1,1,1)))
        self.documents_table.add_widget(Label(text='Company', bold=True, color=(1,1,1,1)))
        self.documents_table.add_widget(Label(text='Project', bold=True, color=(1,1,1,1)))
        self.documents_table.add_widget(Label(text='Type', bold=True, color=(1,1,1,1)))
        self.documents_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
        def fetch():
            try:
                url = 'http://localhost:8000/documents'
                resp = requests.get(url)
                if resp.status_code == 200:
                    documents = resp.json()
                    for d in documents:
                        self.documents_table.add_widget(Label(text=str(d['id']), color=(1,1,1,1)))
                        self.documents_table.add_widget(Label(text=d.get('title',''), color=(1,1,1,1)))
                        self.documents_table.add_widget(Label(text=str(d.get('company_id','')), color=(1,1,1,1)))
                        self.documents_table.add_widget(Label(text=str(d.get('project_id','')), color=(1,1,1,1)))
                        self.documents_table.add_widget(Label(text=d.get('doc_type',''), color=(1,1,1,1)))
                        actions = BoxLayout(orientation='horizontal', size_hint_x=None, width=120, spacing=4)
                        edit_btn = Button(text='Edit', size_hint_x=None, width=50)
                        edit_btn.bind(on_press=lambda btn, did=d['id']: self.open_edit_document_popup(did))
                        del_btn = Button(text='Delete', size_hint_x=None, width=60)
                        del_btn.bind(on_press=lambda btn, did=d['id']: self.delete_document(did))
                        actions.add_widget(edit_btn)
                        actions.add_widget(del_btn)
                        self.documents_table.add_widget(actions)
                    self.documents_status_label.text = f"Loaded {len(documents)} documents."
                else:
                    self.documents_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                self.documents_status_label.text = f"❌ Exception: {e}"
            self.documents_spinner.opacity = 0
        import threading
        threading.Thread(target=fetch).start()

    def open_add_document_popup(self, instance):
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        title_input = TextInput(hint_text='Title')
        company_input = TextInput(hint_text='Company ID')
        project_input = TextInput(hint_text='Project ID')
        type_input = TextInput(hint_text='Type')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'title': title_input.text, 'company_id': int(company_input.text), 'project_id': int(project_input.text), 'doc_type': type_input.text}
            try:
                url = 'http://localhost:8000/documents'
                resp = requests.post(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Document added.'
                    self.load_documents()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Add', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Add Document', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(title_input)
        box.add_widget(company_input)
        box.add_widget(project_input)
        box.add_widget(type_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Add Document', content=box, size_hint=(None, None), size=(400, 400))
        popup.open()

    def open_edit_document_popup(self, document_id):
        # Fetch document details
        try:
            url = f'http://localhost:8000/documents/{document_id}'
            resp = requests.get(url)
            if resp.status_code != 200:
                return
            document = resp.json()
        except Exception:
            return
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        title_input = TextInput(text=document.get('title',''), hint_text='Title')
        company_input = TextInput(text=str(document.get('company_id','')), hint_text='Company ID')
        project_input = TextInput(text=str(document.get('project_id','')), hint_text='Project ID')
        type_input = TextInput(text=document.get('doc_type',''), hint_text='Type')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'title': title_input.text, 'company_id': int(company_input.text), 'project_id': int(project_input.text), 'doc_type': type_input.text}
            try:
                url = f'http://localhost:8000/documents/{document_id}'
                resp = requests.put(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Document updated.'
                    self.load_documents()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Save', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Edit Document', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(title_input)
        box.add_widget(company_input)
        box.add_widget(project_input)
        box.add_widget(type_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Edit Document', content=box, size_hint=(None, None), size=(400, 400))
        popup.open()

    def delete_document(self, document_id):
        try:
            url = f'http://localhost:8000/documents/{document_id}'
            resp = requests.delete(url)
            if resp.status_code == 200:
                self.documents_status_label.text = '✅ Document deleted.'
                self.load_documents()
            else:
                self.documents_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
        except Exception as e:
            self.documents_status_label.text = f"❌ Exception: {e}"

    def load_ledger(self):
        self.ledger_spinner.opacity = 1
        self.ledger_table.clear_widgets()
        # Table header
        from kivy.uix.label import Label
        self.ledger_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
        self.ledger_table.add_widget(Label(text='Type', bold=True, color=(1,1,1,1)))
        self.ledger_table.add_widget(Label(text='Amount', bold=True, color=(1,1,1,1)))
        self.ledger_table.add_widget(Label(text='Date', bold=True, color=(1,1,1,1)))
        self.ledger_table.add_widget(Label(text='Company', bold=True, color=(1,1,1,1)))
        self.ledger_table.add_widget(Label(text='Project', bold=True, color=(1,1,1,1)))
        self.ledger_table.add_widget(Label(text='Description', bold=True, color=(1,1,1,1)))
        self.ledger_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
        def fetch():
            try:
                url = 'http://localhost:8000/ledger'
                resp = requests.get(url)
                if resp.status_code == 200:
                    entries = resp.json()
                    for e in entries:
                        self.ledger_table.add_widget(Label(text=str(e['id']), color=(1,1,1,1)))
                        self.ledger_table.add_widget(Label(text=e.get('type',''), color=(1,1,1,1)))
                        self.ledger_table.add_widget(Label(text=str(e.get('amount','')), color=(1,1,1,1)))
                        self.ledger_table.add_widget(Label(text=e.get('date',''), color=(1,1,1,1)))
                        self.ledger_table.add_widget(Label(text=str(e.get('company_id','')), color=(1,1,1,1)))
                        self.ledger_table.add_widget(Label(text=str(e.get('project_id','')), color=(1,1,1,1)))
                        self.ledger_table.add_widget(Label(text=e.get('description',''), color=(1,1,1,1)))
                        actions = BoxLayout(orientation='horizontal', size_hint_x=None, width=120, spacing=4)
                        edit_btn = Button(text='Edit', size_hint_x=None, width=50)
                        edit_btn.bind(on_press=lambda btn, lid=e['id']: self.open_edit_ledger_popup(lid))
                        del_btn = Button(text='Delete', size_hint_x=None, width=60)
                        del_btn.bind(on_press=lambda btn, lid=e['id']: self.delete_ledger(lid))
                        actions.add_widget(edit_btn)
                        actions.add_widget(del_btn)
                        self.ledger_table.add_widget(actions)
                    self.ledger_status_label.text = f"Loaded {len(entries)} ledger entries."
                else:
                    self.ledger_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                self.ledger_status_label.text = f"❌ Exception: {e}"
            self.ledger_spinner.opacity = 0
        import threading
        threading.Thread(target=fetch).start()

    def open_add_ledger_popup(self, instance):
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        type_input = TextInput(hint_text='Type')
        amount_input = TextInput(hint_text='Amount')
        date_input = TextInput(hint_text='Date (YYYY-MM-DD)')
        company_input = TextInput(hint_text='Company ID')
        project_input = TextInput(hint_text='Project ID')
        desc_input = TextInput(hint_text='Description')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'type': type_input.text, 'amount': float(amount_input.text), 'date': date_input.text, 'company_id': int(company_input.text), 'project_id': int(project_input.text), 'description': desc_input.text}
            try:
                url = 'http://localhost:8000/ledger'
                resp = requests.post(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Entry added.'
                    self.load_ledger()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Add', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Add Ledger Entry', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(type_input)
        box.add_widget(amount_input)
        box.add_widget(date_input)
        box.add_widget(company_input)
        box.add_widget(project_input)
        box.add_widget(desc_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Add Ledger Entry', content=box, size_hint=(None, None), size=(400, 500))
        popup.open()

    def open_edit_ledger_popup(self, ledger_id):
        # Fetch ledger entry details
        try:
            url = f'http://localhost:8000/ledger/{ledger_id}'
            resp = requests.get(url)
            if resp.status_code != 200:
                return
            entry = resp.json()
        except Exception:
            return
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        type_input = TextInput(text=entry.get('type',''), hint_text='Type')
        amount_input = TextInput(text=str(entry.get('amount','')), hint_text='Amount')
        date_input = TextInput(text=entry.get('date',''), hint_text='Date (YYYY-MM-DD)')
        company_input = TextInput(text=str(entry.get('company_id','')), hint_text='Company ID')
        project_input = TextInput(text=str(entry.get('project_id','')), hint_text='Project ID')
        desc_input = TextInput(text=entry.get('description',''), hint_text='Description')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'type': type_input.text, 'amount': float(amount_input.text), 'date': date_input.text, 'company_id': int(company_input.text), 'project_id': int(project_input.text), 'description': desc_input.text}
            try:
                url = f'http://localhost:8000/ledger/{ledger_id}'
                resp = requests.put(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Entry updated.'
                    self.load_ledger()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Save', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Edit Ledger Entry', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(type_input)
        box.add_widget(amount_input)
        box.add_widget(date_input)
        box.add_widget(company_input)
        box.add_widget(project_input)
        box.add_widget(desc_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Edit Ledger Entry', content=box, size_hint=(None, None), size=(400, 500))
        popup.open()

    def delete_ledger(self, ledger_id):
        try:
            url = f'http://localhost:8000/ledger/{ledger_id}'
            resp = requests.delete(url)
            if resp.status_code == 200:
                self.ledger_status_label.text = '✅ Entry deleted.'
                self.load_ledger()
            else:
                self.ledger_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
        except Exception as e:
            self.ledger_status_label.text = f"❌ Exception: {e}"

    def load_subcontractors(self):
        self.subcontractors_spinner.opacity = 1
        self.subcontractors_table.clear_widgets()
        # Table header
        from kivy.uix.label import Label
        self.subcontractors_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
        self.subcontractors_table.add_widget(Label(text='Name', bold=True, color=(1,1,1,1)))
        self.subcontractors_table.add_widget(Label(text='Company', bold=True, color=(1,1,1,1)))
        self.subcontractors_table.add_widget(Label(text='Contact', bold=True, color=(1,1,1,1)))
        self.subcontractors_table.add_widget(Label(text='Description', bold=True, color=(1,1,1,1)))
        self.subcontractors_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
        def fetch():
            try:
                url = 'http://localhost:8000/subcontractors'
                resp = requests.get(url)
                if resp.status_code == 200:
                    subs = resp.json()
                    for s in subs:
                        self.subcontractors_table.add_widget(Label(text=str(s['id']), color=(1,1,1,1)))
                        self.subcontractors_table.add_widget(Label(text=s.get('name',''), color=(1,1,1,1)))
                        self.subcontractors_table.add_widget(Label(text=str(s.get('company_id','')), color=(1,1,1,1)))
                        self.subcontractors_table.add_widget(Label(text=s.get('contact',''), color=(1,1,1,1)))
                        self.subcontractors_table.add_widget(Label(text=s.get('description',''), color=(1,1,1,1)))
                        actions = BoxLayout(orientation='horizontal', size_hint_x=None, width=120, spacing=4)
                        edit_btn = Button(text='Edit', size_hint_x=None, width=50)
                        edit_btn.bind(on_press=lambda btn, sid=s['id']: self.open_edit_subcontractor_popup(sid))
                        del_btn = Button(text='Delete', size_hint_x=None, width=60)
                        del_btn.bind(on_press=lambda btn, sid=s['id']: self.delete_subcontractor(sid))
                        actions.add_widget(edit_btn)
                        actions.add_widget(del_btn)
                        self.subcontractors_table.add_widget(actions)
                    self.subcontractors_status_label.text = f"Loaded {len(subs)} subcontractors."
                else:
                    self.subcontractors_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                self.subcontractors_status_label.text = f"❌ Exception: {e}"
            self.subcontractors_spinner.opacity = 0
        import threading
        threading.Thread(target=fetch).start()

    def open_add_subcontractor_popup(self, instance):
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        name_input = TextInput(hint_text='Name')
        company_input = TextInput(hint_text='Company ID')
        contact_input = TextInput(hint_text='Contact')
        desc_input = TextInput(hint_text='Description')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'name': name_input.text, 'company_id': int(company_input.text), 'contact': contact_input.text, 'description': desc_input.text}
            try:
                url = 'http://localhost:8000/subcontractors'
                resp = requests.post(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Subcontractor added.'
                    self.load_subcontractors()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Add', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Add Subcontractor', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(name_input)
        box.add_widget(company_input)
        box.add_widget(contact_input)
        box.add_widget(desc_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Add Subcontractor', content=box, size_hint=(None, None), size=(400, 400))
        popup.open()

    def open_edit_subcontractor_popup(self, subcontractor_id):
        # Fetch subcontractor details
        try:
            url = f'http://localhost:8000/subcontractors/{subcontractor_id}'
            resp = requests.get(url)
            if resp.status_code != 200:
                return
            sub = resp.json()
        except Exception:
            return
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        name_input = TextInput(text=sub.get('name',''), hint_text='Name')
        company_input = TextInput(text=str(sub.get('company_id','')), hint_text='Company ID')
        contact_input = TextInput(text=sub.get('contact',''), hint_text='Contact')
        desc_input = TextInput(text=sub.get('description',''), hint_text='Description')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'name': name_input.text, 'company_id': int(company_input.text), 'contact': contact_input.text, 'description': desc_input.text}
            try:
                url = f'http://localhost:8000/subcontractors/{subcontractor_id}'
                resp = requests.put(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ Subcontractor updated.'
                    self.load_subcontractors()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Save', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Edit Subcontractor', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(name_input)
        box.add_widget(company_input)
        box.add_widget(contact_input)
        box.add_widget(desc_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Edit Subcontractor', content=box, size_hint=(None, None), size=(400, 400))
        popup.open()

    def delete_subcontractor(self, subcontractor_id):
        try:
            url = f'http://localhost:8000/subcontractors/{subcontractor_id}'
            resp = requests.delete(url)
            if resp.status_code == 200:
                self.subcontractors_status_label.text = '✅ Subcontractor deleted.'
                self.load_subcontractors()
            else:
                self.subcontractors_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
        except Exception as e:
            self.subcontractors_status_label.text = f"❌ Exception: {e}"

    def load_users(self):
        self.users_spinner.opacity = 1
        self.users_table.clear_widgets()
        # Table header
        from kivy.uix.label import Label
        self.users_table.add_widget(Label(text='ID', bold=True, color=(1,1,1,1)))
        self.users_table.add_widget(Label(text='Username', bold=True, color=(1,1,1,1)))
        self.users_table.add_widget(Label(text='Name', bold=True, color=(1,1,1,1)))
        self.users_table.add_widget(Label(text='Email', bold=True, color=(1,1,1,1)))
        self.users_table.add_widget(Label(text='Role', bold=True, color=(1,1,1,1)))
        self.users_table.add_widget(Label(text='Active', bold=True, color=(1,1,1,1)))
        self.users_table.add_widget(Label(text='Actions', bold=True, color=(1,1,1,1)))
        # Loading spinner
        self.users_spinner = Spinner(text='Loading...', size_hint=(None, None), size=(120, 40), pos_hint={'center_x': 0.5}, color=(0,0,0,1))
        users_layout.add_widget(self.users_spinner)
        users_layout.add_widget(self.users_table)
        # Add button
        add_user_btn = Button(text='Add User', size_hint=(None, None), size=(120, 40))
        add_user_btn.bind(on_press=self.open_add_user_popup)
        users_layout.add_widget(add_user_btn)
        self.users_status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        users_layout.add_widget(self.users_status_label)
        # --- Security panel ---
        security_panel = BoxLayout(orientation='vertical', spacing=8, padding=[0,20,0,0])
        security_panel.add_widget(Label(text='Security & Permissions', font_size=18, color=(1,1,1,1), bold=True))
        # Real user/role management
        users = self.fetch_users()
        user_names = [u['name'] for u in users]
        user_dropdown = Spinner(text=user_names[0] if user_names else 'No Users', values=user_names, size_hint_x=0.3)
        selected_user = users[0] if users else None
        role_dropdown = Spinner(text=selected_user['role'] if selected_user else 'Select Role', values=['admin','bookkeeper','owner'], size_hint_x=0.2)
        def update_role(instance):
            if not selected_user:
                return
            new_role = role_dropdown.text
            if new_role != selected_user['role']:
                self.api_client.update_user(selected_user['id'], {'role': new_role})
                show_toast(self, f"Role updated to {new_role}", type="success")
        update_role_btn = Button(text='Update Role', size_hint_x=0.2)
        update_role_btn.bind(on_press=update_role)
        role_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        role_row.add_widget(Label(text='Select User:', size_hint_x=0.2, color=(0.8,0.8,0.8,1)))
        role_row.add_widget(user_dropdown)
        role_row.add_widget(Label(text='Role:', size_hint_x=0.1, color=(0.8,0.8,0.8,1)))
        role_row.add_widget(role_dropdown)
        role_row.add_widget(update_role_btn)
        security_panel.add_widget(role_row)
        # Permissions checkboxes (mock for now)
        perms_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        perms_row.add_widget(Label(text='Permissions:', size_hint_x=0.2, color=(0.8,0.8,0.8,1)))
        for perm in ['user:create','user:read','user:update','user:delete','ledger:read','ledger:update']:
            cb = Button(text=perm, size_hint_x=0.13, background_color=(0.2,0.2,0.2,1), color=(1,1,1,1))
            perms_row.add_widget(cb)
        security_panel.add_widget(perms_row)
        # Audit log (mock for now)
        security_panel.add_widget(Label(text='Audit Log', font_size=16, color=(1,1,1,1), bold=True, padding=[0,10,0,0]))
        from kivy.uix.scrollview import ScrollView
        audit_scroll = ScrollView(size_hint=(1,0.25))
        audit_box = BoxLayout(orientation='vertical', size_hint_y=None)
        audit_box.bind(minimum_height=audit_box.setter('height'))
        mock_audit = [
            '2024-06-10 10:12: User Jane Mwangi updated role to admin',
            '2024-06-10 09:55: John Kamau created new ledger entry',
            '2024-06-10 09:30: Admin deleted user Peter Otieno',
            '2024-06-09 18:22: Jane Mwangi changed password',
            '2024-06-09 17:10: System backup completed',
        ]
        for entry in mock_audit:
            audit_box.add_widget(Label(text=entry, font_size=14, color=(0.7,0.9,1,1)))
        audit_scroll.add_widget(audit_box)
        security_panel.add_widget(audit_scroll)
        users_layout.add_widget(security_panel)
        users_tab.add_widget(users_layout)
        self.admin_tabs.add_widget(users_tab)
        # --- Notifications/Alerts Tab ---
        notifications_tab = TabbedPanelItem(text='Notifications')
        notifications_layout = BoxLayout(orientation='vertical', spacing=10)
        notifications_layout.add_widget(Label(text='Notifications & Alerts', font_size=22, color=(1,1,1,1), bold=True))
        # Mock notifications list
        mock_notifications = [
            {'type': 'alert', 'message': 'Paperless-ngx: 695 documents failed OCR.'},
            {'type': 'info', 'message': 'System backup completed successfully.'},
            {'type': 'warning', 'message': 'Ledger balance for Company 3 is negative.'},
            {'type': 'info', 'message': 'New user registered: Jane Mwangi.'},
            {'type': 'alert', 'message': 'Force scan required for 12 documents.'},
            {'type': 'info', 'message': 'AI risk analysis completed for 34 documents.'},
        ]
        for n in mock_notifications:
            color = (1,0.3,0.3,1) if n['type']=='alert' else (1,0.7,0,1) if n['type']=='warning' else (0.7,0.9,1,1)
            notifications_layout.add_widget(Label(text=f"[{n['type'].capitalize()}] {n['message']}", font_size=16, color=color))
        mark_all_btn = Button(text='Mark all as read', size_hint=(None, None), size=(180, 40))
        notifications_layout.add_widget(mark_all_btn)
        notifications_tab.add_widget(notifications_layout)
        self.admin_tabs.add_widget(notifications_tab, index=1)
        # --- AI/NLP Tab ---
        ai_tab = TabbedPanelItem(text='AI/NLP')
        ai_layout = BoxLayout(orientation='vertical', spacing=10)
        ai_layout.add_widget(Label(text='AI & NLP Analysis', font_size=22, color=(1,1,1,1), bold=True))
        # Mock search input and button
        search_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        search_input = TextInput(hint_text='Semantic search (e.g., "Show all KRA compliance risks")')
        run_btn = Button(text='Run Analysis', size_hint=(None, None), size=(140, 40))
        search_row.add_widget(search_input)
        search_row.add_widget(run_btn)
        ai_layout.add_widget(search_row)
        # Mock analysis results
        ai_layout.add_widget(Label(text='[Mock] Document: Invoice_2023_Altan.pdf', font_size=16, color=(0.7,0.9,1,1)))
        ai_layout.add_widget(Label(text='Summary: Payment overdue. Risk: MEDIUM', font_size=15, color=(1,0.7,0,1)))
        ai_layout.add_widget(Label(text='[Mock] Document: CR12_Masterbuild.pdf', font_size=16, color=(0.7,0.9,1,1)))
        ai_layout.add_widget(Label(text='Summary: Company registration valid. Risk: LOW', font_size=15, color=(0.5,1,0.5,1)))
        ai_layout.add_widget(Label(text='[Mock] Document: Tender_2024_Senaxus.pdf', font_size=16, color=(0.7,0.9,1,1)))
        ai_layout.add_widget(Label(text='Summary: Missing KRA PIN. Risk: HIGH', font_size=15, color=(1,0.3,0.3,1)))
        ai_layout.add_widget(Label(text='[Mock] Semantic Search: "Show all documents with risk > MEDIUM"', font_size=16, color=(0.8,0.8,1,1)))
        ai_layout.add_widget(Label(text='- Tender_2024_Senaxus.pdf (HIGH)', font_size=15, color=(1,0.3,0.3,1)))
        ai_tab.add_widget(ai_layout)
        self.admin_tabs.add_widget(ai_tab, index=2)
        # --- Admin/Maintenance Tools Tab ---
        maint_tab = TabbedPanelItem(text='Admin Tools')
        maint_layout = BoxLayout(orientation='vertical', spacing=16)
        maint_layout.add_widget(Label(text='Admin & Maintenance Tools', font_size=22, color=(1,1,1,1), bold=True))
        # Mock system health
        maint_layout.add_widget(Label(text='System Health: 🟢 All systems operational', font_size=16, color=(0.5,1,0.5,1)))
        maint_layout.add_widget(Label(text='Last Backup: 2024-06-10 02:15', font_size=15, color=(0.7,0.9,1,1)))
        # Action buttons row
        actions_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=20)
        backup_btn = Button(text='Run Backup', size_hint=(None, None), size=(140, 40))
        restart_btn = Button(text='Restart Services', size_hint=(None, None), size=(160, 40))
        clear_cache_btn = Button(text='Clear Cache', size_hint=(None, None), size=(140, 40))
        actions_row.add_widget(backup_btn)
        actions_row.add_widget(restart_btn)
        actions_row.add_widget(clear_cache_btn)
        maint_layout.add_widget(actions_row)
        # Manual triggers
        maint_layout.add_widget(Label(text='Manual Triggers', font_size=18, color=(1,1,1,1), bold=True))
        trigger_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=20)
        force_scan_btn = Button(text='Force Scan All', size_hint=(None, None), size=(140, 40))
        reindex_btn = Button(text='Reindex Database', size_hint=(None, None), size=(160, 40))
        trigger_row.add_widget(force_scan_btn)
        trigger_row.add_widget(reindex_btn)
        maint_layout.add_widget(trigger_row)
        maint_tab.add_widget(maint_layout)
        self.admin_tabs.add_widget(maint_tab, index=3)
        # TODO: Add similar tabs for Documents, Ledger, Subcontractors, Users
        content.add_widget(Label(text='\U0001F4BC  Database Admin', font_size=28, color=(1,1,1,1), bold=True))
        content.add_widget(self.admin_tabs)
        self.load_companies()
        self.load_projects()
        self.load_documents()
        self.load_ledger()
        self.load_subcontractors()
        self.load_users()
        return content

    def open_add_user_popup(self, instance):
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        username_input = TextInput(hint_text='Username')
        name_input = TextInput(hint_text='Name')
        email_input = TextInput(hint_text='Email')
        role_input = TextInput(hint_text='Role')
        active_input = TextInput(hint_text='Active (Yes/No)')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'username': username_input.text, 'name': name_input.text, 'email': email_input.text, 'role': role_input.text, 'active': active_input.text.lower() == 'yes'}
            try:
                url = 'http://localhost:8000/users'
                resp = requests.post(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ User added.'
                    self.load_users()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Add', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Add User', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(username_input)
        box.add_widget(name_input)
        box.add_widget(email_input)
        box.add_widget(role_input)
        box.add_widget(active_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Add User', content=box, size_hint=(None, None), size=(400, 400))
        popup.open()

    def open_edit_user_popup(self, user_id):
        # Fetch user details
        try:
            url = f'http://localhost:8000/users/{user_id}'
            resp = requests.get(url)
            if resp.status_code != 200:
                return
            user = resp.json()
        except Exception:
            return
        box = BoxLayout(orientation='vertical', spacing=10, padding=20)
        username_input = TextInput(text=user.get('username',''), hint_text='Username')
        name_input = TextInput(text=user.get('name',''), hint_text='Name')
        email_input = TextInput(text=user.get('email',''), hint_text='Email')
        role_input = TextInput(text=user.get('role',''), hint_text='Role')
        active_input = TextInput(text='Yes' if user.get('active',True) else 'No', hint_text='Active (Yes/No)')
        status_label = Label(text='', font_size=14, color=(0.8,0.8,0.8,1))
        def submit(_):
            data = {'username': username_input.text, 'name': name_input.text, 'email': email_input.text, 'role': role_input.text, 'active': active_input.text.lower() == 'yes'}
            try:
                url = f'http://localhost:8000/users/{user_id}'
                resp = requests.put(url, json=data)
                if resp.status_code == 200:
                    status_label.text = '✅ User updated.'
                    self.load_users()
                    popup.dismiss()
                else:
                    status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
            except Exception as e:
                status_label.text = f"❌ Exception: {e}"
        submit_btn = Button(text='Save', size_hint_y=None, height=40)
        submit_btn.bind(on_press=submit)
        box.add_widget(Label(text='Edit User', font_size=20, color=(1,1,1,1), bold=True))
        box.add_widget(username_input)
        box.add_widget(name_input)
        box.add_widget(email_input)
        box.add_widget(role_input)
        box.add_widget(active_input)
        box.add_widget(submit_btn)
        box.add_widget(status_label)
        popup = Popup(title='Edit User', content=box, size_hint=(None, None), size=(400, 400))
        popup.open()

    def delete_user(self, user_id):
        try:
            url = f'http://localhost:8000/users/{user_id}'
            resp = requests.delete(url)
            if resp.status_code == 200:
                self.users_status_label.text = '✅ User deleted.'
                self.load_users()
            else:
                self.users_status_label.text = f"❌ Error: {resp.status_code} {resp.text}"
        except Exception as e:
            self.users_status_label.text = f"❌ Exception: {e}"

    def fetch_admin_stats(self):
        # Use the API client to fetch real stats for dashboard widgets
        stats = {
            'companies': 0,
            'projects': 0,
            'documents': 0,
            'users': 0,
            'ledger_balance': 0,
            'pending_documents': 0,
            'failed_documents': 0,
        }
        try:
            stats['companies'] = len(self.api_client.get_companies())
            stats['projects'] = len(self.api_client.get_projects())
            stats['documents'] = 0  # TODO: Wire to real document count if available
            stats['users'] = len(self.api_client.get_users())
            ledger_entries = self.api_client.get_ledger_entries()
            stats['ledger_balance'] = sum(e.get('amount', 0) if e.get('type') == 'income' else -e.get('amount', 0) for e in ledger_entries)
            # TODO: Wire pending/failed documents to real backend if available
            stats['pending_documents'] = 0
            stats['failed_documents'] = 0
        except Exception as e:
            print('Error fetching admin stats:', e)
        return stats
    def fetch_users(self):
        try:
            return self.api_client.get_users()
        except Exception as e:
            print('Error fetching users:', e)
            return []

# Helper to preview long text

def text_preview(text, maxlen=400):
    if not text:
        return '(No text extracted)'
    return text[:maxlen] + ('...' if len(text) > maxlen else '') 