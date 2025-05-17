from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from utils.db_utils import get_students_in_class_with_gpa, get_student_grade_details, get_subject_id_by_teacher_code, get_class_name_by_id

class ClassDisplay(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.class_id = None
        self.dialog = None 
        self.students_data = []
        self.sort_order = None  

    def on_enter(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        teacher_code = app.username
        subject_id = get_subject_id_by_teacher_code(teacher_code)

        self.students_data = get_students_in_class_with_gpa(self.class_id, subject_id)
        self.class_name = get_class_name_by_id(self.class_id)
  
        title_label = MDLabel(
            text=f"Class {self.class_name}",
            halign="center",
            font_style="H5",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": 0.5, "top": 1}
        )
        self.add_widget(title_label)

        menu_items = [
            {"text": "Sort GPA (ASC)", "on_release": lambda x="gpa_asc": self.sort_students(x)},
            {"text": "Sort GPA (DESC)", "on_release": lambda x="gpa_desc": self.sort_students(x)},
            {"text": "Sort by Name (A-Z)", "on_release": lambda x="name_asc": self.sort_students(x)},
            {"text": "Sort by Name (Z-A)", "on_release": lambda x="name_desc": self.sort_students(x)},
            {"text": "Clear Sort", "on_release": lambda x=None: self.sort_students(x)},
        ]

        self.menu = MDDropdownMenu(
            caller=title_label,
            items=menu_items,
            width_mult=3,
        )
        sort_button = MDRaisedButton(
            text="Sort Options",
            pos_hint={"center_x": 0.8, "top": 1},
            on_release=lambda x: self.menu.open()
        )
        self.add_widget(sort_button)

        self.scroll_view = MDScrollView(size_hint=(1, None), height=500, pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.students_layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        self.students_layout.bind(minimum_height=self.students_layout.setter("height"))
        self.scroll_view.add_widget(self.students_layout)
        self.add_widget(self.scroll_view)

        self.display_students()

        back_button = MDRaisedButton(
            text="Back",
            size_hint=(0.3, None),
            height=50,
            pos_hint={"center_x": 0.5, "y": 0.05},
            on_release=self.go_back
        )
        self.add_widget(back_button)

    def display_students(self):
        self.students_layout.clear_widgets()
        for student_id, student_code, student_name, gpa in self.students_data:
            gpa_display = f"{gpa:.2f}" if gpa is not None else "N/A"
            item = OneLineListItem(
                text=f"{student_name} ({student_code}) - GPA: {gpa_display}",
                on_release=lambda instance, code=student_code, name=student_name: self.show_student_grade(instance, code, name),
            )
            self.students_layout.add_widget(item)

    def sort_students(self, order):
        self.sort_order = order
        if order == "gpa_asc":
            self.students_data.sort(key=lambda x: (x[3] is None, x[3]))
        elif order == "gpa_desc":
            self.students_data.sort(key=lambda x: (x[3] is None, -x[3] if x[3] is not None else 0))
        elif order == "name_asc":
            self.students_data.sort(key=lambda x: x[2].lower())  # student_name
        elif order == "name_desc":
            self.students_data.sort(key=lambda x: x[2].lower(), reverse=True)
        self.display_students()
        self.menu.dismiss()


    def show_student_grade(self, instance, student_code, student_name):
        app = MDApp.get_running_app()
        teacher_code = app.username
        subject_id = get_subject_id_by_teacher_code(teacher_code)

        grade_details = get_student_grade_details(student_code, subject_id)
        if grade_details:
            subject_name, attendance, midterm, final, gpa = grade_details
            text = (
                f"[b]Student:[/b] {student_name} ({student_code})\n"
                f"[b]Subject:[/b] {subject_name}\n"
                f"[b]Attendance (10%):[/b] {attendance}\n"
                f"[b]Midterm (40%):[/b] {midterm}\n"
                f"[b]Final (50%):[/b] {final}\n"
                f"[b]GPA:[/b] {gpa}"
            )
        else:
            text = f"No grade information found for {student_name} ({student_code})."

        self.dialog = MDDialog(
            title="Student Grade Details",
            text=text,
            buttons=[MDRaisedButton(text="Close", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()

    def go_back(self, instance):
        self.manager.current = "teacher_classes"
        if self.dialog:
            self.dialog.dismiss()
