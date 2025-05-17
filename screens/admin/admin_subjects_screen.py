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
            content = PaginatedTableView(
                full_data=subjects_data,
                headers=['Subject ID', 'Subject Name', 'Total Teachers', 'Action'],
                column_map={
                    'Subject ID': 'subjectid',
                    'Subject Name': 'subjectname',
                    'Total Teachers': 'total_teachers'
                },
                search_fields=['subjectname'],
                column_widths={
                    'Subject ID': 100,
                    'Subject Name': 300,
                    'Total Teachers': 150,
                    'Action': 250
                },
                items_per_page=10,
                size_hint=(1, 1),
                md_bg_color=[1, 1, 1, 1]
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)
            
            # Bind add button
            add_button.bind(on_release=lambda x: content.add_subject())
            
            content_card.add_widget(content)
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