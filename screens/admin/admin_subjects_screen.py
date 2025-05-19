from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.toast import toast
from utils.db_utils import get_all_subjects
from screens.admin.components.paginated_table import PaginatedTableView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from functools import partial
from screens.admin.admin_teachers_screen import AdminTeachersScreen

class AdminSubjectsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin_subjects_screen"
        
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
            text="Subjects Management",
            font_style="H5",
            bold=True,
            pos_hint={"center_y": 0.5}
        )
        
        # Add button
        add_button = MDRaisedButton(
            text="Add Subject",
            md_bg_color=[0.8, 0.4, 0.2, 1],  # Orange color
            pos_hint={"center_y": 0.5}
        )
        
        header_card.add_widget(back_button)
        header_card.add_widget(title)
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
        subjects_data = get_all_subjects()
        if subjects_data:
            self.content = PaginatedTableView(
                full_data=subjects_data,
                headers=['Subject ID', 'Subject Name', 'Total Teachers', 'Action'],
                column_map={
                    'Subject ID': 'subjectid',
                    'Subject Name': 'subjectname',
                    'Total Teachers': 'total_teachers'
                },
                search_fields=['subjectname'],
                column_widths={
                    'Subject ID': 80,
                    'Subject Name': 200,
                    'Total Teachers': 120,
                    'Action': 300
                },
                items_per_page=10,
                size_hint=(1, 1),
                md_bg_color=[1, 1, 1, 1],
                show_edit=True,
                show_delete=True,
                show_view=True,
                edit_callback=self.edit_subject,
                delete_callback=self.delete_subject,
                view_callback=self.view_teachers
            )
            Clock.schedule_once(lambda dt: self.content.update_table(), 0)
            
            # Bind add button
            add_button.bind(on_release=lambda x: self.content.add_subject())
            
            content_card.add_widget(self.content)
        else:
            # Show message when no data
            no_data_label = MDLabel(
                text="No subjects found",
                halign="center",
                theme_text_color="Secondary"
            )
            content_card.add_widget(no_data_label)
            
        main_layout.add_widget(content_card)
        self.add_widget(main_layout)
            
    def go_back(self, instance):
        self.manager.current = "admin_homescreen"

    def edit_subject(self, row):
        subject_id = row['subjectid']
        old_name = row['subjectname']
        content = MDBoxLayout(orientation='vertical', spacing=16, padding=16, size_hint_y=None)
        content.height = 120
        name_label = MDLabel(text="Subject Name", halign="left", size_hint_y=None, height=24)
        name_field = MDTextField(
            text=old_name,
            size_hint_y=None,
            height=40
        )
        content.add_widget(name_label)
        content.add_widget(name_field)
        self.edit_subject_dialog = MDDialog(
            title=f"Edit Subject {subject_id}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.edit_subject_dialog.dismiss()),
                MDRaisedButton(
                    text="Save",
                    on_release=lambda x: self.save_subject_edit(
                        subject_id,
                        name_field.text
                    )
                )
            ]
        )
        self.edit_subject_dialog.open()

    def save_subject_edit(self, subject_id, new_name):
        from utils.db_utils import ad_update_subject, get_all_subjects
        if not new_name:
            toast("Subject name is required.")
            return
        success = ad_update_subject(subject_id, new_name)
        if success:
            toast("Subject updated successfully!")
            subjects = get_all_subjects()
            self.content.full_data = subjects
            self.content.filtered_data = subjects
            self.content.update_table()
        else:
            toast("Failed to update subject.")
        self.edit_subject_dialog.dismiss()

    def view_teachers(self, row):
        subject_id = row['subjectid']
        from utils.db_utils import get_teachers_by_subject, get_all_subjects
        teachers = get_teachers_by_subject(subject_id)
        
        content = PaginatedTableView(
            full_data=teachers if teachers else [],
            headers=['ID', 'Code', 'Name', 'Email', 'Action'],
            column_map={
                'ID': 'id',
                'Code': 'code',
                'Name': 'name',
                'Email': 'email'
            },
            search_fields=['name', 'code', 'email'],
            column_widths={
                'ID': 60,
                'Code': 100,
                'Name': 200,
                'Email': 250,
                'Action': 200
            },
            items_per_page=10,
            size_hint_y=None,
            height=400,
            show_edit=True,
            show_delete=True,
            edit_callback=self.edit_teacher_in_subject,
            delete_callback=self.delete_teacher_in_subject
        )
        Clock.schedule_once(lambda dt: content.update_table(), 0)

        def update_main_screen():
            # Update the main screen's data
            subjects_data = get_all_subjects()
            self.content.full_data = subjects_data
            self.content.filtered_data = subjects_data
            self.content.update_table()

        self.dialog = MDDialog(
            title=f"Teachers for Subject {row['subjectname']}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Close", on_release=self.close_dialog),
                MDRaisedButton(text="Add Teacher", on_release=lambda instance: content.add_teacher_to_subject(subject_id, update_main_screen))
            ]
        )
        # Store the subject_id in the dialog for later use
        self.dialog.subject_id = subject_id
        self.dialog.open()

    def edit_teacher_in_subject(self, row):
        # Tái sử dụng logic edit_teacher từ admin_teachers_screen.py
        def update_teachers_in_dialog():
            from utils.db_utils import get_teachers_by_subject
            subject_id = row['subjectid'] if 'subjectid' in row else None
            if subject_id:
                teachers = get_teachers_by_subject(subject_id)
                self.dialog.content_cls.full_data = teachers
                self.dialog.content_cls.filtered_data = teachers
                self.dialog.content_cls.update_table()
        # Tạo instance tạm để dùng hàm edit_teacher
        admin_teachers_screen = AdminTeachersScreen()
        admin_teachers_screen.edit_teacher(row, update_callback=update_teachers_in_dialog)

    def delete_teacher_in_subject(self, row):
        teacher_code = row['code']
        teacher_name = row['name']
        self.delete_teacher_dialog = MDDialog(
            title="Confirm Delete",
            text=f"Are you sure you want to delete teacher '{teacher_name}' from this subject?",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.delete_teacher_dialog.dismiss()),
                MDRaisedButton(
                    text="Delete",
                    md_bg_color=(1,0,0,1),
                    on_release=lambda x: self.confirm_delete_teacher_in_subject(teacher_code)
                )
            ]
        )
        self.delete_teacher_dialog.open()

    def confirm_delete_teacher_in_subject(self, teacher_code):
        from utils.db_utils import ad_delete_teacher, get_teachers_by_subject, get_all_subjects
        success = ad_delete_teacher(teacher_code)
        if success:
            toast("Teacher deleted successfully!")
            # Cập nhật lại danh sách giáo viên trong dialog
            if hasattr(self, 'dialog') and self.dialog:
                # Use the stored subject_id instead of trying to get it from the data
                subject_id = self.dialog.subject_id
                if subject_id:
                    teachers = get_teachers_by_subject(subject_id)
                    self.dialog.content_cls.full_data = teachers
                    self.dialog.content_cls.filtered_data = teachers
                    self.dialog.content_cls.update_table()
                    
                    # Cập nhật lại dữ liệu ở màn hình chính
                    subjects_data = get_all_subjects()
                    self.content.full_data = subjects_data
                    self.content.filtered_data = subjects_data
                    self.content.update_table()
        else:
            toast("Failed to delete teacher.")
        self.delete_teacher_dialog.dismiss()

    def delete_subject(self, row):
        subject_id = row['subjectid']
        subject_name = row['subjectname']
        self.delete_subject_dialog = MDDialog(
            title="Confirm Delete",
            text=f"Are you sure you want to delete subject '{subject_name}' and all related teachers (except grades)?",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.delete_subject_dialog.dismiss()),
                MDRaisedButton(
                    text="Delete",
                    md_bg_color=(1,0,0,1),
                    on_release=lambda x: self.confirm_delete_subject(subject_id)
                )
            ]
        )
        self.delete_subject_dialog.open()

    def confirm_delete_subject(self, subject_id):
        from utils.db_utils import ad_delete_subject, get_all_subjects
        success, message = ad_delete_subject(subject_id)
        if success:
            toast("Subject and associated teachers deleted successfully!")
            subjects = get_all_subjects()
            self.content.full_data = subjects
            self.content.filtered_data = subjects
            self.content.update_table()
        else:
            toast(message)
        self.delete_subject_dialog.dismiss()

    def close_dialog(self, instance):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss() 