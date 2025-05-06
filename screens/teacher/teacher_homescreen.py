from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import BoxLayout, MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from utils.db_utils import check_student_exists, get_teacher_name, get_teacher_details, get_teacher_classes, update_teacher_details, submit_grade_to_db

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
            on_release=self.view_details
        )

        classes_button = MDRaisedButton(
            text="View Classes",
            on_release=self.view_classes
        )

        grade_button = MDRaisedButton(
            text="Grade Submission",
            on_release=self.grade_submission
        )
        logout_button = MDRaisedButton(
            text="Log out",
            on_release=self.logout
        )

        buttons_layout.add_widget(detail_button)
        buttons_layout.add_widget(classes_button)
        buttons_layout.add_widget(grade_button)
        buttons_layout.add_widget(logout_button)

        self.add_widget(welcome_label)
        # self.add_widget(teacher_info)
        self.add_widget(buttons_layout)

    def logout(self, instance):
        app = MDApp.get_running_app()
        app.username = None
        app.role = None
        self.manager.current = "login_screen"

    def view_details(self, instance):
        app = MDApp.get_running_app()
        teacher_id = app.username
        details = get_teacher_details(teacher_id)

        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=200)
        content.add_widget(MDLabel(text=f"Name: {details['teacher_name']} \n\nTeacher Code: {details['teacher_code']} \n\nEmail: {details['email']} \n\nSubject: {details['subject']}", halign="left"))

        self.dialog = MDDialog(title="Teacher Details", type="custom", content_cls=content, buttons=[
            MDRaisedButton(text="Change", on_release=self.edit_teacher_details),
            MDRaisedButton(text="Close", on_release=self.close_dialog)
        ])
        self.dialog.open()

    def edit_teacher_details(self, instance):
        self.dialog.dismiss()

        app = MDApp.get_running_app()
        teacher_code = app.username
        teacher = get_teacher_details(teacher_code)
        if not teacher:
            print("Không thể lấy thông tin sinh viên.")
            return

        self.name_input = MDTextField(
            hint_text="Name",
            text=teacher["teacher_name"]
        )
        self.email_input = MDTextField(
            hint_text="Email",
            text=teacher["email"]
        )

        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=200)
        content.add_widget(self.name_input)
        content.add_widget(self.email_input)

        self.edit_dialog = MDDialog(
            title="Change Information",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Save", on_release=self.save_updated_teacher),
                MDRaisedButton(text="Discard", on_release=lambda x: self.edit_dialog.dismiss())
            ]
        )
        self.edit_dialog.open()

    def save_updated_teacher(self, instance):
        app = MDApp.get_running_app()
        teacher_code = app.username
        new_name = self.name_input.text.strip()
        new_email = self.email_input.text.strip()

        if not new_name or not new_email:
            toast("Please fill in all fields.")
            return

        success = update_teacher_details(teacher_code, new_name, new_email)
        self.edit_dialog.dismiss()

        if success:
            toast("Updated successfully!")
        else:
            toast("Failed to update!")

    def view_classes(self, instance):
        app = MDApp.get_running_app()
        teacher_code = app.username
        teacher_classes = get_teacher_classes(teacher_code)
        
        # Create a dialog to show classes
        class_dialog_content = BoxLayout(orientation="vertical", size_hint_y=None, height=200)
        for class_info in teacher_classes:
            class_dialog_content.add_widget(MDLabel(text=f"Class: {class_info['class_name']} - {class_info['subject_name']}", halign="left"))
        
        self.dialog = MDDialog(
            title="My Classes",
            type="custom",
            content_cls=class_dialog_content,
            buttons=[MDRaisedButton(text="Close", on_release=self.close_dialog)]
        )
        self.dialog.open()

    def grade_submission(self, instance):
        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=400)
        self.student_code_input = MDTextField(hint_text="Student Code")
        self.percentage_input = MDTextField(hint_text="Percentage")
        self.grade_input = MDTextField(hint_text="Grade")

        content.add_widget(self.student_code_input)
        content.add_widget(self.percentage_input)
        content.add_widget(self.grade_input)

        self.dialog = MDDialog(
            title="Grade Submission",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Submit", on_release=self.submit_grades),  
                MDRaisedButton(text="Cancel", on_release=self.close_dialog)
            ]
        )
        self.dialog.open()

    def submit_grades(self, instance):
        student_code = self.student_code_input.text.strip()
        grade_text = self.grade_input.text.strip()
        percentage_text = self.percentage_input.text.strip()

        app = MDApp.get_running_app()
        teacher_code = app.username

        if not student_code or not grade_text or not percentage_text:
            toast("Please fill in all fields.")
            return
        
        try:
            grade = float(grade_text)
            if grade <= 0 or grade > 10.0:
                toast("Grade must be between 0 and 10.")
                return
        except ValueError:
            toast("Invalid grade format.")
            return
        
        try:
            percentage = float(percentage_text)
            if percentage not in (0.10, 0.40, 0.50):
                toast("Percentage must be 0.10, 0.40, or 0.50.")
                return
        except ValueError:
            toast("Invalid percentage format.")
            return

        if not check_student_exists(student_code):
            toast("Student code does not exist.")
            return
    
        success = submit_grade_to_db(student_code, teacher_code, grade, percentage)

        if success:
            toast("Grade submitted successfully.")
        else:
            toast("Failed to submit grade.")

        self.close_dialog(instance)

    def close_dialog(self, instance):
        self.dialog.dismiss()

    
