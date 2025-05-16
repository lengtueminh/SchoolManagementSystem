from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from screens.login_screen import LoginScreen
from screens.teacher import TeacherHomeScreen, TeacherClassesScreen
from screens.admin import AdminHomeScreen
from screens.student import StudentHomeScreen
from screens.teacher.class_display import ClassDisplay

class SchoolManagementApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.username = None
        self.role = None

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        sm = ScreenManager()

        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(TeacherHomeScreen(name="teacher_homescreen"))
        sm.add_widget(StudentHomeScreen(name="student_screen"))
        sm.add_widget(AdminHomeScreen(name="admin_homescreen"))
        sm.add_widget(TeacherClassesScreen(name="teacher_classes"))
        sm.add_widget(ClassDisplay(name="class_display"))

        return sm

SchoolManagementApp().run()
