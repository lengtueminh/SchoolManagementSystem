from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty, StringProperty, DictProperty
from kivymd.uix.gridlayout import MDGridLayout
from kivy.core.window import Window
from utils.db_utils import get_all_students, get_all_teachers, get_all_classes, get_all_subjects, update_student_details

class PaginatedTableView(MDBoxLayout):
    full_data = ListProperty([])
    filtered_data = ListProperty([])
    search_fields = ListProperty([])
    search_query = StringProperty('')
    items_per_page = NumericProperty(10)
    current_page = NumericProperty(1)
    headers = ListProperty([])
    column_map = DictProperty({})
    column_widths = DictProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Thêm thanh tìm kiếm
        self.search_field = MDTextField(
            hint_text="Search...",
            size_hint_y=None,
            height=40,
            pos_hint={'center_x': 0.5},
        )
        self.search_field.bind(text=lambda instance, text: setattr(self, 'search_query', text))
        self.add_widget(self.search_field)

        # Layout bảng
        num_cols = len(self.headers) if self.headers else 1
        self.table_layout = MDGridLayout(cols=num_cols, spacing=20, adaptive_height=True)
        self.scroll_view = ScrollView()
        self.scroll_view.add_widget(self.table_layout)
        self.add_widget(self.scroll_view)

        # Layout phân trang
        self.pagination_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=30,
            padding=10,
            spacing=10
        )
        self.page_label = MDLabel(text=f"Page {self.current_page}", halign='center')
        prev_button = MDRaisedButton(text='Previous', on_release=self.prev_page, size_hint_x=None, width=120)
        next_button = MDRaisedButton(text='Next', on_release=self.next_page, size_hint_x=None, width=120)
        self.pagination_layout.add_widget(prev_button)
        self.pagination_layout.add_widget(self.page_label)
        self.pagination_layout.add_widget(next_button)
        self.add_widget(self.pagination_layout)

    def on_full_data(self, instance, value):
        self.filtered_data = value
        self.update_table()

    def on_search_query(self, instance, value):
        if value:
            query = value.lower()
            self.filtered_data = [item for item in self.full_data if any(query in str(item.get(field, '')).lower() for field in self.search_fields)]
        else:
            self.filtered_data = self.full_data
        self.current_page = 1  # Reset về trang đầu tiên khi tìm kiếm
        self.update_table()

    def on_current_page(self, instance, value):
        self.update_table()
        self.page_label.text = f"Page {self.current_page}"

    def update_table(self):
        if not hasattr(self, 'scroll_view'):
            return

        self.table_layout.clear_widgets()
        self.table_layout.cols = len(self.headers)

        # Hiển thị tiêu đề cột
        for header in self.headers:
            width = self.column_widths.get(header, 100)
            self.table_layout.add_widget(MDLabel(
                text=header,
                bold=True,
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=40,
                size_hint_x=None,
                width=width,
                text_size=(width, None),
            ))

        # Lấy dữ liệu của trang hiện tại
        total_items = len(self.filtered_data)
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        current_page_data = self.filtered_data[start_index:end_index]

        # Hiển thị dữ liệu từng hàng
        for item in current_page_data:
            for header in self.headers:
                actual_key = self.column_map.get(header, header)
                text = str(item.get(actual_key, ''))
                width = self.column_widths.get(header, 100)
                self.table_layout.add_widget(MDLabel(
                    text=text,
                    halign='left',
                    valign='middle',
                    size_hint_y=None,
                    height=40,
                    size_hint_x=None,
                    width=width,
                    text_size=(width, None),
                    shorten=False,
                ))

    def next_page(self, instance):
        total_pages = (len(self.filtered_data) + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages:
            self.current_page += 1

    def prev_page(self, instance):
        if self.current_page > 1:
            self.current_page -= 1

class AdminHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self):
        self.clear_widgets()

        app = MDApp.get_running_app()

        welcome_label = MDLabel(
            text=f"Welcome, Admin!",
            halign="center",
            pos_hint={"center_y": 0.95},
            font_style="H6"
        )

        buttons_layout = MDBoxLayout(orientation="vertical", spacing=15, size_hint=(0.6, None), height=300, pos_hint={"center_x": 0.5, "center_y": 0.5})

        students_button = MDRaisedButton(text="View Students", on_release=self.show_students_table)
        teachers_button = MDRaisedButton(text="View Teachers", on_release=self.show_teachers_table)
        classes_button = MDRaisedButton(text="View Classes", on_release=self.show_classes_table)
        subjects_button = MDRaisedButton(text="View Subjects", on_release=self.show_subjects_table)
        logout_button = MDRaisedButton(text="Log out", on_release=self.logout)

        buttons_layout.add_widget(students_button)
        buttons_layout.add_widget(teachers_button)
        buttons_layout.add_widget(classes_button)
        buttons_layout.add_widget(subjects_button)
        buttons_layout.add_widget(logout_button)

        self.add_widget(welcome_label)
        self.add_widget(buttons_layout)

    def logout(self, instance):
        app = MDApp.get_running_app()
        app.username = None
        app.role = None
        self.manager.current = "login_screen"

    def show_students_table(self, instance):
        students_data = get_all_students()
        if students_data:
            content = PaginatedTableView(
                full_data=students_data,
                headers=['Student ID', 'Student Code', 'Student Name', 'Birth Date', 'Class Name', 'Address'],
                column_map={
                    'Student ID': 'id',
                    'Student Code': 'code',
                    'Student Name': 'name',
                    'Birth Date': 'birthdate',
                    'Class Name': 'classname',
                    'Address': 'address'
                },
                search_fields=['name', 'code'],
                column_widths={
                    'Student ID': 60,
                    'Student Code': 100,
                    'Student Name': 120,
                    'Birth Date': 100,
                    'Class Name': 100,
                    'Address': 200
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7,
                size_hint_x=None,
                width=Window.width * 0.9
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Students List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog)
                ]
            )
            self.dialog.open()
        else:
            toast("Could not load students data.")

    def show_teachers_table(self, instance):
        teachers_data = get_all_teachers()
        if teachers_data:
            content = PaginatedTableView(
                full_data=teachers_data,
                headers=['Teacher ID', 'Teacher Code', 'Teacher Name', 'Subject Name', 'Email'],
                column_map={
                    'Teacher ID': 'id',
                    'Teacher Code': 'code',
                    'Teacher Name': 'name',
                    'Subject Name': 'subjectname',
                    'Email': 'email'
                },
                search_fields=['name', 'code'],
                column_widths={
                    'Teacher ID': 60,
                    'Teacher Code': 100,
                    'Teacher Name': 120,
                    'Subject Name': 120,
                    'Email': 150
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Teachers List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog)
                ]
            )
            self.dialog.open()
        else:
            toast("Could not load teachers data.")

    def show_classes_table(self, instance):
        classes_data = get_all_classes()
        if classes_data:
            content = PaginatedTableView(
                full_data=classes_data,
                headers=['Class ID', 'Class Name'],
                column_map={
                    'Class ID': 'id',
                    'Class Name': 'classname'
                },
                search_fields=['classname'],
                column_widths={
                    'Class ID': 60,
                    'Class Name': 150
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Classes List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog)
                ]
            )
            self.dialog.open()
        else:
            toast("Could not load classes data.")

    def show_subjects_table(self, instance):
        subjects_data = get_all_subjects()
        if subjects_data:
            content = PaginatedTableView(
                full_data=subjects_data,
                headers=['Subject ID', 'Subject Name'],
                column_map={
                    'Subject ID': 'subjectid',
                    'Subject Name': 'subjectname'
                },
                search_fields=['subjectname'],
                column_widths={
                    'Subject ID': 60,
                    'Subject Name': 150
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Subjects List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog)
                ]
            )
            self.dialog.open()
        else:
            toast("Could not load subjects data.")

    def close_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss()
