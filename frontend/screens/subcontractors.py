"""
Subcontractors admin panel screen for Vanta Ledger Enhanced.

This module provides the subcontractors management screen for the admin section.
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from frontend.components.forms import TextInputField, FormActions
from frontend.components.dialogs import show_alert, show_confirm, show_toast

class SubcontractorCard(BoxLayout):
    subcontractor_id = ObjectProperty(None)
    name = ObjectProperty(None)
    contact = ObjectProperty(None)
    notes = ObjectProperty(None)
    on_edit = ObjectProperty(None)
    on_delete = ObjectProperty(None)

    def __init__(self, subcontractor_id, name, contact, notes, on_edit, on_delete, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=60, spacing=10, **kwargs)
        self.subcontractor_id = subcontractor_id
        self.name = name
        self.contact = contact
        self.notes = notes
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.label = Label(text=f"[b]{name}[/b]", markup=True, size_hint_x=0.3, color=(0,0,0,1))
        self.contact_label = Label(text=contact or '', size_hint_x=0.3, color=(0.2,0.2,0.2,1))
        self.notes_label = Label(text=notes or '', size_hint_x=0.3, color=(0.2,0.2,0.2,1))
        self.edit_btn = Button(text="Edit", size_hint_x=0.05, background_color=(0,0,0,1), color=(1,1,1,1))
        self.delete_btn = Button(text="Delete", size_hint_x=0.05, background_color=(1,1,1,1), color=(0,0,0,1))
        self.edit_btn.bind(on_press=lambda _: self.on_edit(self.subcontractor_id))
        self.delete_btn.bind(on_press=lambda _: self.on_delete(self.subcontractor_id))
        self.add_widget(self.label)
        self.add_widget(self.contact_label)
        self.add_widget(self.notes_label)
        self.add_widget(self.edit_btn)
        self.add_widget(self.delete_btn)

class SubcontractorForm(BoxLayout):
    subcontractor = ObjectProperty(None)
    on_save = ObjectProperty(None)
    on_cancel = ObjectProperty(None)

    def __init__(self, subcontractor=None, on_save=None, on_cancel=None, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=15, **kwargs)
        self.subcontractor = subcontractor
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.name_field = TextInputField(label_text="Name", hint_text="Enter subcontractor name", required=True)
        self.contact_field = TextInputField(label_text="Contact", hint_text="Enter contact info")
        self.notes_field = TextInputField(label_text="Notes", hint_text="Enter notes")
        self.form_actions = FormActions(submit_text="Save Subcontractor", cancel_text="Cancel", on_submit=self._on_submit, on_cancel=self._on_cancel)
        self.add_widget(self.name_field)
        self.add_widget(self.contact_field)
        self.add_widget(self.notes_field)
        self.add_widget(self.form_actions)
        if subcontractor:
            self.name_field.set_value(subcontractor.get('name', ''))
            self.contact_field.set_value(subcontractor.get('contact', ''))
            self.notes_field.set_value(subcontractor.get('notes', ''))
    def _on_submit(self):
        name_valid, name = self.name_field.validate()
        contact = self.contact_field.text
        notes = self.notes_field.text
        if not name_valid:
            return
        data = {'name': name, 'contact': contact, 'notes': notes}
        if self.on_save:
            self.on_save(data)
    def _on_cancel(self):
        if self.on_cancel:
            self.on_cancel()

class SubcontractorsScreen(Screen):
    api_client = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
        self.header_section = self._create_header_section()
        self.layout.add_widget(self.header_section)
        self.subcontractors_section = self._create_subcontractors_section()
        self.layout.add_widget(self.subcontractors_section)
        self.form_container = BoxLayout(orientation='vertical', size_hint=(1, 0))
        self.layout.add_widget(self.form_container)
        self.add_widget(self.layout)
        self.subcontractor_form = None
        self.editing_subcontractor_id = None
    def on_enter(self):
        if not self.api_client and hasattr(self.manager.parent.parent, 'api_client'):
            self.api_client = self.manager.parent.parent.api_client
        self.load_data()
    def load_data(self):
        if not self.api_client:
            return
        subcontractors = self.api_client.get_subcontractors()
        self._update_subcontractors_list(subcontractors)
    def _create_header_section(self):
        section = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        title = Label(text="Subcontractors", size_hint=(0.7, 1), halign='left', valign='middle', font_size='22sp', color=(0,0,0,1))
        title.bind(size=title.setter('text_size'))
        add_button = Button(text="+ Add Subcontractor", size_hint=(0.3, 0.8), pos_hint={'center_y': 0.5}, background_normal='', background_color=(0,0,0,1), color=(1,1,1,1))
        add_button.bind(on_press=self._on_add_subcontractor)
        section.add_widget(title)
        section.add_widget(add_button)
        return section
    def _create_subcontractors_section(self):
        section = BoxLayout(orientation='vertical', size_hint=(1, 0.9))
        self.subcontractors_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 1))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.subcontractors_layout)
        section.add_widget(scroll)
        return section
    def _update_subcontractors_list(self, subcontractors):
        self.subcontractors_layout.clear_widgets()
        if not subcontractors:
            empty_label = Label(text="No subcontractors found. Add your first subcontractor.", size_hint=(1, 1), halign='center', valign='middle', color=(0.5,0.5,0.5,1))
            empty_label.bind(size=empty_label.setter('text_size'))
            self.subcontractors_layout.add_widget(empty_label)
            return
        for subcontractor in subcontractors:
            card = SubcontractorCard(subcontractor_id=subcontractor.get('id',''), name=subcontractor.get('name',''), contact=subcontractor.get('contact',''), notes=subcontractor.get('notes',''), on_edit=self._on_edit_subcontractor, on_delete=self._on_delete_subcontractor)
            self.subcontractors_layout.add_widget(card)
    def _show_subcontractor_form(self, subcontractor=None):
        self._hide_subcontractor_form()
        self.subcontractor_form = SubcontractorForm(subcontractor=subcontractor, on_save=self._on_save_subcontractor, on_cancel=self._hide_subcontractor_form)
        self.form_container.add_widget(self.subcontractor_form)
        self.form_container.size_hint = (1, 0.8)
        self.subcontractors_section.size_hint = (1, 0)
    def _hide_subcontractor_form(self, *args):
        if self.subcontractor_form:
            self.form_container.remove_widget(self.subcontractor_form)
            self.subcontractor_form = None
        self.form_container.size_hint = (1, 0)
        self.subcontractors_section.size_hint = (1, 0.9)
        self.editing_subcontractor_id = None
    def _on_add_subcontractor(self, instance):
        self._show_subcontractor_form()
    def _on_edit_subcontractor(self, subcontractor_id):
        if not self.api_client:
            return
        subcontractor = self.api_client.get_subcontractor(subcontractor_id)
        if not subcontractor:
            show_alert("Error", "Subcontractor not found")
            return
        self.editing_subcontractor_id = subcontractor_id
        self._show_subcontractor_form(subcontractor)
    def _on_delete_subcontractor(self, subcontractor_id):
        if not self.api_client:
            return
        show_confirm(
            "Delete Subcontractor",
            "Are you sure you want to delete this subcontractor? This action cannot be undone.",
            confirm_text="Delete",
            cancel_text="Cancel",
            on_confirm=lambda: self._confirm_delete_subcontractor(subcontractor_id)
        )
    def _confirm_delete_subcontractor(self, subcontractor_id):
        if not self.api_client:
            return
        success = self.api_client.delete_subcontractor(subcontractor_id)
        if success:
            show_toast(self, "Subcontractor deleted successfully", type="success")
            self.load_data()
        else:
            show_alert("Error", "Failed to delete subcontractor")
    def _on_save_subcontractor(self, data):
        if not self.api_client:
            return
        if self.editing_subcontractor_id:
            success = self.api_client.update_subcontractor(self.editing_subcontractor_id, data)
            message = "Subcontractor updated successfully"
        else:
            success = self.api_client.create_subcontractor(data)
            message = "Subcontractor added successfully"
        if success:
            show_toast(self, message, type="success")
            self._hide_subcontractor_form()
            self.load_data()
        else:
            show_alert("Error", "Failed to save subcontractor") 