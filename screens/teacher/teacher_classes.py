from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.app import MDApp
from kivymd.uix.scrollview import MDScrollView, ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

from utils.db_utils import get_classes_by_teacher, get_student_grade, get_student_count_by_class
from kivymd.uix.boxlayout import MDBoxLayout




class TeacherClassesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def on_enter(self):
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


        # container = MDBoxLayout(
        #     orientation='vertical',
        #     spacing=20,
        #     padding=[0, 20],
        #     size_hint=(0.8, None),
        #     pos_hint={"center_x": 0.5},
        # )
        # container.bind(minimum_height=container.setter('height'))
        grid = MDGridLayout(
            cols=2,
            spacing=20,
            padding=[20, 20],
            adaptive_height=True,
            size_hint=(None, None),
            width=360,
            pos_hint={"center_x": 0.5},
        )
        grid.bind(minimum_height=grid.setter('height'))

        self.classes = get_classes_by_teacher(teacher_code)
        for class_id, class_name in self.classes:
            student_count = get_student_count_by_class(class_id=class_id) #
            # card = MDCard(
            #     orientation='horizontal',
            #     padding=15,
            #     size_hint=(None, None),
            #     size=(300, 100),
            #     ripple_behavior=True,
            #     pos_hint={"center_x": 0.5},
            #     on_release=lambda card, cid=class_id: self.show_students(card, cid),
            # )
            card = MDCard(
                orientation='vertical',
                padding=15,
                size_hint=(None, None),
                size=(160, 120),
                ripple_behavior=True,
                radius=[15, 15, 15, 15],
                # md_bg_color=(0.9, 0.95, 1, 1),
                elevation=1,
                on_release=lambda card, cid=class_id: self.show_students(card, cid),
                pos_hint={"center_x": 0.5},
            )
            box = MDBoxLayout(
                orientation='vertical', 
                spacing=5, 
                padding=5,
                adaptive_height=True,)

            # 📚 Icon lớp học
            icon = MDIconButton(
                icon="school",
                theme_text_color="Custom",
                text_color=(0.2, 0.4, 0.6, 1),
                pos_hint={"center_x": 0.5},
                icon_size="32sp",
            )

            label = MDLabel(
                text=class_name,
                halign="center",
                font_style="Subtitle1",
                theme_text_color="Primary",
                size_hint_y=None,
                height=25,
                # valign="center"
                )
            student_info = MDLabel(
            text=f"{student_count} students",
            halign="center",
            font_style="Caption",
            theme_text_color="Hint",
            size_hint_y=None,
            height=20,
            )
           
            # card.add_widget(label)
            # container.add_widget(card)
            box.add_widget(icon)
            box.add_widget(label)
            box.add_widget(student_info)
            card.add_widget(box)
            grid.add_widget(card)


        # scroll = MDScrollView(
        #     size_hint=(1, 0.8), 
        #     pos_hint={"center_x": 0.5, "center_y": 0.45})
        # scroll.add_widget(grid)
        # self.add_widget(scroll)
        wrapper = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, 0.8),
            padding=[0, 60, 0, 0],
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            )

        scroll = MDScrollView(
        do_scroll_x=False,
        size_hint=(None, None),
        size=(360, 400),
        pos_hint={"center_x": 0.5}
    )
        scroll.add_widget(grid)

        wrapper.add_widget(scroll)
        self.add_widget(wrapper)

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





