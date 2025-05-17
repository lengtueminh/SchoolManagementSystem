from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivymd.uix.card import MDCard
from kivymd.uix.list import IconLeftWidget
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

        # Main container with padding
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            padding=[20, 10, 20, 10],
            size_hint=(1, None),
            height=300,
            pos_hint={"top": 0.98},
            md_bg_color=[0.95, 0.95, 0.95, 1]  # Light gray background
        )

        # Top card with teacher info
        info_card = MDCard(
            orientation="vertical",
            size_hint=(1, None),
            height=180,
            padding=[20, 15, 20, 15],
            elevation=2,
            md_bg_color=[1, 1, 1, 1],  # White background
            radius=[10, 10, 10, 10]  # Rounded corners
        )

        # Teacher basic info
        welcome_label = MDLabel(
            text=f"Welcome back, {teacher_name}!",
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height=50
        )

        info_grid = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None,
            height=100,
            padding=[0, 0, 0, 0]
        )

        info_grid.add_widget(MDLabel(
            text=f"Teacher Code: {teacher_details['teacher_code']}",
            font_style="Subtitle1"
        ))
        info_grid.add_widget(MDLabel(
            text=f"Email: {teacher_details['email']}",
            font_style="Subtitle1"
        ))
        info_grid.add_widget(MDLabel(
            text=f"Subject: {teacher_details['subject']}",
            font_style="Subtitle1"
        ))

        info_card.add_widget(welcome_label)
        info_card.add_widget(info_grid)

        # Action buttons card
        buttons_card = MDCard(
            orientation="horizontal",
            size_hint=(1, None),
            height=60,
            padding=[10, 5, 10, 5],
            spacing=10,
            elevation=2,
            md_bg_color=[1, 1, 1, 1],
            radius=[10, 10, 10, 10]  # Rounded corners
        )

        # Create action buttons with icons
        buttons = [
            {
                "text": "Teacher Details",
                "icon": "account-details",
                "callback": self.view_details,
                "color": [0.2, 0.6, 0.8, 1]  # Blue
            },
            {
                "text": "My Classes",
                "icon": "google-classroom",
                "callback": self.view_classes,
                "color": [0.2, 0.8, 0.2, 1]  # Green
            },
            {
                "text": "Grade Submission",
                "icon": "pencil",
                "callback": self.grade_submission,
                "color": [0.8, 0.4, 0.2, 1]  # Orange
            },
            {
                "text": "Log out",
                "icon": "logout",
                "callback": self.logout,
                "color": [0.8, 0.2, 0.2, 1]  # Red
            }
        ]

        for btn in buttons:
            button = MDRaisedButton(
                text=btn["text"],
                icon=btn["icon"],
                size_hint=(1, None),
                height=50,
                md_bg_color=btn["color"],
                on_release=btn["callback"]
            )
            buttons_card.add_widget(button)

        # Add all sections to main layout
        main_layout.add_widget(info_card)
        main_layout.add_widget(buttons_card)

        self.add_widget(main_layout)

    def view_details(self, instance):
        app = MDApp.get_running_app()
        teacher_id = app.username
        details = get_teacher_details(teacher_id)

        content = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=300,
            md_bg_color=[1, 1, 1, 1]
        )

        # Info grid with icons
        info_items = [
            ("account", "Name", details['teacher_name']),
            ("card-account-details", "Teacher Code", details['teacher_code']),
            ("email", "Email", details['email']),
            ("book-open-variant", "Subject", details['subject'])
        ]

        for icon, label, value in info_items:
            item_layout = MDBoxLayout(
                orientation="horizontal",
                spacing=10,
                size_hint_y=None,
                height=40
            )
            
            icon_widget = IconLeftWidget(
                icon=icon,
                theme_text_color="Custom",
                text_color=[0.2, 0.4, 0.8, 1]
            )
            
            label_widget = MDLabel(
                text=f"{label}: {value}",
                theme_text_color="Primary",
                size_hint_x=None,
                width=400
            )
            
            item_layout.add_widget(icon_widget)
            item_layout.add_widget(label_widget)
            content.add_widget(item_layout)

        # Separator
        separator = MDBoxLayout(
            size_hint_y=None,
            height=1,
            md_bg_color=[0.8, 0.8, 0.8, 1]  # Light gray color
        )
        content.add_widget(separator)

        # Edit button
        edit_button = MDRaisedButton(
            text="Edit Information",
            icon="pencil",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"center_x": 0.5},
            md_bg_color=[0.2, 0.4, 0.8, 1],
            on_release=self.edit_teacher_details
        )
        content.add_widget(edit_button)

        self.dialog = MDDialog(
            title="Teacher Details",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Close",
                    on_release=self.close_dialog
                )
            ]
        )
        self.dialog.open()

    def edit_teacher_details(self, instance):
        self.dialog.dismiss()
        app = MDApp.get_running_app()
        teacher_code = app.username
        teacher = get_teacher_details(teacher_code)

        if not teacher:
            toast("Could not fetch teacher details.")
            return

        content = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=250,
            md_bg_color=[1, 1, 1, 1]
        )

        self.name_input = MDTextField(
            hint_text="Name",
            text=teacher["teacher_name"],
            mode="rectangle",
            icon_right="account"
        )
        self.email_input = MDTextField(
            hint_text="Email",
            text=teacher["email"],
            mode="rectangle",
            icon_right="email"
        )

        content.add_widget(self.name_input)
        content.add_widget(self.email_input)

        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=50,
            pos_hint={"center_x": 0.5}
        )

        save_button = MDRaisedButton(
            text="Save Changes",
            icon="content-save",
            md_bg_color=[0.2, 0.4, 0.8, 1],
            on_release=self.save_updated_teacher
        )

        cancel_button = MDRaisedButton(
            text="Cancel",
            icon="close",
            md_bg_color=[0.7, 0.7, 0.7, 1],
            on_release=lambda x: self.edit_dialog.dismiss()
        )

        buttons_layout.add_widget(save_button)
        buttons_layout.add_widget(cancel_button)
        content.add_widget(buttons_layout)

        self.edit_dialog = MDDialog(
            title="Edit Information",
            type="custom",
            content_cls=content,
            size_hint=(0.8, None)
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
        self.manager.current = "teacher_classes"

    def grade_submission(self, instance):
        content = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=400,
            md_bg_color=[1, 1, 1, 1]
        )

        # Input fields with icons
        self.student_code_input = MDTextField(
            hint_text="Student Code",
            mode="rectangle",
            icon_right="account-card"
        )
        self.percentage_input = MDTextField(
            hint_text="Percentage (0.10, 0.40, or 0.50)",
            mode="rectangle",
            icon_right="percent"
        )
        self.grade_input = MDTextField(
            hint_text="Grade (0-10)",
            mode="rectangle",
            icon_right="pencil"
        )

        content.add_widget(self.student_code_input)
        content.add_widget(self.percentage_input)
        content.add_widget(self.grade_input)

        buttons_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_y=None,
            height=50
        )

        submit_button = MDRaisedButton(
            text="Submit",
            icon="check",
            md_bg_color=[0.2, 0.4, 0.8, 1],
            on_release=self.submit_grades
        )

        cancel_button = MDRaisedButton(
            text="Cancel",
            icon="close",
            md_bg_color=[0.7, 0.7, 0.7, 1],
            on_release=self.close_dialog
        )

        buttons_layout.add_widget(submit_button)
        buttons_layout.add_widget(cancel_button)
        content.add_widget(buttons_layout)

        self.dialog = MDDialog(
            title="Grade Submission",
            type="custom",
            content_cls=content,
            size_hint=(0.8, None)
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
            if grade < 0 or grade > 10.0:
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
    
        success = submit_grade_to_db(teacher_code, student_code, percentage, grade)

        if success:
            toast("Grade submitted successfully!")
            self.dialog.dismiss()
        else:
            toast("Failed to submit grade.")

    def close_dialog(self, instance):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

    def logout(self, instance):
        app = MDApp.get_running_app()
        app.username = None
        app.role = None
        self.manager.current = "login_screen"


   