# from kivymd.uix.screen import MDScreen
# from kivymd.uix.label import MDLabel
# from kivymd.uix.button import MDRaisedButton
# from kivymd.app import MDApp
# from kivymd.uix.boxlayout import MDBoxLayout
# from kivymd.uix.dialog import MDDialog
# from kivymd.uix.textfield import MDTextField
# from kivymd.toast import toast
# from kivy.uix.scrollview import ScrollView
# from kivy.clock import Clock
# from kivy.properties import NumericProperty, ListProperty
# from kivymd.uix.gridlayout import MDGridLayout
# from kivy.core.window import Window
# from utils.db_utils import get_all_students, get_all_teachers, get_all_classes, get_all_subjects, update_student_details

# class PaginatedTableView(MDBoxLayout):
#     data = ListProperty([])
#     items_per_page = NumericProperty(10)
#     current_page = NumericProperty(1)
#     headers = ListProperty([])

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#         self.orientation = 'vertical'

#         # Nếu headers chưa có thì tránh crash bằng col=1
#         num_cols = len(self.headers) if self.headers else 1
#         self.table_layout = MDGridLayout(cols=num_cols, spacing=20, adaptive_height=True)

#         self.scroll_view = ScrollView()
#         self.scroll_view.add_widget(self.table_layout)
#         self.add_widget(self.scroll_view)

