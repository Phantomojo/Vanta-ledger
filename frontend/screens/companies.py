"""
Companies admin panel screen for Vanta Ledger Enhanced.

This module provides the companies management screen for the admin section.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty

from frontend.components.forms import TextInputField, FormActions
from frontend.components.dialogs import show_alert, show_confirm, show_toast

class CompanyCard(BoxLayout):
    company_id = ObjectProperty(None)
    name = ObjectProperty(None)
    description = ObjectProperty(None)
    on_edit = ObjectProperty(None)
    on_delete = ObjectProperty(None)

    def __init__(self, company_id, name, description, on_edit, on_delete, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=60, spacing=10, **kwargs)
        self.company_id = company_id
        self.name = name
        self.description = description
        self.on_edit = on_edit
        self.on_delete = on_delete

        self.label = Label(text=f"[b]{name}[/b]", markup=True, size_hint_x=0.4, color=(0,0,0,1))
        self.desc_label = Label(text=description or '', size_hint_x=0.4, color=(0.2,0.2,0.2,1))
        self.edit_btn = Button(text="Edit", size_hint_x=0.1, background_color=(0,0,0,1), color=(1,1,1,1))
        self.delete_btn = Button(text="Delete", size_hint_x=0.1, background_color=(1,1,1,1), color=(0,0,0,1))
        self.edit_btn.bind(on_press=lambda _: self.on_edit(self.company_id))
        self.delete_btn.bind(on_press=lambda _: self.on_delete(self.company_id))
        self.add_widget(self.label)
        self.add_widget(self.desc_label)
        self.add_widget(self.edit_btn)
        self.add_widget(self.delete_btn)

class CompanyForm(BoxLayout):
    company = ObjectProperty(None)
    on_save = ObjectProperty(None)
    on_cancel = ObjectProperty(None)

    def __init__(self, company=None, on_save=None, on_cancel=None, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=15, **kwargs)
        self.company = company
        self.on_save = on_save
        self.on_cancel = on_cancel

        self.name_field = TextInputField(label_text="Company Name", hint_text="Enter company name", required=True)
        self.desc_field = TextInputField(label_text="Description", hint_text="Enter company description")
        self.form_actions = FormActions(submit_text="Save Company", cancel_text="Cancel", on_submit=self._on_submit, on_cancel=self._on_cancel)
        self.add_widget(self.name_field)
        self.add_widget(self.desc_field)
        self.add_widget(self.form_actions)
        if company:
            self.name_field.set_value(company.get('name', ''))
            self.desc_field.set_value(company.get('description', ''))

    def _on_submit(self):
        name_valid, name = self.name_field.validate()
        desc = self.desc_field.text
        if not name_valid:
            return
        data = {'name': name, 'description': desc}
        if self.on_save:
            self.on_save(data)

    def _on_cancel(self):
        if self.on_cancel:
            self.on_cancel()

class CompaniesScreen(Screen):
    api_client = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        self.header_section = self._create_header_section()
        self.layout.add_widget(self.header_section)
        self.companies_section = self._create_companies_section()
        self.layout.add_widget(self.companies_section)
        self.form_container = BoxLayout(orientation='vertical', size_hint=(1, 0))
        self.layout.add_widget(self.form_container)
        self.add_widget(self.layout)
        self.company_form = None
        self.editing_company_id = None
    def on_enter(self):
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        self.load_data()
    def load_data(self):
        if not self.api_client:
            return
        companies = self.api_client.get_companies()
        self._update_companies_list(companies)
    def _create_header_section(self):
        section = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        title = Label(text="Companies", size_hint=(0.7, 1), halign='left', valign='middle', font_size='22sp', color=(0,0,0,1))
        title.bind(size=title.setter('text_size'))
        add_button = Button(text="+ Add Company", size_hint=(0.3, 0.8), pos_hint={'center_y': 0.5}, background_normal='', background_color=(0,0,0,1), color=(1,1,1,1))
        add_button.bind(on_press=self._on_add_company)
        section.add_widget(title)
        section.add_widget(add_button)
        return section
    def _create_companies_section(self):
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.9))
        self.companies_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 1))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.companies_layout)
        section.add_widget(scroll)
        return section
    def _update_companies_list(self, companies):
        self.companies_layout.clear_widgets()
        if not companies:
            empty_label = Label(text="No companies found. Add your first company.", size_hint=(1, 1), halign='center', valign='middle', color=(0.5,0.5,0.5,1))
            empty_label.bind(size=empty_label.setter('text_size'))
            self.companies_layout.add_widget(empty_label)
            return
        for company in companies:
            card = CompanyCard(company_id=company.get('id',''), name=company.get('name',''), description=company.get('description',''), on_edit=self._on_edit_company, on_delete=self._on_delete_company)
            self.companies_layout.add_widget(card)
    def _show_company_form(self, company=None):
        self._hide_company_form()
        self.company_form = CompanyForm(company=company, on_save=self._on_save_company, on_cancel=self._hide_company_form)
        self.form_container.add_widget(self.company_form)
        self.form_container.size_hint = (1, 0.8)
        self.companies_section.size_hint = (1, 0)
    def _hide_company_form(self, *args):
        if self.company_form:
            self.form_container.remove_widget(self.company_form)
            self.company_form = None
        self.form_container.size_hint = (1, 0)
        self.companies_section.size_hint = (1, 0.9)
        self.editing_company_id = None
    def _on_add_company(self, instance):
        self._show_company_form()
    def _on_edit_company(self, company_id):
        if not self.api_client:
            return
        company = self.api_client.get_company(company_id)
        if not company:
            show_alert("Error", "Company not found")
            return
        self.editing_company_id = company_id
        self._show_company_form(company)
    def _on_delete_company(self, company_id):
        if not self.api_client:
            return
        show_confirm(
            "Delete Company",
            "Are you sure you want to delete this company? This action cannot be undone.",
            confirm_text="Delete",
            cancel_text="Cancel",
            on_confirm=lambda: self._confirm_delete_company(company_id)
        )
    def _confirm_delete_company(self, company_id):
        if not self.api_client:
            return
        success = self.api_client.delete_company(company_id)
        if success:
            show_toast(self, "Company deleted successfully", type="success")
            self.load_data()
        else:
            show_alert("Error", "Failed to delete company")
    def _on_save_company(self, data):
        if not self.api_client:
            return
        if self.editing_company_id:
            success = self.api_client.update_company(self.editing_company_id, data)
            message = "Company updated successfully"
        else:
            success = self.api_client.create_company(data)
            message = "Company added successfully"
        if success:
            show_toast(self, message, type="success")
            self._hide_company_form()
            self.load_data()
        else:
            show_alert("Error", "Failed to save company") 