from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from utils.db_utils import get_students_in_class_with_gpa, get_student_grade_details, get_subject_id_by_teacher_code, get_class_name_by_id
from utils.db_utils import update_student_grade, get_student_id_by_code


class ClassDisplay(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.class_id = None
        self.dialog = None
        self.students_data = []
        self.sort_order = None  


    def on_enter(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        teacher_code = app.username
        subject_id = get_subject_id_by_teacher_code(teacher_code)


        self.students_data = get_students_in_class_with_gpa(self.class_id, subject_id)
        self.class_name = get_class_name_by_id(self.class_id)
 
        title_label = MDLabel(
            text=f"Class {self.class_name}",
            halign="center",
            font_style="H5",
            size_hint=(1, None),
            height=50,
            pos_hint={"center_x": 0.5, "top": 0.95},
            bold =True,
            theme_text_color="Custom",
        )
        self.add_widget(title_label)


        menu_items = [
            {"text": "Sort GPA (ASC)", "on_release": lambda x="gpa_asc": self.sort_students(x)},
            {"text": "Sort GPA (DESC)", "on_release": lambda x="gpa_desc": self.sort_students(x)},
            {"text": "Sort by Name (A-Z)", "on_release": lambda x="name_asc": self.sort_students(x)},
            {"text": "Sort by Name (Z-A)", "on_release": lambda x="name_desc": self.sort_students(x)},
            {"text": "Clear Sort", "on_release": lambda x=None: self.sort_students(x)},
        ]


        self.menu = MDDropdownMenu(
            caller=title_label,
            items=menu_items,
            width_mult=3,
        )
        sort_button = MDRaisedButton(
            text="Sort Options",
            pos_hint={"center_x": 0.8, "top": 0.9},
            size_hint=(0.2, None),
            on_release=lambda x: self.menu.open()
        )
        self.add_widget(sort_button)


        self.scroll_view = MDScrollView(size_hint=(1, None), height=500, pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.students_layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        self.students_layout.bind(minimum_height=self.students_layout.setter("height"))
        self.scroll_view.add_widget(self.students_layout)
        self.add_widget(self.scroll_view)


        self.display_students()


        back_button = MDRaisedButton(
            text="Back",
            size_hint=(0.3, None),
            height=50,
            pos_hint={"center_x": 0.5, "y": 0.05},
            on_release=self.go_back
        )
        self.add_widget(back_button)


    def display_students(self):
        # self.students_layout.clear_widgets()
        # for student_id, student_code, student_name, gpa in self.students_data:
        #     gpa_display = f"{gpa:.2f}" if gpa is not None else "N/A"
        #     item = OneLineListItem(
        #         text=f"{student_name} ({student_code}) - GPA: {gpa_display}",
        #         on_release=lambda instance, code=student_code, name=student_name: self.show_student_grade(instance, code, name),
        #     )
        #     self.students_layout.add_widget(item)


        if hasattr(self, 'data_table'):
            self.remove_widget(self.data_table)


        table_data = []
        for student_id, student_code, student_name, gpa in self.students_data:
            gpa_display = f"{gpa:.2f}" if gpa is not None else "N/A"
            table_data.append((student_name, student_code, gpa_display))


        self.data_table = MDDataTable(
            size_hint=(0.95, 0.6),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("Name", dp(30)),
                ("Code", dp(30)),
                ("GPA", dp(20)),
            ],
            row_data=table_data,
        )
        self.data_table.bind(on_row_press=self.on_row_press)
        self.add_widget(self.data_table)


    def on_row_press(self, instance_table, instance_row):
        name = instance_row.text
        selected_data = None
        for student in self.students_data:
            if name in student:
                selected_data = student
                break
        if selected_data:
            _, code, name, _ = selected_data
            self.show_student_grade(None, code, name)


    def sort_students(self, order):
        self.sort_order = order
        if order == "gpa_asc":
            self.students_data.sort(key=lambda x: (x[3] is None, x[3]))
        elif order == "gpa_desc":
            self.students_data.sort(key=lambda x: (x[3] is None, -x[3] if x[3] is not None else 0))
        elif order == "name_asc":
            self.students_data.sort(key=lambda x: x[2].lower())  # student_name
        elif order == "name_desc":
            self.students_data.sort(key=lambda x: x[2].lower(), reverse=True)
        self.display_students()
        self.menu.dismiss()




    def show_student_grade(self, instance, student_code, student_name):
        app = MDApp.get_running_app()
        teacher_code = app.username
        subject_id = get_subject_id_by_teacher_code(teacher_code)


        grade_details = get_student_grade_details(student_code, subject_id)
        if grade_details:
            subject_name, attendance, midterm, final, gpa = grade_details
            text = (
                f"[b]Student:[/b] {student_name} ({student_code})\n"
                f"[b]Subject:[/b] {subject_name}\n"
                f"[b]Attendance (10%):[/b] {attendance}\n"
                f"[b]Midterm (40%):[/b] {midterm}\n"
                f"[b]Final (50%):[/b] {final}\n"
                f"[b]GPA:[/b] {gpa}"
            )
        else:
            text = f"No grade information found for {student_name} ({student_code})."


        self.dialog = MDDialog(
            title="Student Grade Details",
            text=text,
            buttons=[
                MDRaisedButton(text="Change", on_release=self.edit_student_grade),
                MDRaisedButton(text="Close", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.student_code = student_code
        self.dialog.open()


    def go_back(self, instance):
        self.manager.current = "teacher_classes"
        if self.dialog:
            self.dialog.dismiss()


    def edit_student_grade(self, instance):
        self.dialog.dismiss()
        # Tạo dialog mới để nhập điểm
        self.grade_inputs = {
            "attendance": MDTextField(hint_text="Attendance (10%)"),
            "midterm": MDTextField(hint_text="Midterm (40%)"),
            "final": MDTextField(hint_text="Final (50%)"),
        }


        content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=300, padding=10)
        for field in self.grade_inputs.values():
            content.add_widget(field)


        self.edit_dialog = MDDialog(
            title="Edit Grades",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Save", on_release=self.save_updated_grade),
                MDRaisedButton(text="Cancel", on_release=lambda x: self.edit_dialog.dismiss())
            ]
        )
        self.edit_dialog.open()


    def save_updated_grade(self, instance):
        try:
            attendance_text = self.grade_inputs["attendance"].text.strip()
            midterm_text = self.grade_inputs["midterm"].text.strip()
            final_text = self.grade_inputs["final"].text.strip()


            if not attendance_text or not midterm_text or not final_text:
                raise ValueError("Please fill all grade fields.")


            attendance = float(attendance_text)
            midterm = float(midterm_text)
            final = float(final_text)
            gpa = round(attendance * 0.1 + midterm * 0.4 + final * 0.5, 2)


            app = MDApp.get_running_app()
            teacher_code = app.username
            subject_id = get_subject_id_by_teacher_code(teacher_code)


            student_code = self.dialog.student_code
            student_id = get_student_id_by_code(student_code)  # bạn cần có hàm này


            update_student_grade(student_id, subject_id, attendance, midterm, final, gpa)


            self.edit_dialog.dismiss()
            self.on_enter()  # refresh màn hình
        except ValueError as ve:
            print("Invalid input:", ve)
            # Bạn có thể hiện thông báo lỗi bằng dialog để user biết
        except Exception as e:
            print("Unexpected error:", e)





