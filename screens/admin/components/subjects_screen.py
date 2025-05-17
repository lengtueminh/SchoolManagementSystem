from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.toast import toast
from utils.db_utils import get_all_subjects
from .paginated_table import PaginatedTableView

class SubjectsScreen:
    def __init__(self):
        self.dialog = None

    def show_table(self):
        subjects_data = get_all_subjects()
        if subjects_data:
            content = PaginatedTableView(
                full_data=subjects_data,
                headers=['Subject ID', 'Subject Name', 'Total Teachers', 'Action'],
                column_map={
                    'Subject ID': 'subjectid',
                    'Subject Name': 'subjectname',
                    'Total Teachers': 'total_teachers'
                },
                search_fields=['subjectname'],
                column_widths={
                    'Subject ID': 80,
                    'Subject Name': 250,
                    'Total Teachers': 120,
                    'Action': 200
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Subjects List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog),
                    MDRaisedButton(text="Add", on_release=lambda instance: content.add_subject())
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
            toast("Could not load subjects data.")

    def close_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss() 