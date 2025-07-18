"""
Projects admin panel screen for Vanta Ledger Enhanced.

This module provides the projects management screen for the admin section.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty
from frontend.components.forms import TextInputField, AmountInputField, DateInputField, FormActions
from frontend.components.dialogs import show_alert, show_confirm, show_toast

class ProjectCard(BoxLayout):
    project_id = ObjectProperty(None)
    name = ObjectProperty(None)
    client = ObjectProperty(None)
    value = ObjectProperty(None)
    status = ObjectProperty(None)
    on_edit = ObjectProperty(None)
    on_delete = ObjectProperty(None)

    def __init__(self, project_id, name, client, value, status, on_edit, on_delete, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=60, spacing=10, **kwargs)
        self.project_id = project_id
        self.name = name
        self.client = client
        self.value = value
        self.status = status
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.label = Label(text=f"[b]{name}[/b]", markup=True, size_hint_x=0.25, color=(0,0,0,1))
        self.client_label = Label(text=client or '', size_hint_x=0.2, color=(0.2,0.2,0.2,1))
        self.value_label = Label(text=f"{value}" if value else '', size_hint_x=0.15, color=(0.2,0.2,0.2,1))
        self.status_label = Label(text=status or '', size_hint_x=0.2, color=(0.2,0.2,0.2,1))
        self.edit_btn = Button(text="Edit", size_hint_x=0.1, background_color=(0,0,0,1), color=(1,1,1,1))
        self.delete_btn = Button(text="Delete", size_hint_x=0.1, background_color=(1,1,1,1), color=(0,0,0,1))
        self.edit_btn.bind(on_press=lambda _: self.on_edit(self.project_id))
        self.delete_btn.bind(on_press=lambda _: self.on_delete(self.project_id))
        self.add_widget(self.label)
        self.add_widget(self.client_label)
        self.add_widget(self.value_label)
        self.add_widget(self.status_label)
        self.add_widget(self.edit_btn)
        self.add_widget(self.delete_btn)

class ProjectForm(BoxLayout):
    project = ObjectProperty(None)
    companies = ObjectProperty(None)
    on_save = ObjectProperty(None)
    on_cancel = ObjectProperty(None)

    def __init__(self, project=None, companies=None, on_save=None, on_cancel=None, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=15, **kwargs)
        self.project = project
        self.companies = companies or []
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.name_field = TextInputField(label_text="Project Name", hint_text="Enter project name", required=True)
        self.client_field = TextInputField(label_text="Client", hint_text="Enter client name")
        self.value_field = AmountInputField(label_text="Value", hint_text="Enter project value")
        self.start_date_field = DateInputField(label_text="Start Date", hint_text="YYYY-MM-DD")
        self.end_date_field = DateInputField(label_text="End Date", hint_text="YYYY-MM-DD")
        self.status_field = TextInputField(label_text="Status", hint_text="e.g. Ongoing, Complete")
        self.desc_field = TextInputField(label_text="Description", hint_text="Project description")
        self.company_spinner = Spinner(text='Select Company', values=[c['name'] for c in self.companies], size_hint_y=None, height=44)
        self.form_actions = FormActions(submit_text="Save Project", cancel_text="Cancel", on_submit=self._on_submit, on_cancel=self._on_cancel)
        self.add_widget(self.name_field)
        self.add_widget(self.client_field)
        self.add_widget(self.value_field)
        self.add_widget(self.start_date_field)
        self.add_widget(self.end_date_field)
        self.add_widget(self.status_field)
        self.add_widget(self.desc_field)
        self.add_widget(Label(text="Company", size_hint_y=None, height=24, color=(0,0,0,1)))
        self.add_widget(self.company_spinner)
        self.add_widget(self.form_actions)
        if project:
            self.name_field.set_value(project.get('name', ''))
            self.client_field.set_value(project.get('client', ''))
            self.value_field.set_value(str(project.get('value', '')))
            self.start_date_field.set_value(project.get('start_date', ''))
            self.end_date_field.set_value(project.get('end_date', ''))
            self.status_field.set_value(project.get('status', ''))
            self.desc_field.set_value(project.get('description', ''))
            if 'company' in project and project['company']:
                self.company_spinner.text = project['company'].get('name', 'Select Company')
    def _on_submit(self):
        name_valid, name = self.name_field.validate()
        value = self.value_field.text
        client = self.client_field.text
        start_date = self.start_date_field.text
        end_date = self.end_date_field.text
        status = self.status_field.text
        desc = self.desc_field.text
        company_name = self.company_spinner.text
        company_id = None
        for c in self.companies:
            if c['name'] == company_name:
                company_id = c['id']
                break
        if not name_valid or not company_id:
            show_alert("Validation Error", "Project name and company are required.")
            return
        data = {
            'name': name,
            'client': client,
            'value': float(value) if value else None,
            'start_date': start_date or None,
            'end_date': end_date or None,
            'status': status,
            'description': desc,
            'company_id': company_id
        }
        if self.on_save:
            self.on_save(data)
    def _on_cancel(self):
        if self.on_cancel:
            self.on_cancel()

class ProjectsScreen(Screen):
    api_client = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        self.header_section = self._create_header_section()
        self.layout.add_widget(self.header_section)
        self.projects_section = self._create_projects_section()
        self.layout.add_widget(self.projects_section)
        self.form_container = BoxLayout(orientation='vertical', size_hint=(1, 0))
        self.layout.add_widget(self.form_container)
        self.add_widget(self.layout)
        self.project_form = None
        self.editing_project_id = None
        self.companies = []
    def on_enter(self):
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        self.load_data()
    def load_data(self):
        if not self.api_client:
            return
        self.companies = self.api_client.get_companies()
        projects = self.api_client.get_projects()
        self._update_projects_list(projects)
    def _create_header_section(self):
        section = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        title = Label(text="Projects", size_hint=(0.7, 1), halign='left', valign='middle', font_size='22sp', color=(0,0,0,1))
        title.bind(size=title.setter('text_size'))
        add_button = Button(text="+ Add Project", size_hint=(0.3, 0.8), pos_hint={'center_y': 0.5}, background_normal='', background_color=(0,0,0,1), color=(1,1,1,1))
        add_button.bind(on_press=self._on_add_project)
        section.add_widget(title)
        section.add_widget(add_button)
        return section
    def _create_projects_section(self):
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.9))
        self.projects_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 1))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.projects_layout)
        section.add_widget(scroll)
        return section
    def _update_projects_list(self, projects):
        self.projects_layout.clear_widgets()
        if not projects:
            empty_label = Label(text="No projects found. Add your first project.", size_hint=(1, 1), halign='center', valign='middle', color=(0.5,0.5,0.5,1))
            empty_label.bind(size=empty_label.setter('text_size'))
            self.projects_layout.add_widget(empty_label)
            return
        for project in projects:
            card = ProjectCard(
                project_id=project.get('id',''),
                name=project.get('name',''),
                client=project.get('client',''),
                value=project.get('value',''),
                status=project.get('status',''),
                on_edit=self._on_edit_project,
                on_delete=self._on_delete_project
            )
            self.projects_layout.add_widget(card)
    def _show_project_form(self, project=None):
        self._hide_project_form()
        self.project_form = ProjectForm(project=project, companies=self.companies, on_save=self._on_save_project, on_cancel=self._hide_project_form)
        self.form_container.add_widget(self.project_form)
        self.form_container.size_hint = (1, 0.8)
        self.projects_section.size_hint = (1, 0)
    def _hide_project_form(self, *args):
        if self.project_form:
            self.form_container.remove_widget(self.project_form)
            self.project_form = None
        self.form_container.size_hint = (1, 0)
        self.projects_section.size_hint = (1, 0.9)
        self.editing_project_id = None
    def _on_add_project(self, instance):
        self._show_project_form()
    def _on_edit_project(self, project_id):
        if not self.api_client:
            return
        project = self.api_client.get_project(project_id)
        if not project:
            show_alert("Error", "Project not found")
            return
        self.editing_project_id = project_id
        self._show_project_form(project)
    def _on_delete_project(self, project_id):
        if not self.api_client:
            return
        show_confirm(
            "Delete Project",
            "Are you sure you want to delete this project? This action cannot be undone.",
            confirm_text="Delete",
            cancel_text="Cancel",
            on_confirm=lambda: self._confirm_delete_project(project_id)
        )
    def _confirm_delete_project(self, project_id):
        if not self.api_client:
            return
        success = self.api_client.delete_project(project_id)
        if success:
            show_toast(self, "Project deleted successfully", type="success")
            self.load_data()
        else:
            show_alert("Error", "Failed to delete project")
    def _on_save_project(self, data):
        if not self.api_client:
            return
        if self.editing_project_id:
            success = self.api_client.update_project(self.editing_project_id, data)
            message = "Project updated successfully"
        else:
            success = self.api_client.create_project(data)
            message = "Project added successfully"
        if success:
            show_toast(self, message, type="success")
            self._hide_project_form()
            self.load_data()
        else:
            show_alert("Error", "Failed to save project") 