#         self.pagination_layout = MDBoxLayout(
#             orientation='horizontal',
#             size_hint_y=None,
#             height=30,
#             padding=10,
#             spacing=10
#         )
#         self.page_label = MDLabel(text=f"Page {self.current_page}", halign='center')
#         prev_button = MDRaisedButton(text='Previous', on_release=self.prev_page, size_hint_x=None, width=120)
#         next_button = MDRaisedButton(text='Next', on_release=self.next_page, size_hint_x=None, width=120)
#         self.pagination_layout.add_widget(prev_button)
#         self.pagination_layout.add_widget(self.page_label)
#         self.pagination_layout.add_widget(next_button)
#         self.add_widget(self.pagination_layout)


#     def on_data(self, instance, value):
#         self.update_table()

#     def on_current_page(self, instance, value):
#         self.update_table()
#         self.page_label.text = f"Page {self.current_page}"

#     def update_table(self):
#         if not hasattr(self, 'scroll_view'):
#             print("scroll_view chưa được tạo, tạm hoãn update_table()")
#             return

#         self.table_layout.clear_widgets()
#         self.table_layout.cols = len(self.headers)

#         # Phân bố chiều rộng hợp lý cho từng cột
#         column_widths = {
#             'StudentID': 60,
#             'StudentCode': 100,
#             'StudentName': 120,
#             'BirthDate': 100,
#             'ClassID': 60,
#             'Address': 200,
#         }

#         # Lấy dữ liệu của trang hiện tại
#         start_index = (self.current_page - 1) * self.items_per_page
#         end_index = start_index + self.items_per_page
#         current_page_data = self.data[start_index:end_index]

#         # Header
#         for header in self.headers:
#             width = column_widths.get(header, 100)
#             self.table_layout.add_widget(MDLabel(
#                 text=header,
#                 bold=True,
#                 halign='center',
#                 valign='middle',
#                 size_hint_y=None,
#                 height=40,
#                 size_hint_x=None,
#                 width=width,
#                 text_size=(width, None),
#             ))

#         # Dữ liệu từng hàng
#         for item in current_page_data:
#             for header in self.headers:
#                 width = column_widths.get(header, 100)
#                 text = str(item.get(header, ''))
#                 self.table_layout.add_widget(MDLabel(
#                     text=text,
#                     halign='left',
#                     valign='middle',
#                     size_hint_y=None,
#                     height=40,
#                     size_hint_x=None,
#                     width=width,
#                     text_size=(width, None),
#                     shorten=False,
#                 ))




#     def next_page(self, instance):
#         total_pages = (len(self.data) + self.items_per_page - 1) // self.items_per_page
#         if self.current_page < total_pages:
#             self.current_page += 1

#     def prev_page(self, instance):
#         if self.current_page > 1:
#             self.current_page -= 1

# class AdminHomeScreen(MDScreen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.dialog = None # just declared 

#     def on_enter(self):
#         self.clear_widgets()

#         app = MDApp.get_running_app()

#         welcome_label = MDLabel(
#             text=f"Welcome, Admin!",
#             halign="center",
#             pos_hint={"center_y": 0.95},
#             font_style="H6"
#         )

#         admin_info = MDBoxLayout(orientation="vertical", spacing=5, size_hint_y=None, height=80)
    


#         # Tạo layout để chứa các nút, căn giữa và có khoảng cách
#         buttons_layout = MDBoxLayout(orientation="vertical", spacing=15, size_hint=(0.6, None), height=300, pos_hint={"center_x": 0.5, "center_y": 0.5})

