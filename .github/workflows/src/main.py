from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
import threading, urllib.request, json

SERVER_URL = "http://YOUR_IP:5000/api/chat"
Window.clearcolor = get_color_from_hex("#0d1117")

class ChatApp(App):
    def build(self):
        self.title = "UT Offline AI"
        self.history = []
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)
        header = Label(text="[b]UT Offline AI - Ultra Tech[/b]",
            markup=True, size_hint_y=None, height=50,
            color=get_color_from_hex("#00ff88"), font_size=18)
        root.add_widget(header)
        self.scroll = ScrollView(size_hint=(1,1))
        self.chat_label = Label(text="[color=#888]Start chatting...[/color]",
            markup=True, size_hint_y=None,
            text_size=(350, None),
            color=get_color_from_hex("#e6edf3"),
            font_size=15, halign="left", valign="top", padding=(10,10))
        self.chat_label.bind(texture_size=self.chat_label.setter("size"))
        self.scroll.add_widget(self.chat_label)
        root.add_widget(self.scroll)
        row = BoxLayout(size_hint_y=None, height=50, spacing=8)
        self.inp = TextInput(hint_text="Type question...", multiline=False,
            background_color=get_color_from_hex("#161b22"),
            foreground_color=get_color_from_hex("#e6edf3"),
            font_size=15, size_hint_x=0.8)
        self.inp.bind(on_text_validate=self.send)
        btn = Button(text="Send", size_hint_x=0.2,
            background_color=get_color_from_hex("#00ff88"),
            color=get_color_from_hex("#0d1117"), font_size=14, bold=True)
        btn.bind(on_press=self.send)
        row.add_widget(self.inp)
        row.add_widget(btn)
        root.add_widget(row)
        self.status = Label(text="[color=#888]Ready[/color]",
            markup=True, size_hint_y=None, height=25, font_size=12)
        root.add_widget(self.status)
        return root

    def send(self, *args):
        q = self.inp.text.strip()
        if not q: return
        self.inp.text = ""
        self.add_msg("You", q, "#58a6ff")
        self.status.text = "[color=#ffcc00]Thinking...[/color]"
        threading.Thread(target=self.ask, args=(q,), daemon=True).start()

    def ask(self, q):
        try:
            payload = json.dumps({"messages": self.history[-6:]+[{"role":"user","content":q}]}).encode()
            req = urllib.request.Request(SERVER_URL, data=payload,
                headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode())
            resp = data.get("response","...")
            self.history += [{"role":"user","content":q},{"role":"assistant","content":resp}]
            Clock.schedule_once(lambda dt: self.add_msg("UT AI", resp, "#00ff88"))
            Clock.schedule_once(lambda dt: setattr(self.status,"text","[color=#00ff88]Ready[/color]"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.add_msg("Error", str(e), "#ff4444"))
            Clock.schedule_once(lambda dt: setattr(self.status,"text","[color=#ff4444]Failed[/color]"))

    def add_msg(self, sender, text, color):
        cur = self.chat_label.text
        if "Start chatting" in cur: cur=""
        self.chat_label.text = cur+f"[color={color}][b]{sender}:[/b][/color] {text}\n\n"
        Clock.schedule_once(lambda dt: setattr(self.scroll,"scroll_y",0), 0.1)

if __name__ == "__main__":
    ChatApp().run()
