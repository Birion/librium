import kivy
import pendulum
from kivy import Config
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from pathlib import Path
from librium.database import *
from librium.gui.detail.widgets import Book as KivyBook

kivy.require("1.10.1")

resource_root = Path(__file__).parent.parent / "resources"


def get_res_path(path: str, name: str) -> str:
    res_path = resource_root / path / name
    return str(res_path.resolve())


LabelBase.register(
    name='Roboto',
    fn_regular=get_res_path("fonts/roboto", 'Roboto-Thin.ttf'),
    fn_bold=get_res_path("fonts/roboto", 'Roboto-Medium.ttf')
)
Window.clearcolor = get_color_from_hex("#2d323d")
Factory.register("SingleInput", module="librium.gui.detail.widgets")
Factory.register("MultiInput", module="librium.gui.detail.widgets")
Config.set('input', 'mouse', 'mouse,disable_multitouch')


class LibriumLayout(GridLayout):
    pass


class LibriumApp(App):
    def on_start(self):
        book = Book.query.first()

        root = self.root

        def add_single(section: str):
            widget = root.__getattribute__(section).input
            item = book.__getattribute__(section)
            if isinstance(item, str):
                widget.text = item
            elif isinstance(item, int):
                widget.text = str(item)
            elif isinstance(item, float):
                if item * 10 % 10:
                    widget.text = str(item)
                else:
                    widget.text = str(int(item))
            else:
                widget.text = item.name

        def add_multiple(section: str):
            widget = root.__getattribute__(section)
            items = book.__getattribute__(section)
            for item in items:
                _ = KivyBook()
                _.text = item.name
                widget.add_widget(_)

        for section in ["title", "isbn", "page_count", "price", "format"]:
            add_single(section)

        for section in ["authors", "genres", "languages", "publishers"]:
            add_multiple(section)
