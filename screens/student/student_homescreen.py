from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from utils.db_utils import get_student_name, get_student_details, get_student_classes, get_student_grades, update_student_details

class StudentHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None # just declared 

    def on_enter(self):
        self.clear_widgets()

        app = MDApp.get_running_app()
        student_code = app.username
        student_name = get_student_name(student_code)

        welcome_label = MDLabel(
            text=f"Welcome, {student_name}!",
            halign="center",
            pos_hint={"center_y": 0.95},
            font_style="H6"
        )

        student_info = MDBoxLayout(orientation="vertical", spacing=5, size_hint_y=None, height=80)
    


        # Tạo layout để chứa các nút, căn giữa và có khoảng cách
        buttons_layout = MDBoxLayout(orientation="vertical", spacing=15, size_hint=(0.6, None), height=300, pos_hint={"center_x": 0.5, "center_y": 0.45})

        detail_button = MDRaisedButton(text="Student's Details", on_release=self.view_details)
        class_button = MDRaisedButton(text="Class", on_release=self.view_classes)
        result_button = MDRaisedButton(text="Academic Result", on_release=self.view_results)
        logout_button = MDRaisedButton(text="Log out", on_release=self.logout)

        # Thêm nút vào layout
        buttons_layout.add_widget(detail_button)
        buttons_layout.add_widget(class_button)
        buttons_layout.add_widget(result_button)
        buttons_layout.add_widget(logout_button)

        # Thêm các widget chính vào màn hình
        self.add_widget(welcome_label)
        self.add_widget(student_info)
        self.add_widget(buttons_layout)

    def logout(self, instance):
        app = MDApp.get_running_app()
        app.username = None
        app.role = None
        self.manager.current = "login_screen"

    def view_details(self, instance):
        app = MDApp.get_running_app()
        student_id = app.username
        details = get_student_details(student_id)


        content = MDBoxLayout(orientation="vertical", spacing=10, adaptive_height=True)
        content.add_widget(MDLabel(text=f"Name: {details['student_name']} \nStudent Code: {details['student_code']} \nClass ID: {details['class_id']} \nAddress: {details['address']}", halign="center"))

        self.dialog = MDDialog(title="Student Details", type="custom", content_cls=content, buttons=[
            MDRaisedButton(text="Change", on_release=self.edit_student_details),
            MDRaisedButton(text="Close", on_release=self.close_dialog)
        ])
        self.dialog.open()


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



    def edit_student_details(self, instance):
        self.dialog.dismiss()

        # Tạo form nhập thông tin mới
        self.name_input = MDTextField(hint_text="Name")
        self.address_input = MDTextField(hint_text="Address")

        content = MDBoxLayout(orientation="vertical", spacing=10, adaptive_height=True)
        content.add_widget(self.name_input)
        content.add_widget(self.address_input)

        self.edit_dialog = MDDialog(
            title="Change information",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Save", on_release=self.save_updated_student),
                MDRaisedButton(text="Discard", on_release=lambda x: self.edit_dialog.dismiss())
            ]
        )
        self.edit_dialog.open()

    def save_updated_student(self, instance):
        app = MDApp.get_running_app()
        student_code = app.username
        new_name = self.name_input.text
        new_address = self.address_input.text

        success = update_student_details(student_code, new_name, new_address)
        self.edit_dialog.dismiss()

        if success:
            toast("Updated successfully!")
        else:
            toast("Failed to update!")


    def view_results(self, instance):
        app = MDApp.get_running_app()
        student_code = app.username  # Giả sử username là mã sinh viên
        subjects, gpa_total = get_student_grades(student_code)

        # Tạo layout chứa kết quả
        content = MDBoxLayout(orientation="vertical", spacing=10, adaptive_height=True)

        # Thêm từng dòng điểm môn học

        for subject in subjects:
            content.add_widget(MDLabel(
                text=f"{subject['SubjectName']} | 10%: {subject['Score_10']} | 40%: {subject['Score_40']} | 50%: {subject['Score_50']} | GPA môn: {subject['GPA_Subject']}",
                halign="center"
            ))
            # Thêm dòng trống để tạo khoảng cách
            content.add_widget(MDLabel(text=" "))

        # Thêm GPA toàn bộ môn học
        content.add_widget(MDLabel(
            text=f"→ GPA toàn bộ môn học: {gpa_total}",
            halign="center",
            theme_text_color="Secondary"
        ))

        # Tạo dialog mới mỗi lần để tránh lỗi không hiển thị dữ liệu mới
        self.dialog = MDDialog(
            title="Academic Results",
            type="custom",
            content_cls=content,
            buttons=[MDRaisedButton(text="Close", on_release=self.close_dialog)]
        )
        self.dialog.open()


    def close_dialog(self, instance):
        self.dialog.dismiss()


