from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from utils.db_utils import get_teacher_name

class TeacherHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_enter(self):
        self.clear_widgets() 

        app = MDApp.get_running_app()
        teacher_code = app.username
        teacher_name = get_teacher_name(teacher_code)

        welcome_label = MDLabel(
            text=f"Welcome back, {teacher_name} ({teacher_code})!",
            halign="center",
            pos_hint={"center_y": 0.7}
        )

        logout_button = MDRaisedButton(
            text="Log out",
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            on_release=self.logout
        )

        self.add_widget(welcome_label)
        self.add_widget(logout_button)

    def logout(self, instance):
        app = MDApp.get_running_app()
        app.username = None
        app.role = None
        self.manager.current = "login_screen"