#         students_button = MDRaisedButton(text="View Students", on_release=self.show_students_table)
#         teachers_button = MDRaisedButton(text="View Teachers", on_release=self.show_teachers_table)
#         classes_button = MDRaisedButton(text="View Classes", on_release=self.show_classes_table)
#         subjects_button = MDRaisedButton(text="View Subjects", on_release=self.show_subjects_table)
#         logout_button = MDRaisedButton(text="Log out", on_release=self.logout)

#         buttons_layout.add_widget(students_button)
#         buttons_layout.add_widget(teachers_button)
#         buttons_layout.add_widget(classes_button)
#         buttons_layout.add_widget(subjects_button)
#         buttons_layout.add_widget(logout_button)

#         self.add_widget(welcome_label)
#         self.add_widget(buttons_layout)

#     def logout(self, instance):
#         app = MDApp.get_running_app()
#         app.username = None
#         app.role = None
#         self.manager.current = "login_screen"

#     def show_students_table(self, instance):
#         students_data = get_all_students()
#         if students_data:
#             content = PaginatedTableView(
#                 data=students_data,
#                 headers=['StudentID', 'StudentCode', 'StudentName', 'BirthDate', 'ClassID', 'Address'],
#                 items_per_page=10,
#                 size_hint_y=None,
#                 height=Window.height * 0.7,
#                 size_hint_x=None,
#                 width=Window.width * 0.9,  # tăng chiều rộng một chút
#             )

#             Clock.schedule_once(lambda dt: content.update_table(), 0)

#             self.dialog = MDDialog(
#                 title="Students List",
#                 type="custom",
#                 content_cls=content,
#                 buttons=[
#                     MDRaisedButton(text="Close", on_release=self.close_dialog)
#                 ]
#             )
#             self.dialog.open()
#         else:
#             toast("Could not load students data.")

#     def show_teachers_table(self, instance):
#         teachers_data = get_all_teachers()
#         if teachers_data:
#             content = PaginatedTableView(
#                 data=teachers_data,
#                 headers=['TeacherID', 'TeacherCode', 'TeacherName', 'SubjectID', 'Email'],
#                 items_per_page=10,
#                 size_hint_y=None,
#                 height=Window.height * 0.7
#             )
#             Clock.schedule_once(lambda dt: content.update_table(), 0)

#             self.dialog = MDDialog(
#                 title="Teachers List",
#                 type="custom",
#                 content_cls=content,
#                 buttons=[
#                     MDRaisedButton(text="Close", on_release=self.close_dialog)
#                 ]
#             )
#             self.dialog.open()
#         else:
#             toast("Could not load teachers data.")

#     def show_classes_table(self, instance):
#         classes_data = get_all_classes()
#         if classes_data:
#             content = PaginatedTableView(
#                 data=classes_data,
#                 headers=['ClassID', 'ClassName'],
#                 items_per_page=10,
#                 size_hint_y=None,
#                 height=Window.height * 0.7
#             )
#             Clock.schedule_once(lambda dt: content.update_table(), 0)

#             self.dialog = MDDialog(
#                 title="Classes List",
#                 type="custom",
#                 content_cls=content,
#                 buttons=[
#                     MDRaisedButton(text="Close", on_release=self.close_dialog)
#                 ]
#             )
#             self.dialog.open()
#         else:
#             toast("Could not load classes data.")

#     def show_subjects_table(self, instance):
#         subjects_data = get_all_subjects()
#         if subjects_data:
#             content = PaginatedTableView(
#                 data=subjects_data,
#                 headers=['SubjectID', 'SubjectName'],
#                 items_per_page=10,
#                 size_hint_y=None,
#                 height=Window.height * 0.7
#             )
#             Clock.schedule_once(lambda dt: content.update_table(), 0)

#             self.dialog = MDDialog(
#                 title="Subjects List",
#                 type="custom",
#                 content_cls=content,
#                 buttons=[
#                     MDRaisedButton(text="Close", on_release=self.close_dialog)
#                 ]
#             )
#             self.dialog.open()
#         else:
#             toast("Could not load subjects data.")

#     def close_dialog(self, instance):
#         if self.dialog:
#             self.dialog.dismiss()