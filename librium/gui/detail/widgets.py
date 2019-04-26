from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

from librium.utils.func import load_kv


class Book(TextInput):
    pass


class Section(GridLayout):
    title = StringProperty()


class SingleInput(Section):
    pass


class MultiInput(Section):
    pass


load_kv()
