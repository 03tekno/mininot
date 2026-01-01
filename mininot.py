import gi
import os
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, Gio

SAVE_FILE = os.path.expanduser("~/.yerel_notum.txt")
COLOR_FILE = os.path.expanduser("~/.yerel_not_renk.txt")

# Renk Paletleri (Arkaplan, Header)
COLORS = {
    "Sarı": ("#fff9c4", "#fbc02d"),
    "Mavi": ("#e3f2fd", "#1976d2"),
    "Pembe": ("#fce4ec", "#c2185b")
}

class StickyNote(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.set_default_size(300, 350)
        self.set_title("Notum")

        # Stil sağlayıcıyı sınıfa bağlayalım (dinamik değişim için)
        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Ana dikey kutu
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)

        # HeaderBar ve Menü
        self.header = Gtk.HeaderBar()
        self.main_box.append(self.header)

        # Renk Menüsü oluşturma
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("format-color-fill-symbolic")
        
        popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        for name in COLORS.keys():
            btn = Gtk.Button(label=name)
            btn.connect("clicked", self.change_color, name)
            vbox.append(btn)
        
        popover.set_child(vbox)
        menu_button.set_popover(popover)
        self.header.pack_start(menu_button)

        # Metin Alanı
        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_view.set_left_margin(15)
        self.text_view.set_right_margin(15)
        self.text_view.set_top_margin(15)
        self.text_view.set_bottom_margin(15)
        self.text_view.set_vexpand(True)
        
        # Her harf basıldığında otomatik kaydetme sinyali
        self.text_view.get_buffer().connect("changed", self.auto_save)
        
        self.main_box.append(self.text_view)

        # Başlangıç Ayarları
        self.load_data()

    def apply_ui_style(self, color_name):
        bg, head = COLORS.get(color_name, COLORS["Sarı"])
        css = f"""
            window {{ background-color: {bg}; border-radius: 12px; }}
            textview text {{ background-color: {bg}; color: #212121; font-size: 16px; font-family: sans-serif; }}
            headerbar {{ background-color: {head}; border: none; color: white; }}
            button {{ border-radius: 6px; }}
        """
        self.css_provider.load_from_data(css.encode())

    def change_color(self, widget, color_name):
        self.apply_ui_style(color_name)
        with open(COLOR_FILE, "w") as f:
            f.write(color_name)

    def auto_save(self, buffer):
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)
        with open(SAVE_FILE, "w") as f:
            f.write(text)

    def load_data(self):
        # Yazıyı yükle
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                self.text_view.get_buffer().set_text(f.read())
        
        # Rengi yükle
        current_color = "Sarı"
        if os.path.exists(COLOR_FILE):
            with open(COLOR_FILE, "r") as f:
                current_color = f.read().strip()
        self.apply_ui_style(current_color)

class MyApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.kendi.notum.gtk4")

    def do_activate(self):
        win = StickyNote(application=self)
        win.present()

if __name__ == "__main__":
    app = MyApp()
    app.run(None)