# from kivymd.uix.screen import MDScreen
# from kivymd.uix.label import MDLabel
# from kivymd.uix.button import MDRaisedButton
# from kivymd.app import MDApp
# from kivymd.uix.boxlayout import BoxLayout
# from kivymd.uix.dialog import MDDialog
# from utils.db_utils import get_student_name, get_student_details, get_student_classes, get_student_grades

# class StudentHomeScreen(MDScreen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#     def on_enter(self):
#         self.clear_widgets()

#         app = MDApp.get_running_app()
#         student_code = app.username
#         student_name = get_student_name(student_code)
#         student_details = get_student_details(student_code)

#         welcome_label = MDLabel(
#             text=f"Welcome, {student_name} ({student_code})!",
#             halign="center",
#             pos_hint={"center_y": 0.9}
#         )

#         student_info = BoxLayout(orientation="vertical", spacing=10, size_hint_y=None, height=200)
#         student_info.add_widget(MDLabel(text=f"Name: {student_details['student_name']}", halign="center"))
#         # student_info.add_widget(MDLabel(text=f"Email: {student_details['email']}", halign="center"))

#         detail_button = MDRaisedButton(
#             text="Student's Details",
#             pos_hint={"center_x": 0.5},
#             on_release=self.view_details
#         )

#         class_button = MDRaisedButton(
#             text="Class",
#             pos_hint={"center_x": 0.5},
#             on_release=self.view_classes
#         )

#         result_button = MDRaisedButton(
#             text="Academic Result",
#             pos_hint={"center_x": 0.5},
#             on_release=self.view_results
#         )

#         # noti_button = MDRaisedButton(
#         #     text="Notifications",
#         #     pos_hint={"center_x": 0.5},
#         #     on_release=self.view_notifications
#         # )

#         logout_button = MDRaisedButton(
#             text="Log out",
#             pos_hint={"center_x": 0.5},
#             on_release=self.logout
#         )

#         self.add_widget(welcome_label)
#         self.add_widget(student_info)
#         self.add_widget(detail_button)
#         self.add_widget(class_button)
#         self.add_widget(result_button)
#         # self.add_widget(noti_button)
#         self.add_widget(logout_button)

#     def logout(self, instance):
#         app = MDApp.get_running_app()
#         app.username = None
#         app.role = None
#         self.manager.current = "login_screen"

#     def view_details(self, instance):
#         app = MDApp.get_running_app()
#         student_id = app.username
#         details = get_student_details(student_id)

#         content = BoxLayout(orientation="vertical", spacing=10)
#         for key, value in details.items():
#             content.add_widget(MDLabel(text=f"{key.capitalize()}: {value}", halign="center"))

#         self.dialog = MDDialog(title="Student Details", type="custom", content_cls=content, buttons=[
#             MDRaisedButton(text="Close", on_release=self.close_dialog)
#         ])
#         self.dialog.open()

#     def view_classes(self, instance):
#         app = MDApp.get_running_app()
#         student_id = app.username
#         classes = get_student_classes(student_id)

#         content = BoxLayout(orientation="vertical", spacing=10)
#         for c in classes:
#             content.add_widget(MDLabel(text=f"{c['subject_name']} - {c['teacher_name']}", halign="center"))

#         self.dialog = MDDialog(title="Your Classes", type="custom", content_cls=content, buttons=[
#             MDRaisedButton(text="Close", on_release=self.close_dialog)
#         ])
#         self.dialog.open()

#     def view_results(self, instance):
#         app = MDApp.get_running_app()
#         student_id = app.username
#         grades = get_student_grades(student_id)

#         content = BoxLayout(orientation="vertical", spacing=10)
#         for g in grades:
#             content.add_widget(MDLabel(text=f"{g['subject']}: {g['grade']}", halign="center"))

#         self.dialog = MDDialog(title="Academic Results", type="custom", content_cls=content, buttons=[
#             MDRaisedButton(text="Close", on_release=self.close_dialog)
#         ])
#         self.dialog.open()

#     # def view_notifications(self, instance):
#     #     app = MDApp.get_running_app()
#     #     student_id = app.username
#     #     notis = get_student_notifications(student_id)

#     #     content = BoxLayout(orientation="vertical", spacing=10)
#     #     for n in notis:
#     #         content.add_widget(MDLabel(text=f"- {n['message']}", halign="center"))

#     #     self.dialog = MDDialog(title="Notifications", type="custom", content_cls=content, buttons=[
#     #         MDRaisedButton(text="Close", on_release=self.close_dialog)
#     #     ])
#     #     self.dialog.open()

#     # def close_dialog(self, instance):
#     #     self.dialog.dismiss()


from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.dialog import MDDialog
from utils.db_utils import get_student_name, get_student_details, get_student_classes, get_student_grades

class StudentHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets()

        app = MDApp.get_running_app()
        student_code = app.username
        student_name = get_student_name(student_code)
        student_details = get_student_details(student_code)

        welcome_label = MDLabel(
            text=f"Welcome, {student_name} ({student_code})!",
            halign="center",
            pos_hint={"center_y": 0.95},
            font_style="H6"
        )

        student_info = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None, height=80)
        student_info.add_widget(MDLabel(text=f"Name: {student_details['student_name']}", halign="center"))
        # student_info.add_widget(MDLabel(text=f"Email: {student_details['email']}", halign="center"))

        # Tạo layout để chứa các nút, căn giữa và có khoảng cách
        buttons_layout = BoxLayout(orientation="vertical", spacing=15, size_hint=(0.6, None), height=300, pos_hint={"center_x": 0.5, "center_y": 0.45})

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

        content = BoxLayout(orientation="vertical", spacing=10)
        for key, value in details.items():
            content.add_widget(MDLabel(text=f"{key.capitalize()}: {value}", halign="center"))

        self.dialog = MDDialog(title="Student Details", type="custom", content_cls=content, buttons=[
            MDRaisedButton(text="Close", on_release=self.close_dialog)
        ])
        self.dialog.open()

    def view_classes(self, instance):
        app = MDApp.get_running_app()
        student_id = app.username
        classes = get_student_classes(student_id)

        content = BoxLayout(orientation="vertical", spacing=10)
        for c in classes:
            content.add_widget(MDLabel(text=f"{c['subject_name']} - {c['teacher_name']}", halign="center"))

        self.dialog = MDDialog(title="Your Classes", type="custom", content_cls=content, buttons=[
            MDRaisedButton(text="Close", on_release=self.close_dialog)
        ])
        self.dialog.open()

    def view_results(self, instance):
        app = MDApp.get_running_app()
        student_id = app.username
        grades = get_student_grades(student_id)

        content = BoxLayout(orientation="vertical", spacing=10)
        for g in grades:
            content.add_widget(MDLabel(text=f"{g['subject']}: {g['grade']}", halign="center"))

        self.dialog = MDDialog(title="Academic Results", type="custom", content_cls=content, buttons=[
            MDRaisedButton(text="Close", on_release=self.close_dialog)
        ])
        self.dialog.open()

    def close_dialog(self, instance):
        self.dialog.dismiss()
