from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from utils.db_utils import get_teacher_name, get_teacher_details, get_teacher_classes

class TeacherHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets() 

        app = MDApp.get_running_app()
        teacher_code = app.username
        teacher_name = get_teacher_name(teacher_code)
        teacher_details = get_teacher_details(teacher_code)

        welcome_label = MDLabel(
            text=f"Welcome back, {teacher_name} ({teacher_code})!",
            halign="center",
            pos_hint={"center_y": 0.95},
            font_style="H6"
        )

        teacher_info = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None, height=80)
        teacher_info.add_widget(MDLabel(text=f"Name: {teacher_details['teacher_name']}", halign="center"))
        teacher_info.add_widget(MDLabel(text=f"Email: {teacher_details['email']}", halign="center"))

        buttons_layout = BoxLayout(
            orientation="vertical", 
            spacing=15, 
            size_hint=(0.6, None), 
            height=300, 
            pos_hint={"center_x": 0.5, "center_y": 0.45}
        )

        detail_button = MDRaisedButton(
            text="Teacher's Details", 
            # on_release=self.view_details
        )

        classes_button = MDRaisedButton(
            text="View Classes",
            # pos_hint={"center_x": 0.5},
            on_release=self.view_classes
        )

        grade_button = MDRaisedButton(
            text="Grade Submission",
            # pos_hint={"center_x": 0.5},
            on_release=self.grade_submission
        )
        logout_button = MDRaisedButton(
            text="Log out",
            # pos_hint={"center_x": 0.5, "center_y": 0.4},
            on_release=self.logout
        )

        buttons_layout.add_widget(detail_button)
        buttons_layout.add_widget(classes_button)
        buttons_layout.add_widget(grade_button)
        buttons_layout.add_widget(logout_button)

        self.add_widget(welcome_label)
        self.add_widget(teacher_info)
        self.add_widget(buttons_layout)

    def logout(self, instance):
        app = MDApp.get_running_app()
        app.username = None
        app.role = None
        self.manager.current = "login_screen"

    def view_classes(self, instance):
        app = MDApp.get_running_app()
        teacher_code = app.username
        teacher_classes = get_teacher_classes(teacher_code)
        
        # Create a dialog to show classes
        class_dialog_content = BoxLayout(orientation="vertical", size_hint_y=None, height=200)
        for class_info in teacher_classes:
            class_dialog_content.add_widget(MDLabel(text=f"Class: {class_info['class_name']} - {class_info['subject_name']}", halign="center"))
        
        self.dialog = MDDialog(
            title="Classes Taught",
            type="custom",
            content_cls=class_dialog_content,
            buttons=[MDRaisedButton(text="Close", on_release=self.close_dialog)]
        )
        self.dialog.open()

    def grade_submission(self, instance):
        # Here you would create a form for submitting grades
        self.dialog = MDDialog(
            title="Grade Submission",
            type="custom",
            content_cls=self.create_grade_form(),
            buttons=[MDRaisedButton(text="Submit", on_release=self.submit_grades), MDRaisedButton(text="Cancel", on_release=self.close_dialog)]
        )
        self.dialog.open()

    def create_grade_form(self):
        # Create form for grade submission, can be expanded as needed
        grade_form_layout = BoxLayout(orientation="vertical", spacing=10)
        grade_form_layout.add_widget(MDLabel(text="Student ID"))
        grade_form_layout.add_widget(MDLabel(text="Grade"))
        return grade_form_layout

    def submit_grades(self, instance):
        # Handle grade submission logic here (e.g., save grades to the database)
        print("Grades submitted.")
        self.close_dialog(instance)

    def close_dialog(self, instance):
        self.dialog.dismiss()

    
