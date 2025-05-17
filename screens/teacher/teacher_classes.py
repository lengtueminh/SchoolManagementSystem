from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView, ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog


from utils.db_utils import get_classes_by_teacher, get_student_grade
from kivymd.uix.boxlayout import MDBoxLayout




class TeacherClassesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def on_enter(self):
        # self.clear_widgets()


        # app = MDApp.get_running_app()
        # teacher_code = app.username
       
        # your_classes = MDLabel(
        #     text=f"YOUR CLASSES",
        #     halign="center",
        #     pos_hint={"center_y": 0.95},
        #     font_style="H6",
        #     bold=True
        # )


        # buttons_layout = MDBoxLayout(
        #     orientation="vertical",
        #     spacing=15,
        #     size_hint=(0.6, None),
        #     height=300,
        #     pos_hint={"center_x": 0.5, "center_y": 0.45}
        # )


        # self.classes = get_classes_by_teacher(teacher_code)
        # for class_id, class_name in self.classes:
        #     class_button = MDRaisedButton(
        #         text=class_name,
        #         on_release=lambda btn, cid=class_id: self.show_students(btn, cid)
        #         )
        #     buttons_layout.add_widget(class_button)


        # back_button = MDRaisedButton(text="Back", on_release=self.go_back)
        # buttons_layout.add_widget(back_button)
        # self.add_widget(your_classes)
        # self.add_widget(buttons_layout)
        self.clear_widgets()


        app = MDApp.get_running_app()
        teacher_code = app.username


        your_classes = MDLabel(
            text="YOUR CLASSES",
            halign="center",
            font_style="H5",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": 0.5, "top": 0.95},
            bold=True,
        )
        self.add_widget(your_classes)


        container = MDBoxLayout(
            orientation='vertical',
            spacing=20,
            padding=[0, 20],
            size_hint=(0.8, None),
            pos_hint={"center_x": 0.5},
        )
        container.bind(minimum_height=container.setter('height'))


        self.classes = get_classes_by_teacher(teacher_code)
        for class_id, class_name in self.classes:
            card = MDCard(
                orientation='horizontal',
                padding=15,
                size_hint=(None, None),
                size=(300, 100),
                ripple_behavior=True,
                pos_hint={"center_x": 0.5},
                on_release=lambda card, cid=class_id: self.show_students(card, cid),
            )
            label = MDLabel(
                text=class_name,
                halign="center",
                font_style="H6",
                size_hint_x=0.9,
                valign="center"
                )
           
            card.add_widget(label)
            container.add_widget(card)


        scroll = MDScrollView(size_hint=(1, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.4})
        scroll.add_widget(container)
        self.add_widget(scroll)


        back_button = MDRaisedButton(
            text="Back",
            size_hint=(0.3, None),
            height=50,
            pos_hint={"center_x": 0.5, "y": 0.05},)
        back_button.bind(on_release=self.go_back)
        self.add_widget(back_button)


    def show_students(self, instance, class_id):
        app = MDApp.get_running_app()
        class_students_screen = app.root.get_screen("class_display")
        class_students_screen.class_id = class_id  # Truyền class_id vào màn hình
        self.manager.current = "class_display"  


        # container = StudentListContainer(orientation='vertical', spacing=10, padding=10)
        # for student_id, student_code, student_name in students:
        #     item = OneLineListItem(
        #         text=student_name,
        #         on_release=partial(self.show_student_grade, student_code)
        #     )
        #     container.add_widget(item)


        # self.dialog = MDDialog(
        #     title="Student List",
        #     type="custom",
        #     content_cls=container,
        #     buttons=[MDRaisedButton(text="Close", on_release=self.close_dialog)]
        # )
        # self.dialog.open()


        # student_list = MDBoxLayout(orientation='vertical', adaptive_height=True)
        # for student_id, student_code, student_name in students:
        #     item = OneLineListItem(
        #         text=student_name,
        #         on_release=partial(self.show_student_grade, student_code)
        #     )
        #     student_list.add_widget(item)


        # scroll = MDScrollView()
        # scroll.add_widget(student_list)


        # self.dialog = MDDialog(
        #     title="Student List",
        #     type="custom",
        #     content_cls=scroll,
        #     buttons=[MDRaisedButton(text="Close", on_release=self.close_dialog)]
        # )
        # self.dialog.open()


    def show_student_grade(self, instance, student_code):
        # Lấy điểm của học sinh (cần truyền subject_id và teacher_code từ thông tin giáo viên)
        grade = get_student_grade(student_code, subject_id=1)  # Giả sử subject_id là 1 (thay bằng subject_id thực tế)
       
        # Tạo dialog để hiển thị điểm học sinh
        content = MDLabel(text=f"Student Code: {student_code}\nGrade: {grade}")
        self.grade_dialog = MDDialog(
            title="Student Grade",
            content_cls=content,
            buttons=[MDRaisedButton(text="Close", on_release=self.close_dialog)]
        )
        self.grade_dialog.open()


    def go_back(self, instance):
        self.manager.current = "teacher_homescreen"


    def close_dialog(self, instance):
        self.dialog.dismiss() if hasattr(self, 'dialog') else None
        self.grade_dialog.dismiss() if hasattr(self, 'grade_dialog') else None





