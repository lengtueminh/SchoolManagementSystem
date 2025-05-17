from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.toast import toast
from utils.db_utils import get_all_teachers
from .paginated_table import PaginatedTableView

class TeachersScreen:
    def __init__(self):
        self.dialog = None

    def show_table(self):
        teachers_data = get_all_teachers()
        if teachers_data:
            content = PaginatedTableView(
                full_data=teachers_data,
                headers=['ID', 'Code', 'Name', 'Subject', 'Email', 'Action'],
                column_map={
                    'ID': 'id',
                    'Code': 'code',
                    'Name': 'name',
                    'Subject': 'subjectname',
                    'Email': 'email'
                },
                search_fields=['name', 'code', 'subjectname', 'email'],
                column_widths={
                    'ID': 50,
                    'Code': 120,
                    'Name': 200,
                    'Subject': 150,
                    'Email': 250,
                    'Action': 150
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7,
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Teachers List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog),
                    MDRaisedButton(text="Add", on_release=lambda instance: content.add_teacher())
                ]
            )
            max_width = Window.width * 0.95
            if content.required_width > max_width:
                self.dialog.size_hint_x = None
                self.dialog.width = max_width
            else:
                self.dialog.size_hint_x = None
                self.dialog.width = content.required_width
            self.dialog.open()
        else:
            toast("Could not load teachers data.")

    def close_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss() 