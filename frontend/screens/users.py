"""
Users admin panel screen for Vanta Ledger Enhanced.

This module provides the users management screen for the admin section.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.properties import ObjectProperty
from frontend.components.forms import TextInputField, FormActions
from frontend.components.dialogs import show_alert, show_confirm, show_toast

class UserCard(BoxLayout):
    user_id = ObjectProperty(None)
    name = ObjectProperty(None)
    email = ObjectProperty(None)
    role = ObjectProperty(None)
    on_edit = ObjectProperty(None)
    on_delete = ObjectProperty(None)

    def __init__(self, user_id, name, email, role, on_edit, on_delete, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=60, spacing=10, **kwargs)
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.label = Label(text=f"[b]{name}[/b]", markup=True, size_hint_x=0.3, color=(0,0,0,1))
        self.email_label = Label(text=email or '', size_hint_x=0.3, color=(0.2,0.2,0.2,1))
        self.role_label = Label(text=role or '', size_hint_x=0.2, color=(0.2,0.2,0.2,1))
        self.edit_btn = Button(text="Edit", size_hint_x=0.1, background_color=(0,0,0,1), color=(1,1,1,1))
        self.delete_btn = Button(text="Delete", size_hint_x=0.1, background_color=(1,1,1,1), color=(0,0,0,1))
        self.edit_btn.bind(on_press=lambda _: self.on_edit(self.user_id))
        self.delete_btn.bind(on_press=lambda _: self.on_delete(self.user_id))
        self.add_widget(self.label)
        self.add_widget(self.email_label)
        self.add_widget(self.role_label)
        self.add_widget(self.edit_btn)
        self.add_widget(self.delete_btn)

class UserForm(BoxLayout):
    user = ObjectProperty(None)
    on_save = ObjectProperty(None)
    on_cancel = ObjectProperty(None)

    def __init__(self, user=None, on_save=None, on_cancel=None, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=15, **kwargs)
        self.user = user
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.name_field = TextInputField(label_text="Name", hint_text="Enter user name", required=True)
        self.email_field = TextInputField(label_text="Email", hint_text="Enter email", required=True)
        self.password_field = TextInputField(label_text="Password", hint_text="Enter password", required=True)
        self.role_spinner = Spinner(text='Select Role', values=['admin', 'bookkeeper', 'owner'], size_hint_y=None, height=44)
        self.form_actions = FormActions(submit_text="Save User", cancel_text="Cancel", on_submit=self._on_submit, on_cancel=self._on_cancel)
        self.add_widget(self.name_field)
        self.add_widget(self.email_field)
        self.add_widget(self.password_field)
        self.add_widget(Label(text="Role", size_hint_y=None, height=24, color=(0,0,0,1)))
        self.add_widget(self.role_spinner)
        self.add_widget(self.form_actions)
        if user:
            self.name_field.set_value(user.get('name', ''))
            self.email_field.set_value(user.get('email', ''))
            self.role_spinner.text = user.get('role', 'Select Role')
    def _on_submit(self):
        name_valid, name = self.name_field.validate()
        email_valid, email = self.email_field.validate()
        password = self.password_field.text
        role = self.role_spinner.text
        if not (name_valid and email_valid and password and role != 'Select Role'):
            show_alert("Validation Error", "All fields are required.")
            return
        data = {'name': name, 'email': email, 'password': password, 'role': role}
        if self.on_save:
            self.on_save(data)
    def _on_cancel(self):
        if self.on_cancel:
            self.on_cancel()

class UsersScreen(Screen):
    api_client = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        self.header_section = self._create_header_section()
        self.layout.add_widget(self.header_section)
        self.users_section = self._create_users_section()
        self.layout.add_widget(self.users_section)
        self.form_container = BoxLayout(orientation='vertical', size_hint=(1, 0))
        self.layout.add_widget(self.form_container)
        self.add_widget(self.layout)
        self.user_form = None
        self.editing_user_id = None
    def on_enter(self):
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        self.load_data()
    def load_data(self):
        if not self.api_client:
            return
        users = self.api_client.get_users()
        self._update_users_list(users)
    def _create_header_section(self):
        section = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        title = Label(text="Users", size_hint=(0.7, 1), halign='left', valign='middle', font_size='22sp', color=(0,0,0,1))
        title.bind(size=title.setter('text_size'))
        add_button = Button(text="+ Add User", size_hint=(0.3, 0.8), pos_hint={'center_y': 0.5}, background_normal='', background_color=(0,0,0,1), color=(1,1,1,1))
        add_button.bind(on_press=self._on_add_user)
        section.add_widget(title)
        section.add_widget(add_button)
        return section
    def _create_users_section(self):
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.9))
        self.users_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 1))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.users_layout)
        section.add_widget(scroll)
        return section
    def _update_users_list(self, users):
        self.users_layout.clear_widgets()
        if not users:
            empty_label = Label(text="No users found. Add your first user.", size_hint=(1, 1), halign='center', valign='middle', color=(0.5,0.5,0.5,1))
            empty_label.bind(size=empty_label.setter('text_size'))
            self.users_layout.add_widget(empty_label)
            return
        for user in users:
            card = UserCard(user_id=user.get('id',''), name=user.get('name',''), email=user.get('email',''), role=user.get('role',''), on_edit=self._on_edit_user, on_delete=self._on_delete_user)
            self.users_layout.add_widget(card)
    def _show_user_form(self, user=None):
        self._hide_user_form()
        self.user_form = UserForm(user=user, on_save=self._on_save_user, on_cancel=self._hide_user_form)
        self.form_container.add_widget(self.user_form)
        self.form_container.size_hint = (1, 0.8)
        self.users_section.size_hint = (1, 0)
    def _hide_user_form(self, *args):
        if self.user_form:
            self.form_container.remove_widget(self.user_form)
            self.user_form = None
        self.form_container.size_hint = (1, 0)
        self.users_section.size_hint = (1, 0.9)
        self.editing_user_id = None
    def _on_add_user(self, instance):
        self._show_user_form()
    def _on_edit_user(self, user_id):
        if not self.api_client:
            return
        user = self.api_client.get_user(user_id)
        if not user:
            show_alert("Error", "User not found")
            return
        self.editing_user_id = user_id
        self._show_user_form(user)
    def _on_delete_user(self, user_id):
        if not self.api_client:
            return
        show_confirm(
            "Delete User",
            "Are you sure you want to delete this user? This action cannot be undone.",
            confirm_text="Delete",
            cancel_text="Cancel",
            on_confirm=lambda: self._confirm_delete_user(user_id)
        )
    def _confirm_delete_user(self, user_id):
        if not self.api_client:
            return
        success = self.api_client.delete_user(user_id)
        if success:
            show_toast(self, "User deleted successfully", type="success")
            self.load_data()
        else:
            show_alert("Error", "Failed to delete user")
    def _on_save_user(self, data):
        if not self.api_client:
            return
        if self.editing_user_id:
            success = self.api_client.update_user(self.editing_user_id, data)
            message = "User updated successfully"
        else:
            success = self.api_client.create_user(data)
            message = "User added successfully"
        if success:
            show_toast(self, message, type="success")
            self._hide_user_form()
            self.load_data()
        else:
            show_alert("Error", "Failed to save user") 