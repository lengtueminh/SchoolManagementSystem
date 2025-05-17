from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.toast import toast
from utils.db_utils import get_all_classes
from screens.admin.components.paginated_table import PaginatedTableView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard

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
            md_bg_color=[0.2, 0.8, 0.2, 1],  # Green color
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
            content = PaginatedTableView(
                full_data=classes_data,
                headers=['Class ID', 'Class Name', 'Action'],
                column_map={
                    'Class ID': 'id',
                    'Class Name': 'classname'
                },
                search_fields=['classname'],
                column_widths={
                    'Class ID': 100,
                    'Class Name': 300,
                    'Action': 250
                },
                items_per_page=10,
                size_hint=(1, 1),
                md_bg_color=[1, 1, 1, 1]
            )
            Clock.schedule_once(lambda dt: content.update_table(), 0)
            
            # Bind add button
            add_button.bind(on_release=lambda x: content.add_class())
            
            content_card.add_widget(content)
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
            
    def go_back(self, instance):
        self.manager.current = "admin_homescreen" 