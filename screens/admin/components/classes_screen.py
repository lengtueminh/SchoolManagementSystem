from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.toast import toast
from utils.db_utils import get_all_classes
from .paginated_table import PaginatedTableView

class ClassesScreen:
    def __init__(self):
        self.dialog = None

    def show_table(self):
        classes_data = get_all_classes()
        if classes_data:
            content = PaginatedTableView(
                full_data=classes_data,
                headers=['Class ID', 'Class Name', 'Total Students', 'Action'],
                column_map={
                    'Class ID': 'id',
                    'Class Name': 'classname',
                    'Total Students': 'total_students'
                },
                search_fields=['classname'],
                column_widths={
                    'Class ID': 80,
                    'Class Name': 200,
                    'Total Students': 120,
                    'Action': 200
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Classes List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog),
                    MDRaisedButton(text="Add", on_release=lambda instance: content.add_class())
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
            toast("Could not load classes data.")

    def close_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss() 