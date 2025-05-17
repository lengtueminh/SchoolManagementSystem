from kivymd.app import MDApp
from kivymd.uix.screenmanager import ScreenManager
from screens.login_screen import LoginScreen
from screens.teacher import TeacherHomeScreen, TeacherClassesScreen
from screens.admin import AdminHomeScreen
from screens.admin.admin_teachers_screen import AdminTeachersScreen
from screens.admin.admin_classes_screen import AdminClassesScreen
from screens.admin.admin_subjects_screen import AdminSubjectsScreen
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

        # Add all screens
        screens = [
            LoginScreen(name="login_screen"),
            TeacherHomeScreen(name="teacher_homescreen"),
            StudentHomeScreen(name="student_screen"),
            AdminHomeScreen(name="admin_homescreen"),
            TeacherClassesScreen(name="teacher_classes"),
            ClassDisplay(name="class_display"),
            AdminTeachersScreen(),
            AdminClassesScreen(),
            AdminSubjectsScreen()
        ]
        
        for screen in screens:
            sm.add_widget(screen)

        return sm

SchoolManagementApp().run()
