from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.toast import toast
from utils.db_utils import get_all_classes, get_students_of_class
from screens.admin.components.paginated_table import PaginatedTableView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from functools import partial
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.scrollview import ScrollView

class AdminClassesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin_classes_screen"
        
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
            text="Classes Management",
            font_style="H5",
            bold=True,
            pos_hint={"center_y": 0.5}
        )
        
        # Add button
        add_button = MDRaisedButton(
            text="Add Class",
            md_bg_color=[0.2, 0.6, 0.8, 1],
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
        classes_data = get_all_classes()
        if classes_data:
            self.content = PaginatedTableView(
                full_data=classes_data,
                headers=['ID', 'Class Name', 'Total Students', 'Action'],
                column_map={
                    'ID': 'id',
                    'Class Name': 'classname',
                    'Total Students': 'total_students'
                },
                search_fields=['classname'],
                column_widths={
                    'ID': 60,
                    'Class Name': 200,
                    'Total Students': 150,
                    'Action': 300
                },
                items_per_page=10,
                size_hint=(1, 1),
                md_bg_color=[1, 1, 1, 1],
                show_edit=True,
                show_delete=True,
                show_view=True,
                edit_callback=self.edit_class,
                delete_callback=self.delete_class,
                view_callback=self.view_students
            )
            Clock.schedule_once(lambda dt: self.content.update_table(), 0)
            
            # Bind add button
            add_button.bind(on_release=lambda x: self.content.add_class())
            
            content_card.add_widget(self.content)
        else:
            # Show message when no data
            no_data_label = MDLabel(
                text="No classes found",
                halign="center",
                theme_text_color="Secondary"
            )
            content_card.add_widget(no_data_label)
            
        main_layout.add_widget(content_card)
        self.add_widget(main_layout)

    def edit_class(self, row):
        class_id = row['id']
        old_name = row['classname']
        content = MDBoxLayout(orientation='vertical', spacing=10, padding=10)
        name_field = MDTextField(
            hint_text='Class Name',
            text=old_name,
            size_hint_y=None,
            height=40
        )
        content.add_widget(name_field)
        self.edit_dialog = MDDialog(
            title=f"Edit Class {old_name}",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Cancel", on_release=self.close_edit_dialog),
                MDRaisedButton(text="Save", on_release=lambda x: self.save_class_name(class_id, name_field.text))
            ]
        )
        self.edit_dialog.open()

    def save_class_name(self, class_id, new_name):
        from utils.db_utils import connect_db, get_all_classes
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE Classes SET ClassName = %s WHERE ClassID = %s", (new_name, class_id))
                conn.commit()
                toast("Class name updated successfully!")
                self.full_data = get_all_classes()
                self.content.full_data = self.full_data
                self.content.filtered_data = self.full_data
                self.content.update_table()
            except Exception as e:
                toast(f"Failed to update class: {e}")
            finally:
                cursor.close()
                conn.close()
        self.close_edit_dialog(None)

    def close_edit_dialog(self, instance):
        if hasattr(self, 'edit_dialog') and self.edit_dialog:
            self.edit_dialog.dismiss()

    def delete_class(self, row):
        class_id = row['id']
        class_name = row['classname']
        self.delete_dialog = MDDialog(
            title="Confirm Delete",
            text=f"Are you sure you want to delete class '{class_name}' and all its students?",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.delete_dialog.dismiss()),
                MDRaisedButton(text="Delete", md_bg_color=(1,0,0,1), on_release=lambda x: self.confirm_delete_class(class_id))
            ]
        )
        self.delete_dialog.open()

    def confirm_delete_class(self, class_id):
        from utils.db_utils import ad_delete_class, get_all_classes
        success = ad_delete_class(class_id)
        if success:
            toast("Class and all its students deleted!")
            self.full_data = get_all_classes()
            self.content.full_data = self.full_data
            self.content.filtered_data = self.full_data
            self.content.update_table()
        else:
            toast("Failed to delete class!")
        if hasattr(self, 'delete_dialog') and self.delete_dialog:
            self.delete_dialog.dismiss()

    def view_students(self, row):
        class_id = row['id']
        students_data = get_students_of_class(class_id)
        if not students_data:
            toast(f"No students found in this class.")
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
                'Action': 200
            },
            items_per_page=10,
            size_hint_y=None,
            height=Window.height * 0.7,
            show_edit=True,
            show_delete=True,
            edit_callback=self.edit_student,
            delete_callback=self.delete_student
        )
        Clock.schedule_once(lambda dt: content.update_table(), 0)

        self.dialog = MDDialog(
            title=f"Students in Class",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="Close", on_release=self.close_dialog),
                MDRaisedButton(text="Add Student", on_release=lambda instance: content.add_student(class_id))
            ]
        )
        self.dialog.open()

    def edit_student(self, row):
        student_code = row['code']
        old_name = row['name']
        old_address = row['address']
        old_birthdate = row['birthdate']
        old_class = row['classname']
        class_id = row['id'] if 'id' in row else None
        classes = get_all_classes()
        content = MDGridLayout(cols=1, spacing=18, padding=[24, 24, 24, 8], size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        # Name
        name_label = MDLabel(text="Name", halign="left", size_hint_y=None, height=28)
        name_field = MDTextField(
            text=old_name,
            size_hint_y=None,
            height=44
        )
        # Address
        address_label = MDLabel(text="Address", halign="left", size_hint_y=None, height=28)
        address_field = MDTextField(
            text=old_address,
            size_hint_y=None,
            height=44
        )
        # Birthdate
        birthdate_label = MDLabel(text="Birthdate (YYYY-MM-DD)", halign="left", size_hint_y=None, height=28)
        birthdate_field = MDTextField(
            text=old_birthdate,
            size_hint_y=None,
            height=44
        )
        # Class
        class_label = MDLabel(text="Class", halign="left", size_hint_y=None, height=28)
        class_field = MDTextField(
            text=old_class,
            size_hint_y=None,
            height=44,
            readonly=True
        )
        # Dropdown menu for class
        menu_items = []
        for c in classes:
            menu_items.append({
                "text": c['classname'],
                "on_release": partial(self.set_class_for_student, class_field, c['id'], c['classname'])
            })
        self.class_menu = MDDropdownMenu(
            caller=class_field,
            items=menu_items,
            width_mult=4,
        )
        class_field.bind(on_touch_down=lambda instance, touch: self.class_menu.open() if instance.collide_point(*touch.pos) and touch.button == 'left' else None)
        self.selected_class_id = None
        for c in classes:
            if c['classname'] == old_class:
                self.selected_class_id = c['id']
                break
        content.add_widget(name_label)
        content.add_widget(name_field)
        content.add_widget(address_label)
        content.add_widget(address_field)
        content.add_widget(birthdate_label)
        content.add_widget(birthdate_field)
        content.add_widget(class_label)
        content.add_widget(class_field)
        scroll = ScrollView(size_hint=(1, None), size=(500, 400))
        scroll.add_widget(content)
        self.edit_student_dialog = MDDialog(
            title=f"Edit Student {student_code}",
            type="custom",
            content_cls=scroll,
            size_hint=(0.95, None),
            auto_dismiss=False,
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.edit_student_dialog.dismiss()),
                MDRaisedButton(
                    text="Save",
                    on_release=lambda x: self.save_student_edit(
                        student_code,
                        name_field.text,
                        address_field.text,
                        birthdate_field.text,
                        self.selected_class_id
                    )
                )
            ]
        )
        self.edit_student_dialog.open()

    def set_class_for_student(self, class_field, class_id, class_name, *args):
        class_field.text = class_name
        self.selected_class_id = class_id
        if hasattr(self, 'class_menu'):
            self.class_menu.dismiss()

    def save_student_edit(self, student_code, new_name, new_address, new_birthdate, class_id):
        from utils.db_utils import ad_update_student_details, get_students_of_class
        if not (new_name and new_address and new_birthdate):
            toast("All fields are required.")
            return
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", new_birthdate):
            toast("Birthdate must be in YYYY-MM-DD format.")
            return
        success = ad_update_student_details(student_code, new_name, new_address, new_birthdate, class_id)
        if success:
            toast("Student updated successfully!")
            if class_id:
                students = get_students_of_class(class_id)
                self.dialog.content_cls.full_data = students
                self.dialog.content_cls.filtered_data = students
                self.dialog.content_cls.update_table()
        else:
            toast("Failed to update student.")
        self.edit_student_dialog.dismiss()

    def delete_student(self, row):
        student_code = row['code']
        class_id = row['id'] if 'id' in row else None
        student_name = row['name']
        self.delete_student_dialog = MDDialog(
            title="Confirm Delete",
            text=f"Are you sure you want to delete student '{student_name}'?",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: self.delete_student_dialog.dismiss()),
                MDRaisedButton(
                    text="Delete",
                    md_bg_color=(1,0,0,1),
                    on_release=lambda x: self.confirm_delete_student(student_code, class_id)
                )
            ]
        )
        self.delete_student_dialog.open()

    def confirm_delete_student(self, student_code, class_id):
        from utils.db_utils import ad_delete_student, get_students_of_class
        success = ad_delete_student(student_code)
        if success:
            toast("Student deleted successfully!")
            if class_id:
                students = get_students_of_class(class_id)
                self.dialog.content_cls.full_data = students
                self.dialog.content_cls.filtered_data = students
                self.dialog.content_cls.update_table()
        else:
            toast("Failed to delete student.")
        self.delete_student_dialog.dismiss()

    def close_dialog(self, instance):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()
            
    def go_back(self, instance):
        self.manager.current = "admin_homescreen" 