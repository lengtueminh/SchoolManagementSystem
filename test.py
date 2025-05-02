import mysql.connector
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivy.core.window import Window
from kivy.metrics import dp

Window.size = (900, 600)

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"

        screen = MDScreen()
        screen.md_bg_color = (240 / 255, 240 / 255, 255 / 255, 1)

        layout = MDBoxLayout(orientation='vertical',
                             spacing=25,
                             padding=[250, 80, 250, 80],
                             size_hint=(1, None),
                             height=700)

        title_label = MDLabel(
            text="Login to the System",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=dp(60)
        )

        self.username = MDTextField(
            hint_text="Username",
            helper_text="Enter your username",
            helper_text_mode="on_focus",
            icon_right="account",
            size_hint_x=1
        )

        self.password = MDTextField(
            hint_text="Password",
            password=True,
            helper_text="Enter your password",
            helper_text_mode="on_focus",
            size_hint_x=0.9
        )

        self.toggle_button = MDIconButton(
            icon="eye-off",
            on_release=self.toggle_password
        )

        password_box = MDBoxLayout(orientation='horizontal')
        password_box.add_widget(self.password)
        password_box.add_widget(self.toggle_button)

        self.role_field = MDTextField(
            hint_text="Select Role",
            readonly=True,
            size_hint_x=1,
            icon_right="account-circle"
        )

        role_items = [
            {"text": "Admin", "on_release": lambda x="Admin": self.set_role(x)},
            {"text": "Student", "on_release": lambda x="Student": self.set_role(x)},
            {"text": "Teacher", "on_release": lambda x="Teacher": self.set_role(x)},
        ]

        self.role_menu = MDDropdownMenu(
            caller=self.role_field,
            items=role_items,
            width_mult=4
        )

        self.role_field.bind(on_touch_down=self.open_menu_touch)

        login_button = MDRaisedButton(
            text="Login",
            pos_hint={"center_x": 0.5},
            on_release=self.login,
            md_bg_color=self.theme_cls.primary_color,
            size_hint=(None, None),
            size=(200, 50),
            elevation=3
        )

        layout.add_widget(title_label)
        layout.add_widget(self.username)
        layout.add_widget(password_box)
        layout.add_widget(self.role_field)
        layout.add_widget(login_button)

        screen.add_widget(layout)
        return screen

    def toggle_password(self, instance):
        self.password.password = not self.password.password
        self.toggle_button.icon = "eye" if not self.password.password else "eye-off"

    def open_menu_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.role_menu.open()
        return False

    def set_role(self, role):
        self.role_field.text = role
        self.role_menu.dismiss()

    def login(self, instance):
        user = self.username.text
        pw = self.password.text
        role = self.role_field.text

        if not user or not pw or not role:
            print("Please fill all fields!")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="thuhangtran128",     # đổi thành mật khẩu thật
                database="SchoolManagementSystem"          # đổi thành tên database thật
            )
            cursor = conn.cursor()

            query = "SELECT * FROM Users WHERE Username=%s AND Password=%s AND UserType=%s"
            cursor.execute(query, (user, pw, role))
            result = cursor.fetchone()

            if result:
                print(f"Login successful as {role}")
            else:
                print("Login failed. Wrong username, password or role!")

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            print("Database error:", err)

MainApp().run()