# main.py
from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from screens.login_screen import LoginScreen
# from screens.admin_screen import AdminScreen
# from screens.student_screen import StudentScreen

class SchoolManagementApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        sm = ScreenManager()

        sm.add_widget(LoginScreen(name="login_screen"))
        # sm.add_widget(AdminScreen(name="admin_screen"))
        # sm.add_widget(StudentScreen(name="student_screen"))

        return sm

SchoolManagementApp().run()
