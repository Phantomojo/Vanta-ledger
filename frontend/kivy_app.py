from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
import sqlite3
import csv
import os
from datetime import datetime

KV = '''
<VantaLedgerUI>:
    orientation: 'vertical'

    TabbedPanel:
        id: tab_panel
        do_default_tab: False
        disabled: False

        TabbedPanelItem:
            text: 'Transactions'
            BoxLayout:
                orientation: 'vertical'
                BoxLayout:
                    size_hint_y: None
                    height: '40dp'
                    Button:
                        text: 'Add'
                        on_press: root.show_add_transaction()
                    Button:
                        text: 'Edit'
                        on_press: root.show_edit_transaction()
                    Button:
                        text: 'Delete'
                        on_press: root.delete_transaction()
                    Button:
                        id: export_btn
                        text: 'Export'
                        on_press: root.export_transactions()

                ScrollView:
                    GridLayout:
                        id: transaction_list
                        cols: 1
                        size_hint_y: None
                        height: self.minimum_height

                GridLayout:
                    id: transaction_form
                    cols: 2
                    size_hint_y: None
                    height: '200dp'
                    padding: '10dp'
                    spacing: '10dp'

                    Label:
                        text: 'Type:'
                    TextInput:
                        id: type_input
                        multiline: False

                    Label:
                        text: 'Amount:'
                    TextInput:
                        id: amount_input
                        multiline: False
                        input_filter: 'float'

                    Label:
                        text: 'Description:'
                    TextInput:
                        id: description_input
                        multiline: False

                    Label:
                        text: 'Date (YYYY-MM-DD):'
                    TextInput:
                        id: date_input
                        multiline: False

                    Button:
                        id: save_btn
                        text: 'Save'
                        on_press: root.save_transaction()

                    Button:
                        id: cancel_btn
                        text: 'Cancel'
                        on_press: root.cancel_transaction()

        TabbedPanelItem:
            text: 'Summary'
            BoxLayout:
                orientation: 'vertical'
                Label:
                    id: summary_label
                    text: 'Ledger Summary will appear here.'
                    halign: 'left'
                    valign: 'top'
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1]

        TabbedPanelItem:
            text: 'Settings'
            BoxLayout:
                orientation: 'vertical'
                GridLayout:
                    cols: 2
                    padding: '10dp'
                    spacing: '10dp'

                    Label:
                        text: 'Default Currency:'
                    TextInput:
                        id: currency_input
                        multiline: False
                        text: 'USD'

                    Label:
                        text: 'Allow Negative Balance:'
                    CheckBox:
                        id: allow_negative_checkbox
                        active: False

                    Button:
                        text: 'Save Settings'
                        on_press: root.save_settings()
'''

Builder.load_string(KV)

