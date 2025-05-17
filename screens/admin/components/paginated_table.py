from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivy.uix.button import Button
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ListProperty, StringProperty, DictProperty
from utils.db_utils import (
    get_all_teachers, get_all_classes, get_all_subjects, get_all_students,
    ad_update_student_details, get_students_of_class,
    ad_update_teacher_details, ad_add_student, ad_add_teacher,
    ad_add_class, ad_add_subject, ad_delete_student,
    ad_delete_teacher, ad_delete_class, ad_delete_subject,
    get_teachers_by_subject, get_classID_by_name, connect_db
)
from kivymd.uix.gridlayout import MDGridLayout

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
    add_dialog = None
    viewing_subject_id = None

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

    def on_full_data(self, instance, value):
        self.filtered_data = value
        self.update_table()

    def on_search_query(self, instance, value):
        if value:
            query = value.lower()
            self.filtered_data = [item for item in self.full_data if any(query in str(item.get(field, '')).lower() for field in self.search_fields)]
        else:
            self.filtered_data = self.full_data
        self.update_table()

    def update_table(self):
        if not hasattr(self, 'scroll_view'):
            return

        self.table_layout.clear_widgets()
        
        # If no data and no headers, return early
        if not self.headers:
            return
            
        self.table_layout.cols = len(self.headers)
        if self.headers:
            widths = [self.column_widths.get(header, 100) for header in self.headers]
            spacing = 20
            self.required_width = sum(widths) + (len(self.headers) - 1) * spacing
        else:
            self.required_width = 0
        self.table_layout.size_hint_x = None
        self.table_layout.width = self.required_width

        # Add headers
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

        # If no data, return after adding headers
        if not self.filtered_data:
            # Add empty cells to maintain table structure
            for _ in range(len(self.headers)):
                self.table_layout.add_widget(MDLabel(
                    text="",
                    halign='center',
                    valign='middle',
                    size_hint_y=None,
                    height=40,
                    size_hint_x=None,
                    width=self.column_widths.get(self.headers[_], 100),
                ))
            return

        # Add data rows
        for item in self.filtered_data:
            for header in self.headers:
                width = self.column_widths.get(header, 100)
                if header == 'Action':
                    action_layout = MDBoxLayout(orientation='horizontal', spacing=5, size_hint_y=None, height=40)
                    
                    # Add action buttons based on table type
                    if self.headers == ['Class ID', 'Class Name', 'Action']:
                        class_id = item.get('id', '')
                        edit_button = MDRaisedButton(
                            text="Edit",
                            size_hint=(None, None),
                            size=(60, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, cid=class_id: self.edit_class(cid)
                        )
                        view_button = MDRaisedButton(
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
                        action_layout.add_widget(view_button)
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
                    elif self.headers == ['Subject ID', 'Subject Name', 'Total Teachers', 'Action']:
                        subject_id = item.get('subjectid', '')
                        edit_button = MDRaisedButton(
                            text="Edit",
                            size_hint=(None, None),
                            size=(60, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, sid=subject_id: self.edit_subject(sid)
                        )
                        view_button = MDRaisedButton(
                            text="View Teachers",
                            size_hint=(None, None),
                            size=(120, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, sid=subject_id: self.view_teachers_of_subject(sid)
                        )
                        delete_button = MDRaisedButton(
                            text="Delete",
                            size_hint=(None, None),
                            size=(60, 40),
                            pos_hint={'center_y': 0.5},
                            on_release=lambda instance, sid=subject_id: self.delete_item(sid, 'subject')
                        )
                        action_layout.add_widget(edit_button)
                        action_layout.add_widget(view_button)
                        action_layout.add_widget(delete_button)
                    
                    self.table_layout.add_widget(action_layout)
                else:
                    actual_key = self.column_map.get(header, header.lower())
                    text = str(item.get(actual_key, ''))
                    self.table_layout.add_widget(MDLabel(
                        text=text,
                        halign='center',
                        valign='middle',
                        size_hint_y=None,
                        height=40,
                        size_hint_x=None,
                        width=width,
                        text_size=(width, None),
                    ))

    def view_teachers_of_subject(self, subject_id):
        teachers_data = get_teachers_by_subject(subject_id)
        if not teachers_data:
            toast(f"No teachers found for subject ID {subject_id}.")
            return

        # Store the subject ID for later use
        self.viewing_subject_id = subject_id

        content = PaginatedTableView(
            full_data=teachers_data,
            headers=['ID', 'Code', 'Name', 'Email', 'Action'],
            column_map={
                'ID': 'TeacherID',
                'Code': 'TeacherCode',
                'Name': 'TeacherName',
                'Email': 'Email'
            },
            search_fields=['name', 'code'],
            column_widths={
                'ID': 60,
                'Code': 100,
                'Name': 200,
                'Email': 250,
                'Action': 150
            },
            items_per_page=10,
            size_hint_y=None,
            height=Window.height * 0.7,
        )
        # Pass the subject ID to the content view
        content.viewing_subject_id = subject_id
        Clock.schedule_once(lambda dt: content.update_table(), 0)

        self.dialog = MDDialog(
            title=f"Teachers of Subject ID {subject_id}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Close", on_release=self.close_dialog),
                MDRaisedButton(text="Add", on_release=lambda instance: content.add_teacher_to_subject(subject_id))
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
                MDRaisedButton(text="Add", on_release=lambda instance: content.add_student(cid))
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

    def add_student(self, class_id=None):
        classes = get_all_classes()
        if not classes:
            toast("Could not load classes.")
            return

        add_layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)

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

        # Only add class selection if not in a class-specific view
        if class_id is None:
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
            add_layout.add_widget(self.add_class_field)
            add_layout.height = 350
        else:
            self.selected_add_class_id = class_id
            add_layout.height = 300  # Adjust height without class field

        add_layout.add_widget(self.add_name_field)
        add_layout.add_widget(self.add_address_field)
        add_layout.add_widget(self.add_birthdate_field)

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

        # Get the current class ID before updating
        student = next((item for item in self.full_data if item.get('code') == student_code), None)
        current_class_id = get_classID_by_name(student.get('classname', '')) if student else None

        success = ad_update_student_details(student_code, new_name, new_address, new_birthdate, new_class_id)
        if success:
            toast("Student updated successfully.")
            # If we're in a class-specific view
            if self.headers == ['ID', 'Code', 'Name', 'Birthday', 'Class', 'Address', 'Action']:
                # If student was moved to a different class
                if current_class_id != new_class_id:
                    # Refresh the current class view (student will be removed)
                    self.full_data = get_students_of_class(current_class_id)
                else:
                    # Refresh the current class view
                    self.full_data = get_students_of_class(new_class_id)
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
            # Always refresh with the current class's students
            self.full_data = get_students_of_class(new_class_id)
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

    def delete_item(self, code, item_type, class_id=None):
        if item_type == 'student':
            success = ad_delete_student(code)
            if success:
                toast("Student deleted successfully.")
                # Always refresh with the current class's students
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
                # If we're in a subject-specific view
                if hasattr(self, 'viewing_subject_id') and self.viewing_subject_id:
                    # Refresh the current subject's teachers
                    new_data = get_teachers_by_subject(self.viewing_subject_id)
                    if new_data:
                        self.full_data = new_data
                        self.filtered_data = self.full_data
                    else:
                        # If no teachers left, set empty lists
                        self.full_data = []
                        self.filtered_data = []
                else:
                    # Refresh all teachers
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
            # Get all teachers associated with the subject
            teachers = get_teachers_by_subject(code)
            if teachers:
                for teacher in teachers:
                    teacher_code = teacher.get('TeacherCode', '')
                    ad_delete_teacher(teacher_code)  # Delete each teacher
            # Now delete the subject
            success, message = ad_delete_subject(code)
            if success:
                toast("Subject and associated teachers deleted successfully.")
                self.full_data = get_all_subjects()
                self.filtered_data = self.full_data
                self.update_table()
            else:
                toast(message)

    def close_dialog(self, instance):
        if self.dialog:
            self.dialog.dismiss()

    def close_edit_dialog(self, instance):
        if self.edit_dialog:
            self.edit_dialog.dismiss()

    def close_add_dialog(self, instance):
        if self.add_dialog:
            self.add_dialog.dismiss()

    def add_teacher_to_subject(self, subject_id):
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

        add_layout.add_widget(self.add_teacher_name_field)
        add_layout.add_widget(self.add_email_field)

        self.add_dialog = MDDialog(
            title="Add New Teacher",
            type="custom",
            content_cls=add_layout,
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda instance: self.save_new_teacher_to_subject(subject_id)
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_add_dialog
                )
            ]
        )
        self.add_dialog.open()

    def save_new_teacher_to_subject(self, subject_id):
        new_name = self.add_teacher_name_field.text.strip()
        new_email = self.add_email_field.text.strip()

        if not new_name or not new_email:
            toast("All fields are required.")
            return

        import re
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", new_email):
            toast("Invalid email format.")
            return

        success = ad_add_teacher(new_name, subject_id, new_email)
        if success:
            toast("Teacher added successfully.")
            # If we're in a subject-specific view
            if self.headers == ['ID', 'Code', 'Name', 'Email', 'Action']:
                # Refresh the current subject's teachers
                self.full_data = get_teachers_by_subject(subject_id)
                self.filtered_data = self.full_data
                self.update_table()
        else:
            toast("Failed to add teacher.")

        self.close_add_dialog(None)

    def edit_class(self, class_id):
        # Get class data from the filtered_data
        class_data = next((item for item in self.filtered_data if item['id'] == class_id), None)
        if not class_data:
            return

        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=150,
            padding=20
        )

        class_name_field = MDTextField(
            text=class_data['classname'],
            hint_text="Class Name",
            helper_text="Enter class name",
            helper_text_mode="on_error",
        )

        content.add_widget(class_name_field)

        self.edit_dialog = MDDialog(
            title=f"Edit Class {class_data['classname']}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_edit_dialog
                ),
                MDRaisedButton(
                    text="Save",
                    on_release=lambda x: self.save_class_changes(class_id, class_name_field.text)
                ),
            ],
        )
        self.edit_dialog.open()

    def save_class_changes(self, class_id, new_name):
        # Update class name in database
        success = self.update_class_name(class_id, new_name)
        if success:
            toast("Class updated successfully")
            # Refresh the table data
            self.full_data = get_all_classes()
            self.close_edit_dialog(None)
        else:
            toast("Failed to update class")

    def update_class_name(self, class_id, new_name):
        connection = connect_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = "UPDATE Classes SET ClassName = %s WHERE ClassID = %s"
                cursor.execute(query, (new_name, class_id))
                connection.commit()
                return True
            except Exception as e:
                print(f"Failed to update class name: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        return False

    def edit_subject(self, subject_id):
        # Get subject data from the filtered_data
        subject_data = next((item for item in self.filtered_data if item['subjectid'] == subject_id), None)
        if not subject_data:
            return

        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=150,
            padding=20
        )

        subject_name_field = MDTextField(
            text=subject_data['subjectname'],
            hint_text="Subject Name",
            helper_text="Enter subject name",
            helper_text_mode="on_error",
        )

        content.add_widget(subject_name_field)

        self.edit_dialog = MDDialog(
            title=f"Edit Subject {subject_data['subjectname']}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_edit_dialog
                ),
                MDRaisedButton(
                    text="Save",
                    on_release=lambda x: self.save_subject_changes(subject_id, subject_name_field.text)
                ),
            ],
        )
        self.edit_dialog.open()

    def save_subject_changes(self, subject_id, new_name):
        # Update subject name in database
        success = self.update_subject_name(subject_id, new_name)
        if success:
            toast("Subject updated successfully")
            # Refresh the table data
            self.full_data = get_all_subjects()
            self.close_edit_dialog(None)
        else:
            toast("Failed to update subject")

    def update_subject_name(self, subject_id, new_name):
        connection = connect_db()
        if connection:
            try:
                cursor = connection.cursor()
                query = "UPDATE Subjects SET SubjectName = %s WHERE SubjectID = %s"
                cursor.execute(query, (new_name, subject_id))
                connection.commit()
                return True
            except Exception as e:
                print(f"Failed to update subject name: {e}")
                return False
            finally:
                cursor.close()
                connection.close()
        return False 