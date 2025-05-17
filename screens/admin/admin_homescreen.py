from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard

class AdminHomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin_homescreen"

    def on_enter(self):
        self.clear_widgets()

        # Main container with padding
        main_layout = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            padding=[20, 10, 20, 10],
            size_hint=(1, None),
            height=300,
            pos_hint={"top": 0.98},
            md_bg_color=[0.95, 0.95, 0.95, 1]  # Light gray background
        )

        # Top card with admin info
        info_card = MDCard(
            orientation="vertical",
            size_hint=(1, None),
            height=140,
            padding=[20, 15, 20, 15],
            elevation=2,
            md_bg_color=[1, 1, 1, 1],  # White background
            radius=[10, 10, 10, 10]  # Rounded corners
        )

        # Admin info section
        welcome_label = MDLabel(
            text="Welcome, Admin!",
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height=40
        )

        info_grid = MDBoxLayout(
            orientation="vertical",
            spacing=5,
            size_hint_y=None,
            height=60,
            padding=[0, 0, 0, 0]
        )

        info_grid.add_widget(MDLabel(
            text="School Management System",
            theme_text_color="Secondary",
            font_style="Subtitle1"
        ))
        info_grid.add_widget(MDLabel(
            text="Administrator Access",
            theme_text_color="Secondary",
            font_style="Subtitle1"
        ))

        info_card.add_widget(welcome_label)
        info_card.add_widget(info_grid)

        # Action buttons card
        buttons_card = MDCard(
            orientation="horizontal",
            size_hint=(1, None),
            height=60,
            padding=[10, 5, 10, 5],
            spacing=10,
            elevation=2,
            md_bg_color=[1, 1, 1, 1],
            radius=[10, 10, 10, 10]  # Rounded corners
        )

        # Create action buttons with icons
        buttons = [
            {
                "text": "Teachers",
                "icon": "account-tie",
                "callback": self.show_teachers_screen,
                "color": [0.2, 0.6, 0.8, 1]  # Blue
            },
            {
                "text": "Classes",
                "icon": "google-classroom",
                "callback": self.show_classes_screen,
                "color": [0.2, 0.8, 0.2, 1]  # Green
            },
            {
                "text": "Subjects",
                "icon": "book-open-variant",
                "callback": self.show_subjects_screen,
                "color": [0.8, 0.4, 0.2, 1]  # Orange
            },
            {
                "text": "Log out",
                "icon": "logout",
                "callback": self.logout,
                "color": [0.8, 0.2, 0.2, 1]  # Red
            }
        ]

        for btn in buttons:
            button = MDRaisedButton(
                text=btn["text"],
                icon=btn["icon"],
                size_hint=(1, None),
                height=50,
                md_bg_color=btn["color"],
                on_release=btn["callback"]
            )
            buttons_card.add_widget(button)

        # Add all sections to main layout
        main_layout.add_widget(info_card)
        main_layout.add_widget(buttons_card)

        self.add_widget(main_layout)

    def logout(self, instance):
        app = MDApp.get_running_app()
        app.username = None
        app.role = None
        self.manager.current = "login_screen"

    def show_teachers_screen(self, instance):
        self.manager.current = "admin_teachers_screen"

    def show_classes_screen(self, instance):
        self.manager.current = "admin_classes_screen"

    def show_subjects_screen(self, instance):
        self.manager.current = "admin_subjects_screen"