class VantaLedgerUI(BoxLayout):
    tab_panel = ObjectProperty()
    transaction_list = ObjectProperty()
    type_input = ObjectProperty()
    amount_input = ObjectProperty()
    description_input = ObjectProperty()
    date_input = ObjectProperty()
    save_btn = ObjectProperty()
    cancel_btn = ObjectProperty()
    summary_label = ObjectProperty()
    currency_input = ObjectProperty()
    allow_negative_checkbox = ObjectProperty()
    export_btn = ObjectProperty()

    def on_kv_post(self, base_widget):
        # Assign ObjectProperty fields from ids to ensure proper binding
        self.tab_panel = self.ids.get('tab_panel')
        self.transaction_list = self.ids.get('transaction_list')
        self.type_input = self.ids.get('type_input')
        self.amount_input = self.ids.get('amount_input')
        self.description_input = self.ids.get('description_input')
        self.date_input = self.ids.get('date_input')
        self.save_btn = self.ids.get('save_btn')
        self.cancel_btn = self.ids.get('cancel_btn')
        self.summary_label = self.ids.get('summary_label')
        self.currency_input = self.ids.get('currency_input')
        self.allow_negative_checkbox = self.ids.get('allow_negative_checkbox')
        self.export_btn = self.ids.get('export_btn')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.editing_id = None
        self.db_path = "vanta_ledger.db"
        self.load_settings()
        self.update_ui_state()

    def update_ui_state(self):
        if self.tab_panel:
            self.tab_panel.disabled = False

    def load_transactions(self):
        self.clear_transaction_list()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, type, amount, description, date FROM transactions ORDER BY date DESC")
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                btn = Button(text=f"{row[0]} | {row[1]} | {row[2]:.2f} | {row[3]} | {row[4]}", size_hint_y=None, height=40)
                btn.bind(on_press=self.select_transaction)
                btn.transaction_id = row[0]
                self.transaction_list.add_widget(btn)
        except Exception as e:
            self.show_popup("Error", f"Failed to load transactions: {e}")

    def clear_transaction_list(self):
        self.transaction_list.clear_widgets()

    def select_transaction(self, instance):
        self.editing_id = instance.transaction_id
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT type, amount, description, date FROM transactions WHERE id=?", (self.editing_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                self.type_input.text = row[0]
                self.amount_input.text = str(row[1])
                self.description_input.text = row[2]
                self.date_input.text = row[3]
        except Exception as e:
            self.show_popup("Error", f"Failed to load transaction: {e}")

    def clear_transaction_form(self):
        self.editing_id = None
        self.type_input.text = ""
        self.amount_input.text = ""
        self.description_input.text = ""
        self.date_input.text = ""

    def show_add_transaction(self):
        self.clear_transaction_form()

    def show_edit_transaction(self):
        if self.editing_id is None:
            self.show_popup("Warning", "Please select a transaction to edit")
            return

    def save_transaction(self):
        if not self.type_input or not self.amount_input or not self.description_input or not self.date_input:
            self.show_popup("Error", "UI elements not properly initialized")
            return
        type_ = self.type_input.text.strip() if self.type_input.text else ""
        amount = self.amount_input.text.strip() if self.amount_input.text else ""
        description = self.description_input.text.strip() if self.description_input.text else ""
        date = self.date_input.text.strip() if self.date_input.text else ""

        if not type_ or not amount or not description or not date:
            self.show_popup("Warning", "Please fill in all fields")
            return
        try:
            amount_val = float(amount)
        except ValueError:
            self.show_popup("Warning", "Amount must be a number")
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            self.show_popup("Warning", "Date must be in YYYY-MM-DD format")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if self.editing_id is None:
                cursor.execute(
                    "INSERT INTO transactions (type, amount, description, date) VALUES (?, ?, ?, ?)",
                    (type_, amount_val, description, date),
                )
            else:
                cursor.execute(
                    "UPDATE transactions SET type=?, amount=?, description=?, date=? WHERE id=?",
                    (type_, amount_val, description, date, self.editing_id),
                )
            conn.commit()
            conn.close()
            self.load_transactions()
            self.clear_transaction_form()
        except Exception as e:
            self.show_popup("Error", f"Failed to save transaction: {e}")

    def delete_transaction(self):
        if self.editing_id is None:
            self.show_popup("Warning", "Please select a transaction to delete")
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id=?", (self.editing_id,))
            conn.commit()
            conn.close()
            self.load_transactions()
            self.clear_transaction_form()
        except Exception as e:
            self.show_popup("Error", f"Failed to delete transaction: {e}")

    def load_summary(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='sale'")
            total_sales = cursor.fetchone()[0] or 0
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expenditure'")
            total_expenses = cursor.fetchone()[0] or 0
            profit_loss = total_sales - total_expenses
            summary_text = (
                f"Total Sales: {self.currency} {total_sales:.2f}\\n"
                f"Total Expenses: {self.currency} {total_expenses:.2f}\\n"
                f"Profit/Loss: {self.currency} {profit_loss:.2f}\\n"
            )
            self.summary_label.text = summary_text
            conn.close()
        except Exception as e:
            self.show_popup("Error", f"Failed to load summary: {e}")

    def load_settings(self):
        self.currency = "USD"
        self.allow_negative_balance = False

    def save_settings(self):
        try:
            currency_text = getattr(self.currency_input, 'text', None)
            if currency_text:
                self.currency = currency_text.strip().upper() or "USD"
            else:
                self.currency = "USD"
            allow_negative = getattr(self.allow_negative_checkbox, 'active', None)
            if allow_negative is not None:
                self.allow_negative_balance = allow_negative
            else:
                self.allow_negative_balance = False
            self.show_popup("Settings", "Settings saved")
        except Exception as e:
            self.show_popup("Error", f"Failed to save settings: {e}")

    def export_transactions(self):
        file_path = os.path.join(os.path.expanduser("~"), "transactions_export.csv")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, type, amount, description, date FROM transactions ORDER BY date DESC")
            rows = cursor.fetchall()
            conn.close()
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Type", "Amount", "Description", "Date"])
                writer.writerows(rows)
            self.show_popup("Export", f"Transactions exported to {file_path}")
        except Exception as e:
            self.show_popup("Error", f"Failed to export transactions: {e}")

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(400, 200))
        popup.open()

class VantaLedgerApp(App):
    def build(self):
        return VantaLedgerUI()

if __name__ == '__main__':
    VantaLedgerApp().run()
