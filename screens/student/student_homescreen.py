from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from utils.db_utils import get_student_info, get_student_subjects_and_teachers, get_student_details, get_student_classes, get_student_grades, update_student_details
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import ScrollView

class StudentHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.student_info = None
        self.subjects_data = None
        self.dialog = None

    def on_enter(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        
        # Fetch student data
        self.student_info = get_student_info(app.username)
        if not self.student_info:
            return
        
        self.subjects_data = get_student_subjects_and_teachers(app.username)

        # Main container with padding to prevent edge touching
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[40, 20, 40, 20],  # left, top, right, bottom
            size_hint=(1, 1),
            md_bg_color=[0.9, 0.9, 0.9, 1]  # Light gray background
        )

        # Top section with student info
        info_card = MDCard(
            orientation="vertical",
            size_hint=(1, None),
            height=200,
            padding=[20, 20, 20, 20],
            elevation=2,
            md_bg_color=[1, 1, 1, 1]  # White background
        )

        # Student basic info
        welcome_label = MDLabel(
            text=f"Welcome, {self.student_info['StudentName']}!",
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height=50
        )

        info_grid = MDGridLayout(
            cols=2,
            spacing=10,
            size_hint_y=None,
            height=100,
            padding=[0, 10, 0, 10]
        )

        # Left column info
        student_code_label = MDLabel(
            text=f"Student Code: {self.student_info['StudentCode']}",
            font_style="Subtitle1"
        )
        
        class_label = MDLabel(
            text=f"Class: {self.student_info['ClassName']}",
            font_style="Subtitle1"
        )

        address_label = MDLabel(
            text=f"Address: {self.student_info['Address']}",
            font_style="Subtitle1"
        )

        # Add info to grid
        info_grid.add_widget(student_code_label)
        info_grid.add_widget(class_label)
        info_grid.add_widget(address_label)

        # Add all elements to info card
        info_card.add_widget(welcome_label)
        info_card.add_widget(info_grid)

        # Action buttons in a horizontal layout
        buttons_card = MDCard(
            orientation="horizontal",
            size_hint=(1, None),
            height=80,
            padding=[20, 10, 20, 10],
            spacing=20,
            elevation=2,
            md_bg_color=[1, 1, 1, 1]
        )

        # Create action buttons
        buttons = [
            {
                "text": "Student Details",
                "icon": "account-details",
                "callback": self.view_details
            },
            {
                "text": "My Classes",
                "icon": "google-classroom",
                "callback": self.view_classes
            },
            {
                "text": "Academic Results",
                "icon": "school",
                "callback": self.view_results
            },
            {
                "text": "Log out",
                "icon": "logout",
                "callback": self.logout
            }
        ]

        for btn in buttons:
            button = MDRaisedButton(
                text=btn["text"],
                icon=btn["icon"],
                size_hint=(1, None),
                height=50,
                md_bg_color=[0.2, 0.4, 0.8, 1],  # Custom blue color
                on_release=btn["callback"]
            )
            buttons_card.add_widget(button)

        # Subjects section
        subjects_card = MDCard(
            orientation="vertical",
            size_hint=(1, 1),
            padding=[20, 20, 20, 20],
            elevation=2,
            md_bg_color=[1, 1, 1, 1]
        )

        subjects_title = MDLabel(
            text="My Subjects and Teachers",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=50
        )

        # Create scrollable list for subjects
        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False
        )
        
        subjects_list = MDList(
            spacing=10,
            padding=[0, 10, 0, 10]
        )

        if self.subjects_data:
            for subject in self.subjects_data:
                icon = IconLeftWidget(
                    icon="book-open-page-variant",
                    theme_text_color="Custom",
                    text_color=[0.2, 0.4, 0.8, 1]  # Match button color
                )
                item = OneLineIconListItem(
                    text=f"{subject['SubjectName']} - Teacher: {subject['TeacherName']}",
                    divider="Full",
                    divider_color=[0.8, 0.8, 0.8, 1]  # Light gray divider
                )
                item.add_widget(icon)
                subjects_list.add_widget(item)
        else:
            no_subjects_label = MDLabel(
                text="No subjects assigned yet.",
                halign="center",
                theme_text_color="Secondary"
            )
            subjects_list.add_widget(no_subjects_label)

        scroll.add_widget(subjects_list)
        subjects_card.add_widget(subjects_title)
        subjects_card.add_widget(scroll)

        # Add all sections to main layout
        main_layout.add_widget(info_card)
        main_layout.add_widget(buttons_card)
        main_layout.add_widget(subjects_card)

        self.add_widget(main_layout)

    def logout(self, instance):
        app = MDApp.get_running_app()
        app.username = None
        app.role = None
        self.manager.current = "login_screen"

    def view_details(self, instance):
        app = MDApp.get_running_app()
        student_id = app.username
        details = get_student_details(student_id)

        content = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=400,
            md_bg_color=[1, 1, 1, 1]
        )

        # Info section
        info_grid = MDGridLayout(
            cols=2,
            spacing=10,
            size_hint_y=None,
            height=200,
            padding=[0, 10, 0, 10]
        )

        # Labels with consistent styling
        label_style = {
            "theme_text_color": "Secondary",
            "font_style": "Body1"
        }
        value_style = {
            "theme_text_color": "Primary",
            "font_style": "Body1",
            "bold": True
        }

        # Add each field with label
        fields = [
            ("Name", details['student_name']),
            ("Student Code", details['student_code']),
            ("Class", f"Class {details['class_id']}"),
            ("Address", details['address'])
        ]

        for label, value in fields:
            info_grid.add_widget(MDLabel(
                text=f"{label}:",
                **label_style
            ))
            info_grid.add_widget(MDLabel(
                text=str(value),
                **value_style
            ))

        content.add_widget(info_grid)

        # Simple separator using MDBoxLayout
        separator = MDBoxLayout(
            size_hint_y=None,
            height=1,
            md_bg_color=[0.8, 0.8, 0.8, 1]  # Light gray color
        )
        content.add_widget(separator)

        # Edit button with icon
        edit_button = MDRaisedButton(
            text="Edit Information",
            icon="pencil",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"center_x": 0.5},
            md_bg_color=[0.2, 0.4, 0.8, 1],
            on_release=self.edit_student_details
        )
        content.add_widget(edit_button)

        self.dialog = MDDialog(
            title="Student Details",
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

    def edit_student_details(self, instance):
        self.dialog.dismiss()
        app = MDApp.get_running_app()
        student_code = app.username
        student = get_student_details(student_code)

        if not student:
            toast("Could not fetch student details.")
            return

        content = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=300,
            md_bg_color=[1, 1, 1, 1]
        )

        # Title
        title = MDLabel(
            text="Edit Your Information",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=50
        )
        content.add_widget(title)

        # Input fields with icons
        self.name_input = MDTextField(
            hint_text="Name",
            text=student["student_name"],
            mode="rectangle",
            icon_right="account",
            size_hint_y=None,
            height=50
        )

        self.address_input = MDTextField(
            hint_text="Address",
            text=student["address"],
            mode="rectangle",
            icon_right="home",
            size_hint_y=None,
            height=50,
            multiline=True
        )

        content.add_widget(self.name_input)
        content.add_widget(self.address_input)

        # Buttons with better styling
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
            on_release=self.save_updated_student
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
            type="custom",
            content_cls=content,
            size_hint=(0.8, None)
        )
        self.edit_dialog.open()

    def save_updated_student(self, instance):
        app = MDApp.get_running_app()
        student_code = app.username
        new_name = self.name_input.text.strip()
        new_address = self.address_input.text.strip()

        # Kiểm tra rỗng
        if not new_name or not new_address:
            toast("Please fill in all fields.")
            return

        success = update_student_details(student_code, new_name, new_address)
        self.edit_dialog.dismiss()

        if success:
            toast("Updated successfully!")
        else:
            toast("Failed to update!")

    def view_classes(self, instance):
        app = MDApp.get_running_app()
        student_id = app.username
        classes = get_student_classes(student_id)

        content = MDBoxLayout(orientation="vertical", spacing=10, adaptive_height=True, padding=10)

        # Tiêu đề bảng
        header = MDBoxLayout(orientation="horizontal", spacing=10)
        header.add_widget(MDLabel(text="No.", bold=True, size_hint_x=0.2))
        header.add_widget(MDLabel(text="Subject", bold=True, size_hint_x=0.4))
        header.add_widget(MDLabel(text="Teacher", bold=True, size_hint_x=0.4))
        content.add_widget(header)

        # Dữ liệu bảng
        for idx, item in enumerate(classes, start=1):
            row = MDBoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40) # just changed
            row.add_widget(MDLabel(text=str(idx), size_hint_x=0.2))
            row.add_widget(MDLabel(text=item['subject_name'], size_hint_x=0.4))
            row.add_widget(MDLabel(text=item['teacher_name'], size_hint_x=0.4))
            content.add_widget(row)

        self.dialog = MDDialog(
            title="Your Classes",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Close", on_release=self.close_dialog)
            ]
        )
        self.dialog.open()

    def view_results(self, instance):
        app = MDApp.get_running_app()
        student_code = app.username
        subjects, gpa_total = get_student_grades(student_code)

        content = MDBoxLayout(
            orientation="vertical",
            spacing=20,
            padding=[20, 20, 20, 20],
            size_hint_y=None,
            height=400 + (len(subjects) * 80) if subjects else 200,
            md_bg_color=[1, 1, 1, 1]
        )

        # Scrollable container for subjects
        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False
        )

        subjects_layout = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            size_hint_y=None,
            adaptive_height=True
        )

        if subjects:
            for subject in subjects:
                # Card for each subject
                subject_card = MDCard(
                    orientation="vertical",
                    size_hint=(1, None),
                    height=100,
                    padding=15,
                    elevation=2
                )

                # Subject name with icon
                subject_header = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=30
                )
                subject_icon = IconLeftWidget(
                    icon="book",
                    theme_text_color="Custom",
                    text_color=[0.2, 0.4, 0.8, 1]
                )
                subject_name = MDLabel(
                    text=subject['SubjectName'],
                    font_style="H6",
                    bold=True
                )
                subject_header.add_widget(subject_icon)
                subject_header.add_widget(subject_name)
                subject_card.add_widget(subject_header)

                # Grades grid
                grades_grid = MDGridLayout(
                    cols=4,
                    spacing=10,
                    padding=[10, 5, 10, 5]
                )

                # Add grades with labels
                grades = [
                    ("Attendance (10%)", subject['Score_10']),
                    ("Midterm (40%)", subject['Score_40']),
                    ("Final (50%)", subject['Score_50']),
                    ("GPA", subject['GPA_Subject'])
                ]

                for label, value in grades:
                    grades_grid.add_widget(MDLabel(
                        text=label,
                        theme_text_color="Secondary",
                        font_style="Caption"
                    ))
                    grades_grid.add_widget(MDLabel(
                        text=str(value),
                        theme_text_color="Primary",
                        bold=True
                    ))

                subject_card.add_widget(grades_grid)
                subjects_layout.add_widget(subject_card)

            # Total GPA card
            total_gpa_card = MDCard(
                orientation="horizontal",
                size_hint=(1, None),
                height=60,
                padding=15,
                elevation=2,
                md_bg_color=[0.2, 0.4, 0.8, 0.1]
            )

            total_gpa_label = MDLabel(
                text="Overall GPA:",
                theme_text_color="Primary",
                font_style="H6",
                bold=True
            )

            total_gpa_value = MDLabel(
                text=str(gpa_total),
                theme_text_color="Primary",
                font_style="H6",
                bold=True,
                halign="right"
            )

            total_gpa_card.add_widget(total_gpa_label)
            total_gpa_card.add_widget(total_gpa_value)
            subjects_layout.add_widget(total_gpa_card)

        else:
            no_results = MDLabel(
                text="No academic results available.",
                halign="center",
                theme_text_color="Secondary"
            )
            subjects_layout.add_widget(no_results)

        scroll.add_widget(subjects_layout)
        content.add_widget(scroll)

        self.dialog = MDDialog(
            title="Academic Results",
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

    def close_dialog(self, instance):
        self.dialog.dismiss()


