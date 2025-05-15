from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from functools import partial
from utils.db_utils import get_students_in_class, get_student_grade

class ClassDisplay(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.class_id = None
        self.dialog = None 

    def on_enter(self):
        self.clear_widgets()

        title_label = MDLabel(
            text=f"Class {self.class_id}",
            halign="center",
            font_style="H5",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": 0.5, "top": 1}
        )
        self.add_widget(title_label)

        scroll_view = MDScrollView(size_hint=(1, None), height=500, pos_hint={"center_x": 0.5, "center_y": 0.5})
        students_layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        students_layout.bind(minimum_height=students_layout.setter("height"))

        students = get_students_in_class(self.class_id)
        for student_id, student_code, student_name in students:
            student_item = OneLineListItem(
                text=f"{student_name} ({student_code})",
                on_release=partial(self.show_student_grade, student_code)
            )
            students_layout.add_widget(student_item)

        scroll_view.add_widget(students_layout)
        self.add_widget(scroll_view)

        back_button = MDRaisedButton(
            text="Back",
            size_hint=(0.3, None),
            height=50,
            pos_hint={"center_x": 0.5, "y": 0.05},
            on_release=self.go_back
        )
        self.add_widget(back_button)

    def show_student_grade(self, instance, student_code):
        grade = get_student_grade(student_code, subject_id=1)  #SỬA

        self.dialog = MDDialog(
            title="Student Grade",
            text=f"Student Code: {student_code}\nGrade: {grade}",
            buttons=[
                MDRaisedButton(
                    text="Close",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def go_back(self, instance):
        self.manager.current = "teacher_classes"