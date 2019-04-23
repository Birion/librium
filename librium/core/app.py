import kivy
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.app import App

kivy.require("1.10.1")


class LibriumBook(Widget):
    title = StringProperty("None")


class LibriumApp(App):
    def build(self):
        return LibriumBook()
