from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.toast import toast
from utils.db_utils import get_all_teachers, get_all_subjects, get_teachers_by_subject
from screens.admin.components.paginated_table import PaginatedTableView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from functools import partial
from kivymd.uix.gridlayout import MDGridLayout

class AdminTeachersScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin_teachers_screen"
        
    def on_enter(self):
        self.clear_widgets()
        
        # Main layout
        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=[16, 16, 16, 16],
            md_bg_color=[0.95, 0.95, 0.95, 1]  # Light gray background
        )
        
        # Header card
        header_card = MDCard(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            padding=[16, 0, 16, 0],
            spacing=20,
            elevation=2,
            radius=[15, 15, 15, 15]
        )
        
        # Back button
        back_button = MDIconButton(
            icon="arrow-left",
            on_release=self.go_back,
            pos_hint={"center_y": 0.5}
        )
        
        # Title
        title = MDLabel(
            text="Teachers Management",
            font_style="H5",
            bold=True,
            pos_hint={"center_y": 0.5}
        )
        
        # Filter button
        self.filter_button = MDRaisedButton(
            text="Filter by Subject",
            md_bg_color=[0.2, 0.6, 0.8, 1],
            pos_hint={"center_y": 0.5}
        )
        self.filter_button.bind(on_release=self.show_filter_menu)
        
        # Add button
        add_button = MDRaisedButton(
            text="Add Teacher",
            md_bg_color=[0.2, 0.6, 0.8, 1],
            pos_hint={"center_y": 0.5}
        )
        
        header_card.add_widget(back_button)
        header_card.add_widget(title)
        header_card.add_widget(self.filter_button)
        header_card.add_widget(add_button)
        
        main_layout.add_widget(header_card)
        
        # Content card
        content_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=Window.height * 0.8,
            padding=[16, 16, 16, 16],
            spacing=10,
            elevation=2,
            radius=[15, 15, 15, 15],
            pos_hint={"center_x": 0.5}
        )
        
        # Table content
        teachers_data = get_all_teachers()
        if teachers_data:
            self.content = PaginatedTableView(
                full_data=teachers_data,
                headers=['ID', 'Code', 'Name', 'Subject', 'Email', 'Action'],
                column_map={
                    'ID': 'id',
                    'Code': 'code',
                    'Name': 'name',
                    'Subject': 'subjectname',
                    'Email': 'email'
                },
                search_fields=['name', 'code', 'subjectname', 'email'],
                column_widths={
                    'ID': 60,
                    'Code': 120,
                    'Name': 200,
                    'Subject': 150,
                    'Email': 250,
                    'Action': 200
                },
                items_per_page=10,
                size_hint=(1, 1),
                md_bg_color=[1, 1, 1, 1],
                show_edit=True,
                show_delete=True,
                edit_callback=self.edit_teacher,
                delete_callback=self.delete_teacher
            )
            Clock.schedule_once(lambda dt: self.content.update_table(), 0)
            
            # Bind add button
            add_button.bind(on_release=lambda x: self.content.add_teacher())
            
            content_card.add_widget(self.content)
        else:
            # Show message when no data
            no_data_label = MDLabel(
                text="No teachers found",
                halign="center",
                theme_text_color="Secondary"
            )
            content_card.add_widget(no_data_label)
            
        main_layout.add_widget(content_card)
        self.add_widget(main_layout)

    def show_filter_menu(self, instance):
        subjects = get_all_subjects()
        menu_items = [
            {
                "text": "All Subjects",
                "on_release": lambda: self.filter_teachers(None)
            }
        ]
        for subject in subjects:
            menu_items.append({
                "text": subject["subjectname"],
                "on_release": lambda sid=subject["subjectid"]: self.filter_teachers(sid)
            })
        
        self.menu = MDDropdownMenu(
            caller=instance,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def filter_teachers(self, subject_id):
        if subject_id is None:
            teachers_data = get_all_teachers()
        else:
            teachers_data = get_teachers_by_subject(subject_id)
        
        if hasattr(self, 'content'):
            self.content.full_data = teachers_data
            self.content.filtered_data = teachers_data
            self.content.show_edit = True
            self.content.show_delete = True
            self.content.edit_callback = self.edit_teacher
            self.content.delete_callback = self.delete_teacher
            self.content.update_table()
        
        if self.menu:
            self.menu.dismiss()

    def edit_teacher(self, row, update_callback=None):
        teacher_code = row['code']
        old_name = row['name']
        old_email = row['email']
        old_subject = row['subjectname']
        subjects = get_all_subjects()
        content = MDGridLayout(cols=1, spacing=18, padding=[24, 24, 24, 8], size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        # Name
        name_label = MDLabel(text="Name", halign="left", size_hint_y=None, height=28)
        name_field = MDTextField(
            text=old_name,
            size_hint_y=None,
            height=44
        )
        # Email
        email_label = MDLabel(text="Email", halign="left", size_hint_y=None, height=28)
        email_field = MDTextField(
            text=old_email,
            size_hint_y=None,
            height=44
        )
        # Subject
        subject_label = MDLabel(text="Subject", halign="left", size_hint_y=None, height=28)
        subject_field = MDTextField(
            text=old_subject,
            size_hint_y=None,
            height=44,
            readonly=True
        )
        # Dropdown menu for subject
        menu_items = []
        for subject in subjects:
            menu_items.append({
                "text": subject['subjectname'],
                "on_release": partial(self.set_subject_for_teacher, subject_field, subject['subjectid'], subject['subjectname'])
            })
        self.subject_menu = MDDropdownMenu(
            caller=subject_field,
            items=menu_items,
            width_mult=4,
        )
        subject_field.bind(on_touch_down=lambda instance, touch: self.subject_menu.open() if instance.collide_point(*touch.pos) and touch.button == 'left' else None)
        self.selected_subject_id = None
        for subject in subjects:
            if subject['subjectname'] == old_subject:
                self.selected_subject_id = subject['subjectid']
                break
        content.add_widget(name_label)
        content.add_widget(name_field)
        content.add_widget(email_label)
        content.add_widget(email_field)
        content.add_widget(subject_label)
        content.add_widget(subject_field)
        self.edit_teacher_dialog = MDDialog(
            title=f"Edit Teacher {teacher_code}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.edit_teacher_dialog.dismiss()),
                MDRaisedButton(
                    text="Save",
                    on_release=lambda x: self.save_teacher_edit(
                        teacher_code,
                        name_field.text,
                        email_field.text,
                        self.selected_subject_id,
                        update_callback
                    )
                )
            ]
        )
        self.edit_teacher_dialog.open()

    def set_subject_for_teacher(self, subject_field, subject_id, subject_name, *args):
        subject_field.text = subject_name
        self.selected_subject_id = subject_id
        if hasattr(self, 'subject_menu'):
            self.subject_menu.dismiss()

    def save_teacher_edit(self, teacher_code, new_name, new_email, new_subject_id, update_callback=None):
        from utils.db_utils import ad_update_teacher_details, get_all_teachers
        if not (new_name and new_email and new_subject_id):
            toast("All fields are required.")
            return
        import re
        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", new_email):
            toast("Invalid email format.")
            return
        success = ad_update_teacher_details(teacher_code, new_name, new_subject_id, new_email)
        if success:
            toast("Teacher updated successfully!")
            if update_callback:
                update_callback()
            else:
                teachers = get_all_teachers()
                self.content.full_data = teachers
                self.content.filtered_data = teachers
                self.content.update_table()
        else:
            toast("Failed to update teacher.")
        self.edit_teacher_dialog.dismiss()

    def delete_teacher(self, row):
        teacher_code = row['code']
        teacher_name = row['name']
        self.delete_teacher_dialog = MDDialog(
            title="Confirm Delete",
            text=f"Are you sure you want to delete teacher '{teacher_name}' and all related info (except grades)?",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.delete_teacher_dialog.dismiss()),
                MDRaisedButton(
                    text="Delete",
                    md_bg_color=(1,0,0,1),
                    on_release=lambda x: self.confirm_delete_teacher(teacher_code)
                )
            ]
        )
        self.delete_teacher_dialog.open()

    def confirm_delete_teacher(self, teacher_code):
        from utils.db_utils import ad_delete_teacher, get_all_teachers
        success = ad_delete_teacher(teacher_code)
        if success:
            toast("Teacher deleted successfully!")
            teachers = get_all_teachers()
            self.content.full_data = teachers
            self.content.filtered_data = teachers
            self.content.update_table()
        else:
            toast("Failed to delete teacher.")
        self.delete_teacher_dialog.dismiss()

    def go_back(self, instance):
        self.manager.current = "admin_homescreen" 