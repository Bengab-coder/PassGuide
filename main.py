from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.list import TwoLineListItem
from kivy.clock import Clock

try:
    from kivymd.toast.androidtoast.androidtoast import toast
except:
    from kivymd.toast import toast
from kivy.properties import StringProperty
from security import Credentials
from kivy.animation import Animation
from kivymd.uix.label import MDLabel
from android.runnable import run_on_ui_thread
from jnius import autoclass

Color = autoclass("android.graphics.Color")
WindowManager = autoclass("android.view.WindowManager$LayoutParams")
activity = autoclass("org.kivy.android.PythonActivity").mActivity


class PassGuide(MDApp):
    account_name_label = StringProperty("Account Name")
    user_name_label = StringProperty("User Name")
    email_label = StringProperty("Email")
    password_label = StringProperty("Password")

    def __init__(self, **kwargs):
        super(PassGuide, self).__init__(**kwargs)
        self.statusbar("#3594D0")
        self.credentials = Credentials()
        self.master_passwd_set = self.credentials.check_for_master_passwd()
        self.label = MDLabel(text="No password has been added , click the + button to add one", halign="center",
                             pos_hint={"center_y": 0.5}, theme_text_color="Custom",
                             text_color=self.theme_cls.primary_color, font_style="H4")

    @run_on_ui_thread
    def statusbar(self, color):
        window = activity.getWindow()
        window.clearFlags(WindowManager.FLAG_TRANSLUCENT_STATUS)
        window.addFlags(WindowManager.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS)
        window.setStatusBarColor(Color.parseColor(color))
        window.setNavigationBarColor(Color.parseColor(color))

    def build(self):
        return Builder.load_file("design.kv")

    def on_start(self):
        if not self.master_passwd_set:
            self.root.ids.sm.current = 'set_master_passwd'
        else:
            self.root.ids.sm.current = 'enter_master_passwd'
        self.init_screen()

    def init_screen(self):
        all_credentials = self.credentials.get_credentials()
        if not all_credentials:
            self.root.ids.passwds_screen.add_widget(self.label)

        for credential in all_credentials:
            item = TwoLineListItem(text=credential[-1], secondary_text=credential[1], theme_text_color="Custom",
                                   text_color=self.theme_cls.primary_color, font_style="H6",
                                   on_release=self.display_credential_details)
            self.root.ids.passwds.add_widget(item)

    def add_passwd(self, sm, username, email, passwd, account_name):
        username = username.text.strip()
        email = email.text.strip()
        passwd = passwd.text.strip()
        account_name = account_name.text.strip()
        if len(passwd) > 0 and len(account_name) > 0:
            self.credentials.save_credentials(username, email, passwd, account_name)
            item = TwoLineListItem(text=account_name, secondary_text=username, theme_text_color="Custom",
                                   text_color=self.theme_cls.primary_color, font_style="H6",
                                   on_release=self.display_credential_details)

            if self.label in self.root.ids.passwds_screen.children:
                self.root.ids.passwds_screen.remove_widget(self.label)

            self.root.ids.passwds.add_widget(item)
            sm.current = "my_passwds"
            Clock.schedule_once(self.clear_textfields)
        else:
            toast("You must specify at least the Accont name and the password")

    def set_master_passwd(self, sm, passwd1):
        passwd = passwd1.text
        passwd1.text = ""
        if len(passwd) >= 5:
            self.credentials.set_master_passwd(passwd)
            toast("Master password set")
            sm.current = "enter_master_passwd"
        else:
            toast("Password is too short")

    def clear_textfields(self, dt):
        self.root.ids.user_name.text = ""
        self.root.ids.email.text = ""
        self.root.ids.passwd_new.text = ""
        self.root.ids.account_name.text = ""

    def go_back(self):
        self.root.ids.sm.current = "my_passwds"

    def authenticate(self, sm, passwd):
        passwd = passwd.text.strip()
        if passwd:
            if passwd == self.credentials.get_master_passwd():
                sm.current = "my_passwds"
            else:
                toast("Wrong password")

    def display_credential_details(self, instance):
        for cred in self.credentials.get_credentials():
            if cred[1] == instance.secondary_text and cred[-1] == instance.text:
                self.account_name_label = cred[-1]
                self.user_name_label = cred[1]
                self.email_label = cred[-2]
                self.password_label = cred[2]
                self.root.ids.sm.current = "view_credentials"
                break

    def delete_account(self, passwd_v, acct_name, user):
        if passwd_v.text == self.credentials.get_master_passwd():
            for child in self.root.ids.passwds.children:
                if child.text == acct_name and child.secondary_text == user:

                    id = self.credentials.get_id(child.text, child.secondary_text)
                    self.credentials.delete_credential(id)
                    self.root.ids.passwds.remove_widget(child)
                    if len(self.root.ids.passwds.children) == 0 and self.label not in self.root.ids.passwds_screen.children:
                        self.root.ids.passwds_screen.add_widget(self.label)

                    self.root.ids.sm.current = "my_passwds"
                    toast("Account deleted")
                    break
        else:
            toast("Wrong password")
        passwd_v.text = ""

    def on_stop(self):
        self.credentials.close_connection()


PassGuide().run()
