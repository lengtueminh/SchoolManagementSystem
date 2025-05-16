from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty, StringProperty, DictProperty
from kivymd.uix.gridlayout import MDGridLayout
from kivy.core.window import Window
from utils.db_utils import get_all_students, get_all_teachers, get_all_classes, get_all_subjects, ad_update_student_details, get_students_of_class, ad_update_teacher_details, ad_add_student, ad_add_teacher, ad_add_class, ad_add_subject, ad_delete_student, ad_delete_teacher, ad_delete_class, ad_delete_subject

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
    required_width = NumericProperty(0)
    dialog = None
    edit_dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        if self.headers:
            widths = [self.column_widths.get(header, 100) for header in self.headers]
            spacing = 20
            self.required_width = sum(widths) + (len(self.headers) - 1) * spacing
        else:
            self.required_width = 0

        self.search_field = MDTextField(
            hint_text="Search...",
            size_hint_y=None,
            height=40,
            pos_hint={'center_x': 0.5},
        )
        self.search_field.bind(text=lambda instance, text: setattr(self, 'search_query', text))
        self.add_widget(self.search_field)

        num_cols = len(self.headers) if self.headers else 1
        self.table_layout = MDGridLayout(cols=num_cols, spacing=20, adaptive_height=True)
        self.table_layout.size_hint_x = None
        self.table_layout.width = self.required_width

        self.scroll_view = ScrollView(
            size_hint_y=1,
            do_scroll_x=True,
            do_scroll_y=True,
            bar_width=10,
            scroll_type=['bars', 'content']
        )
        self.scroll_view.add_widget(self.table_layout)
        self.add_widget(self.scroll_view)

        self.pagination_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=40,
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
        self.current_page = 1
        self.update_table()

    def on_current_page(self, instance, value):
        self.update_table()
        self.page_label.text = f"Page {self.current_page}"

    def update_table(self):
        if not hasattr(self, 'scroll_view'):
            return

        self.table_layout.clear_widgets()
        self.table_layout.cols = len(self.headers)
        if self.headers:
            widths = [self.column_widths.get(header, 100) for header in self.headers]
            spacing = 20
            self.required_width = sum(widths) + (len(self.headers) - 1) * spacing
        else:
            self.required_width = 0
        self.table_layout.size_hint_x = None
        self.table_layout.width = self.required_width

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

        total_items = len(self.filtered_data)
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        current_page_data = self.filtered_data[start_index:end_index]

        for item in current_page_data:
            for header in self.headers:
                width = self.column_widths.get(header, 100)
                if header == 'Action':
                    action_layout = MDBoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=40)
                    if self.headers == ['Class ID', 'Class Name', 'Action']:
                        class_id = item.get('id', '')
                        edit_button = MDRaisedButton(
                            text="View Students",
                            size_hint=(None, None),
                            size=(120, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, cid=class_id: self.view_students_of_class(cid)
                        )
                        action_layout.add_widget(edit_button)
                    elif self.headers == ['ID', 'Code', 'Name', 'Birthday', 'Class', 'Address', 'Action']:
                        student_code = item.get('code', '')
                        edit_button = MDRaisedButton(
                            text="Edit",
                            size_hint=(None, None),
                            size=(60, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, scode=student_code: self.edit_student(scode)
                        )
                        delete_button = MDRaisedButton(
                            text="Delete",
                            size_hint=(None, None),
                            size=(60, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, scode=student_code: self.delete_item(scode, 'student')
                        )
                        action_layout.add_widget(edit_button)
                        action_layout.add_widget(delete_button)
                    elif self.headers == ['ID', 'Code', 'Name', 'Subject', 'Email', 'Action']:
                        teacher_code = item.get('code', '')
                        edit_button = MDRaisedButton(
                            text="Edit",
                            size_hint=(None, None),
                            size=(60, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, tcode=teacher_code: self.edit_teacher(tcode)
                        )
                        delete_button = MDRaisedButton(
                            text="Delete",
                            size_hint=(None, None),
                            size=(60, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, tcode=teacher_code: self.delete_item(tcode, 'teacher')
                        )
                        action_layout.add_widget(edit_button)
                        action_layout.add_widget(delete_button)
                    elif self.headers == ['Class ID', 'Class Name', 'Action']:
                        class_id = item.get('id', '')
                        edit_button = MDRaisedButton(
                            text="View Students",
                            size_hint=(None, None),
                            size=(120, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, cid=class_id: self.view_students_of_class(cid)
                        )
                        delete_button = MDRaisedButton(
                            text="Delete",
                            size_hint=(None, None),
                            size=(60, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, cid=class_id: self.delete_item(cid, 'class')
                        )
                        action_layout.add_widget(edit_button)
                        action_layout.add_widget(delete_button)
                    elif self.headers == ['Subject ID', 'Subject Name', 'Action']:
                        subject_id = item.get('subjectid', '')
                        delete_button = MDRaisedButton(
                            text="Delete",
                            size_hint=(None, None),
                            size=(60, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, sid=subject_id: self.delete_item(sid, 'subject')
                        )
                        action_layout.add_widget(delete_button)
                    self.table_layout.add_widget(action_layout)
                else:
                    actual_key = self.column_map.get(header, header)
                    text = str(item.get(actual_key, ''))
                    if self.headers == ['Class ID', 'Class Name', 'Action'] or self.headers == ['Subject ID', 'Subject Name']:
                        self.table_layout.add_widget(MDLabel(
                            text=text,
                            halign='center',
                            valign='middle',
                            size_hint_y=None,
                            height=40,
                            size_hint_x=None,
                            width=width,
                            text_size=(width, 40),
                        ))
                    else:
                        self.table_layout.add_widget(MDLabel(
                            text=text,
                            halign='left',
                            valign='middle',
                            size_hint_y=None,
                            height=40,
                            size_hint_x=None,
                            width=width,
                            text_size=(width, 40),
                        ))

    def view_students_of_class(self, cid):
        students_data = get_students_of_class(cid)
        if not students_data:
            toast(f"No students found for class ID {cid}.")
            return

        content = PaginatedTableView(
            full_data=students_data,
            headers=['ID', 'Code', 'Name', 'Birthday', 'Class', 'Address', 'Action'],
            column_map={
                'ID': 'id',
                'Code': 'code',
                'Name': 'name',
                'Birthday': 'birthdate',
                'Class': 'classname',
                'Address': 'address'
            },
            search_fields=['name', 'code'],
            column_widths={
                'ID': 60,
                'Code': 100,
                'Name': 200,
                'Birthday': 100,
                'Class': 100,
                'Address': 300,
                'Action': 150
            },
            items_per_page=10,
            size_hint_y=None,
            height=Window.height * 0.7,
        )
        Clock.schedule_once(lambda dt: content.update_table(), 0)

        self.dialog = MDDialog(
            title=f"Students of Class ID {cid}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Close", on_release=self.close_dialog),
                MDRaisedButton(text="Add", on_release=lambda instance: self.add_student())
            ]
        )
        max_width = Window.width * 0.95
        if content.required_width > max_width:
            self.dialog.size_hint_x = None
            self.dialog.width = max_width
        else:
            self.dialog.size_hint_x = None
            self.dialog.width = content.required_width
        self.dialog.open()

    def edit_student(self, student_code):
        student = next((item for item in self.full_data if item.get('code') == student_code), None)
        if not student:
            toast("Student not found.")
            return

        classes = get_all_classes()
        if not classes:
            toast("Could not load classes.")
            return

        edit_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None, height=350)

        self.name_field = MDTextField(
            hint_text="Name",
            text=student.get('name', ''),
            size_hint_y=None,
            height=40,
        )
        self.address_field = MDTextField(
            hint_text="Address",
            text=student.get('address', ''),
            size_hint_y=None,
            height=40,
        )
        self.birthdate_field = MDTextField(
            hint_text="Birthdate (YYYY-MM-DD)",
            text=str(student.get('birthdate', '')),
            size_hint_y=None,
            height=40,
        )

        self.class_field = MDTextField(
            hint_text="Select Class",
            text=student.get('classname', 'Select Class'),
            size_hint_y=None,
            height=40,
            mode="rectangle",
            readonly=True,
        )

        self.dropdown = DropDown()
        for class_item in classes:
            btn = Button(
                text=class_item["classname"],
                size_hint_y=None,
                height=40,
            )
            btn.bind(on_release=lambda btn, cid=class_item["id"], cname=class_item["classname"]: self.set_class(cid, cname))
            self.dropdown.add_widget(btn)

        self.class_field.bind(on_touch_down=self.open_dropdown)
        self.selected_class_id = None
        for class_item in classes:
            if class_item["classname"] == student.get('classname'):
                self.selected_class_id = class_item["id"]
                break

        edit_layout.add_widget(self.name_field)
        edit_layout.add_widget(self.address_field)
        edit_layout.add_widget(self.birthdate_field)
        edit_layout.add_widget(self.class_field)

        self.edit_dialog = MDDialog(
            title=f"Edit Student {student_code}",
            type="custom",
            content_cls=edit_layout,
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda instance: self.save_student_changes(student_code)
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_edit_dialog
                )
            ]
        )
        self.edit_dialog.open()

    def edit_teacher(self, teacher_code):
        teacher = next((item for item in self.full_data if item.get('code') == teacher_code), None)
        if not teacher:
            toast("Teacher not found.")
            return

        subjects = get_all_subjects()
        if not subjects:
            toast("Could not load subjects.")
            return

        edit_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None, height=280)

        self.teacher_name_field = MDTextField(
            hint_text="Name",
            text=teacher.get('name', ''),
            size_hint_y=None,
            height=40,
        )
        self.email_field = MDTextField(
            hint_text="Email",
            text=teacher.get('email', ''),
            size_hint_y=None,
            height=40,
        )

        self.subject_field = MDTextField(
            hint_text="Select Subject",
            text=teacher.get('subjectname', 'Select Subject'),
            size_hint_y=None,
            height=40,
            mode="rectangle",
            readonly=True,
        )

        self.subject_dropdown = DropDown()
        for subject_item in subjects:
            btn = Button(
                text=subject_item["subjectname"],
                size_hint_y=None,
                height=40,
            )
            btn.bind(on_release=lambda btn, sid=subject_item["subjectid"], sname=subject_item["subjectname"]: self.set_subject(sid, sname))
            self.subject_dropdown.add_widget(btn)

        self.subject_field.bind(on_touch_down=self.open_subject_dropdown)
        self.selected_subject_id = None
        for subject_item in subjects:
            if subject_item["subjectname"] == teacher.get('subjectname'):
                self.selected_subject_id = subject_item["subjectid"]
                break

        edit_layout.add_widget(self.teacher_name_field)
        edit_layout.add_widget(self.email_field)
        edit_layout.add_widget(self.subject_field)

        self.edit_dialog = MDDialog(
            title=f"Edit Teacher {teacher_code}",
            type="custom",
            content_cls=edit_layout,
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda instance: self.save_teacher_changes(teacher_code)
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_edit_dialog
                )
            ]
        )
        self.edit_dialog.open()

    def add_student(self):
        classes = get_all_classes()
        if not classes:
            toast("Could not load classes.")
            return

        add_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None, height=350)

        self.add_name_field = MDTextField(
            hint_text="Name",
            size_hint_y=None,
            height=40,
        )
        self.add_address_field = MDTextField(
            hint_text="Address",
            size_hint_y=None,
            height=40,
        )
        self.add_birthdate_field = MDTextField(
            hint_text="Birthdate (YYYY-MM-DD)",
            size_hint_y=None,
            height=40,
        )

        self.add_class_field = MDTextField(
            hint_text="Select Class",
            text="Select Class",
            size_hint_y=None,
            height=40,
            mode="rectangle",
            readonly=True,
        )

        self.add_dropdown = DropDown()
        for class_item in classes:
            btn = Button(
                text=class_item["classname"],
                size_hint_y=None,
                height=40,
            )
            btn.bind(on_release=lambda btn, cid=class_item["id"], cname=class_item["classname"]: self.set_class(cid, cname, 'add'))
            self.add_dropdown.add_widget(btn)

        self.add_class_field.bind(on_touch_down=self.open_add_dropdown)
        self.selected_add_class_id = None

        add_layout.add_widget(self.add_name_field)
        add_layout.add_widget(self.add_address_field)
        add_layout.add_widget(self.add_birthdate_field)
        add_layout.add_widget(self.add_class_field)

        self.add_dialog = MDDialog(
            title="Add New Student",
            type="custom",
            content_cls=add_layout,
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda instance: self.save_new_student()
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_add_dialog
                )
            ]
        )
        self.add_dialog.open()

    def add_teacher(self):
        subjects = get_all_subjects()
        if not subjects:
            toast("Could not load subjects.")
            return

        add_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None, height=280)

        self.add_teacher_name_field = MDTextField(
            hint_text="Name",
            size_hint_y=None,
            height=40,
        )
        self.add_email_field = MDTextField(
            hint_text="Email",
            size_hint_y=None,
            height=40,
        )

        self.add_subject_field = MDTextField(
            hint_text="Select Subject",
            text="Select Subject",
            size_hint_y=None,
            height=40,
            mode="rectangle",
            readonly=True,
        )

        self.add_subject_dropdown = DropDown()
        for subject_item in subjects:
            btn = Button(
                text=subject_item["subjectname"],
                size_hint_y=None,
                height=40,
            )
            btn.bind(on_release=lambda btn, sid=subject_item["subjectid"], sname=subject_item["subjectname"]: self.set_subject(sid, sname, 'add'))
            self.add_subject_dropdown.add_widget(btn)

        self.add_subject_field.bind(on_touch_down=self.open_add_subject_dropdown)
        self.selected_add_subject_id = None

        add_layout.add_widget(self.add_teacher_name_field)
        add_layout.add_widget(self.add_email_field)
        add_layout.add_widget(self.add_subject_field)

        self.add_dialog = MDDialog(
            title="Add New Teacher",
            type="custom",
            content_cls=add_layout,
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda instance: self.save_new_teacher()
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_add_dialog
                )
            ]
        )
        self.add_dialog.open()

    def add_class(self):
        add_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None, height=100)

        self.add_classname_field = MDTextField(
            hint_text="Class Name",
            size_hint_y=None,
            height=40,
        )

        add_layout.add_widget(self.add_classname_field)

        self.add_dialog = MDDialog(
            title="Add New Class",
            type="custom",
            content_cls=add_layout,
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda instance: self.save_new_class()
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_add_dialog
                )
            ]
        )
        self.add_dialog.open()

    def add_subject(self):
        add_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None, height=100)

        self.add_subjectname_field = MDTextField(
            hint_text="Subject Name",
            size_hint_y=None,
            height=40,
        )

        add_layout.add_widget(self.add_subjectname_field)

        self.add_dialog = MDDialog(
            title="Add New Subject",
            type="custom",
            content_cls=add_layout,
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda instance: self.save_new_subject()
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_add_dialog
                )
            ]
        )
        self.add_dialog.open()

    def open_dropdown(self, instance, touch):
        if instance.collide_point(*touch.pos) and touch.button == 'left':
            self.dropdown.open(instance)

    def open_subject_dropdown(self, instance, touch):
        if instance.collide_point(*touch.pos) and touch.button == 'left':
            self.subject_dropdown.open(instance)

    def open_add_dropdown(self, instance, touch):
        if instance.collide_point(*touch.pos) and touch.button == 'left':
            self.add_dropdown.open(instance)

    def open_add_subject_dropdown(self, instance, touch):
        if instance.collide_point(*touch.pos) and touch.button == 'left':
            self.add_subject_dropdown.open(instance)

    def set_class(self, class_id, class_name, mode='edit'):
        if mode == 'edit':
            self.class_field.text = class_name
            self.selected_class_id = class_id
            self.dropdown.dismiss()
        else:  # mode == 'add'
            self.add_class_field.text = class_name
            self.selected_add_class_id = class_id
            self.add_dropdown.dismiss()

    def set_subject(self, subject_id, subject_name, mode='edit'):
        if mode == 'edit':
            self.subject_field.text = subject_name
            self.selected_subject_id = subject_id
            self.subject_dropdown.dismiss()
        else:  # mode == 'add'
            self.add_subject_field.text = subject_name
            self.selected_add_subject_id = subject_id
            self.add_subject_dropdown.dismiss()

    def save_student_changes(self, student_code):
        new_name = self.name_field.text.strip()
        new_address = self.address_field.text.strip()
        new_birthdate = self.birthdate_field.text.strip()
        new_class_id = self.selected_class_id

        if not new_name or not new_address or not new_birthdate or not new_class_id:
            toast("All fields are required.")
            return

        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", new_birthdate):
            toast("Birthdate must be in YYYY-MM-DD format.")
            return

        success = ad_update_student_details(student_code, new_name, new_address, new_birthdate, new_class_id)
        if success:
            toast("Student updated successfully.")
            if self.headers == ['ID', 'Code', 'Name', 'Birthday', 'Class', 'Address', 'Action']:
                self.full_data = get_all_students()
                self.filtered_data = self.full_data
            else:
                class_id = next((item['id'] for item in self.full_data if item.get('code') == student_code), None)
                if class_id:
                    self.full_data = get_students_of_class(class_id)
                    self.filtered_data = self.full_data
            self.update_table()
        else:
            toast("Failed to update student.")

        self.close_edit_dialog(None)

    def save_teacher_changes(self, teacher_code):
        new_name = self.teacher_name_field.text.strip()
        new_email = self.email_field.text.strip()
        new_subject_id = self.selected_subject_id

        if not new_name or not new_email or not new_subject_id:
            toast("All fields are required.")
            return

        import re
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", new_email):
            toast("Invalid email format.")
            return

        success = ad_update_teacher_details(teacher_code, new_name, new_subject_id, new_email)
        if success:
            toast("Teacher updated successfully.")
            self.full_data = get_all_teachers()
            self.filtered_data = self.full_data
            self.update_table()
        else:
            toast("Failed to update teacher.")

        self.close_edit_dialog(None)

    def save_new_student(self):
        new_name = self.add_name_field.text.strip()
        new_address = self.add_address_field.text.strip()
        new_birthdate = self.add_birthdate_field.text.strip()
        new_class_id = self.selected_add_class_id

        if not new_name or not new_address or not new_birthdate or not new_class_id:
            toast("All fields are required.")
            return

        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", new_birthdate):
            toast("Birthdate must be in YYYY-MM-DD format.")
            return

        success = ad_add_student(new_name, new_address, new_birthdate, new_class_id)
        if success:
            toast("Student added successfully.")
            if self.headers == ['ID', 'Code', 'Name', 'Birthday', 'Class', 'Address', 'Action']:
                self.full_data = get_all_students()
                self.filtered_data = self.full_data
            else:
                class_id = next((item['id'] for item in self.full_data if item.get('code') == student_code), None)
                if class_id:
                    self.full_data = get_students_of_class(class_id)
                    self.filtered_data = self.full_data
            self.update_table()
        else:
            toast("Failed to add student.")

        self.close_add_dialog(None)

    def save_new_teacher(self):
        new_name = self.add_teacher_name_field.text.strip()
        new_email = self.add_email_field.text.strip()
        new_subject_id = self.selected_add_subject_id

        if not new_name or not new_email or not new_subject_id:
            toast("All fields are required.")
            return

        import re
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", new_email):
            toast("Invalid email format.")
            return

        success = ad_add_teacher(new_name, new_subject_id, new_email)
        if success:
            toast("Teacher added successfully.")
            self.full_data = get_all_teachers()
            self.filtered_data = self.full_data
            self.update_table()
        else:
            toast("Failed to add teacher.")

        self.close_add_dialog(None)

    def save_new_class(self):
        new_classname = self.add_classname_field.text.strip()

        if not new_classname:
            toast("Class name is required.")
            return

        success = ad_add_class(new_classname)
        if success:
            toast("Class added successfully.")
            self.full_data = get_all_classes()
            self.filtered_data = self.full_data
            self.update_table()
        else:
            toast("Failed to add class.")

        self.close_add_dialog(None)

    def save_new_subject(self):
        new_subjectname = self.add_subjectname_field.text.strip()

        if not new_subjectname:
            toast("Subject name is required.")
            return

        success = ad_add_subject(new_subjectname)
        if success:
            toast("Subject added successfully.")
            self.full_data = get_all_subjects()
            self.filtered_data = self.full_data
            self.update_table()
        else:
            toast("Failed to add subject.")

        self.close_add_dialog(None)

    def delete_item(self, code, item_type):
        if item_type == 'student':
            success = ad_delete_student(code)
            if success:
                toast("Student deleted successfully.")
                if self.headers == ['ID', 'Code', 'Name', 'Birthday', 'Class', 'Address', 'Action']:
                    self.full_data = get_all_students()
                    self.filtered_data = self.full_data
                else:
                    class_id = next((item['id'] for item in self.full_data if item.get('code') == code), None)
                    if class_id:
                        self.full_data = get_students_of_class(class_id)
                        self.filtered_data = self.full_data
                self.update_table()
            else:
                toast("Failed to delete student.")
        elif item_type == 'teacher':
            success = ad_delete_teacher(code)
            if success:
                toast("Teacher deleted successfully.")
                self.full_data = get_all_teachers()
                self.filtered_data = self.full_data
                self.update_table()
            else:
                toast("Failed to delete teacher.")
        elif item_type == 'class':
            success = ad_delete_class(code)
            if success:
                toast("Class deleted successfully.")
                self.full_data = get_all_classes()
                self.filtered_data = self.full_data
                self.update_table()
            else:
                toast("Failed to delete class.")
        elif item_type == 'subject':
            success = ad_delete_subject(code)
            if success:
                toast("Subject deleted successfully.")
                self.full_data = get_all_subjects()
                self.filtered_data = self.full_data
                self.update_table()
            else:
                toast("Failed to delete subject.")

    def close_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss()

    def close_edit_dialog(self, instance):
        if self.edit_dialog:
            self.edit_dialog.dismiss()

    def close_add_dialog(self, instance):
        if self.add_dialog:
            self.add_dialog.dismiss()

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
                headers=['ID', 'Code', 'Name', 'Birthday', 'Class', 'Address', 'Action'],
                column_map={
                    'ID': 'id',
                    'Code': 'code',
                    'Name': 'name',
                    'Birthday': 'birthdate',
                    'Class': 'classname',
                    'Address': 'address'
                },
                search_fields=['name', 'code'],
                column_widths={
                    'ID': 60,
                    'Code': 100,
                    'Name': 200,
                    'Birthday': 100,
                    'Class': 100,
                    'Address': 300,
                    'Action': 150
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7,
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Students List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog),
                    MDRaisedButton(text="Add", on_release=lambda instance: content.add_student())
                ]
            )
            max_width = Window.width * 0.95
            if content.required_width > max_width:
                self.dialog.size_hint_x = None
                self.dialog.width = max_width
            else:
                self.dialog.size_hint_x = None
                self.dialog.width = content.required_width
            self.dialog.open()
        else:
            toast("Could not load students data.")

    def show_teachers_table(self, instance):
        teachers_data = get_all_teachers()
        if teachers_data:
            content = PaginatedTableView(
                full_data=teachers_data,
                headers=['ID', 'Code', 'Name', 'Subject', 'Email', 'Action'],
                column_map={
                    'ID': 'id',
                    'Code': 'code',
                    'Name': 'name',
                    'Subject': 'subjectname',
                    'Email': 'email'
                },
                search_fields=['name', 'code'],
                column_widths={
                    'ID': 60,
                    'Code': 100,
                    'Name': 200,
                    'Subject': 120,
                    'Email': 250,
                    'Action': 150
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7,
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Teachers List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog),
                    MDRaisedButton(text="Add", on_release=lambda instance: content.add_teacher())
                ]
            )
            max_width = Window.width * 0.95
            if content.required_width > max_width:
                self.dialog.size_hint_x = None
                self.dialog.width = max_width
            else:
                self.dialog.size_hint_x = None
                self.dialog.width = content.required_width
            self.dialog.open()
        else:
            toast("Could not load teachers data.")

    def show_classes_table(self, instance):
        classes_data = get_all_classes()
        if classes_data:
            content = PaginatedTableView(
                full_data=classes_data,
                headers=['Class ID', 'Class Name', 'Action'],
                column_map={
                    'Class ID': 'id',
                    'Class Name': 'classname'
                },
                search_fields=['classname'],
                column_widths={
                    'Class ID': 60,
                    'Class Name': 250,
                    'Action': 150
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7,
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Classes List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog),
                    MDRaisedButton(text="Add", on_release=lambda instance: content.add_class())
                ]
            )
            max_width = Window.width * 0.95
            if content.required_width > max_width:
                self.dialog.size_hint_x = None
                self.dialog.width = max_width
            else:
                self.dialog.size_hint_x = None
                self.dialog.width = content.required_width
            self.dialog.open()
        else:
            toast("Could not load classes data.")

    def show_subjects_table(self, instance):
        subjects_data = get_all_subjects()
        if subjects_data:
            content = PaginatedTableView(
                full_data=subjects_data,
                headers=['Subject ID', 'Subject Name', 'Action'],
                column_map={
                    'Subject ID': 'subjectid',
                    'Subject Name': 'subjectname'
                },
                search_fields=['subjectname'],
                column_widths={
                    'Subject ID': 60,
                    'Subject Name': 300,
                    'Action': 150
                },
                items_per_page=10,
                size_hint_y=None,
                height=Window.height * 0.7,
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)

            self.dialog = MDDialog(
                title="Subjects List",
                type="custom",
                content_cls=content,
                buttons=[
                    MDRaisedButton(text="Close", on_release=self.close_dialog),
                    MDRaisedButton(text="Add", on_release=lambda instance: content.add_subject())
                ]
            )
            max_width = Window.width * 0.95
            if content.required_width > max_width:
                self.dialog.size_hint_x = None
                self.dialog.width = max_width
            else:
                self.dialog.size_hint_x = None
                self.dialog.width = content.required_width
            self.dialog.open()
        else:
            toast("Could not load subjects data.")

    def close_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss()
