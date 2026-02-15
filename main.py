import os
import json
import time
import threading
import traceback
from io import StringIO

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

# ============================================================
# INTERFACE KV - Limpa e funcional
# ============================================================

KV = '''
#:import dp kivy.metrics.dp

<RoundButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    bold: True
    canvas.before:
        Color:
            rgba: self.bg_color if hasattr(self, 'bg_color') else (0.3, 0.2, 0.8, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

<CardBox@BoxLayout>:
    canvas.before:
        Color:
            rgba: 0.08, 0.08, 0.14, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]

ScreenManager:
    id: sm
'''

# ============================================================
# ANDROID
# ============================================================

class Android:
    """Funcoes Android"""
    
    is_android = platform == 'android'
    
    @staticmethod
    def request_permissions():
        if not Android.is_android:
            return
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.INTERNET,
            ])
        except Exception as e:
            print(f"Perm error: {e}")
    
    @staticmethod
    def request_overlay():
        if not Android.is_android:
            print("[PC] Overlay nao disponivel")
            return
        try:
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            Intent = autoclass('android.content.Intent')
            
            if not Settings.canDrawOverlays(activity):
                intent = Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:" + activity.getPackageName())
                )
                activity.startActivityForResult(intent, 1234)
        except Exception as e:
            print(f"Overlay error: {e}")
    
    @staticmethod
    def request_accessibility():
        if not Android.is_android:
            print("[PC] Acessibilidade nao disponivel")
            return
        try:
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            Settings = autoclass('android.provider.Settings')
            Intent = autoclass('android.content.Intent')
            
            intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            activity.startActivity(intent)
        except Exception as e:
            print(f"Access error: {e}")
    
    @staticmethod
    def request_write_settings():
        if not Android.is_android:
            return
        try:
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            Intent = autoclass('android.content.Intent')
            
            if not Settings.System.canWrite(activity):
                intent = Intent(
                    Settings.ACTION_MANAGE_WRITE_SETTINGS,
                    Uri.parse("package:" + activity.getPackageName())
                )
                activity.startActivity(intent)
        except Exception as e:
            print(f"Write settings error: {e}")
    
    @staticmethod
    def tap(x, y):
        if Android.is_android:
            os.system(f'input tap {x} {y}')
        else:
            print(f"[PC] TAP ({x}, {y})")
    
    @staticmethod
    def swipe(x1, y1, x2, y2, ms=300):
        if Android.is_android:
            os.system(f'input swipe {x1} {y1} {x2} {y2} {ms}')
        else:
            print(f"[PC] SWIPE ({x1},{y1})->({x2},{y2})")
    
    @staticmethod
    def long_press(x, y, ms=1000):
        if Android.is_android:
            os.system(f'input swipe {x} {y} {x} {y} {ms}')
        else:
            print(f"[PC] LONG ({x}, {y})")
    
    @staticmethod
    def key(code):
        if Android.is_android:
            os.system(f'input keyevent {code}')
    
    @staticmethod
    def type_text(text):
        if Android.is_android:
            os.system(f"input text '{text}'")
    
    @staticmethod
    def screenshot(path=None):
        if path is None:
            path = '/sdcard/macro_screen.png'
        if Android.is_android:
            os.system(f'screencap -p {path}')
        return path
    
    @staticmethod
    def toast(msg):
        if not Android.is_android:
            print(f"[TOAST] {msg}")
            return
        try:
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            Toast = autoclass('android.widget.Toast')
            
            @run_on_ui_thread
            def show():
                Toast.makeText(activity, str(msg), Toast.LENGTH_SHORT).show()
            show()
        except:
            pass
    
    @staticmethod
    def vibrate(ms=100):
        if Android.is_android:
            try:
                from jnius import autoclass
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                Context = autoclass('android.content.Context')
                vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
                vibrator.vibrate(ms)
            except:
                pass
    
    @staticmethod
    def battery():
        if Android.is_android:
            try:
                from jnius import autoclass
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                Context = autoclass('android.content.Context')
                BM = autoclass('android.os.BatteryManager')
                bm = activity.getSystemService(Context.BATTERY_SERVICE)
                return bm.getIntProperty(BM.BATTERY_PROPERTY_CAPACITY)
            except:
                pass
        return 100
    
    @staticmethod
    def launch_app(package):
        if Android.is_android:
            try:
                from jnius import autoclass
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                pm = activity.getPackageManager()
                intent = pm.getLaunchIntentForPackage(package)
                if intent:
                    activity.startActivity(intent)
                    return True
            except:
                pass
        return False
    
    @staticmethod
    def brightness(val):
        if Android.is_android:
            try:
                from jnius import autoclass
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                Settings = autoclass('android.provider.Settings')
                Settings.System.putInt(
                    activity.getContentResolver(),
                    Settings.System.SCREEN_BRIGHTNESS,
                    int(val)
                )
            except:
                pass


# ============================================================
# SCRIPT ENGINE
# ============================================================

class ScriptEngine:
    """Executa scripts Python com API de automacao"""
    
    def __init__(self):
        self.output = StringIO()
        self.tags = {}
        self._stop = False
    
    def get_api(self):
        """Retorna funcoes disponiveis nos scripts"""
        return {
            'tap': Android.tap,
            'toque': Android.tap,
            'swipe': Android.swipe,
            'arrastar': Android.swipe,
            'long_press': Android.long_press,
            'segurar': Android.long_press,
            'esperar': time.sleep,
            'wait': time.sleep,
            'sleep': time.sleep,
            'digitar': Android.type_text,
            'type_text': Android.type_text,
            'tecla': Android.key,
            'key': Android.key,
            'screenshot': Android.screenshot,
            'captura': Android.screenshot,
            'home': lambda: Android.key('KEYCODE_HOME'),
            'voltar': lambda: Android.key('KEYCODE_BACK'),
            'back': lambda: Android.key('KEYCODE_BACK'),
            'toast': Android.toast,
            'vibrar': Android.vibrate,
            'bateria': Android.battery,
            'battery': Android.battery,
            'brilho': Android.brightness,
            'brightness': Android.brightness,
            'abrir_app': Android.launch_app,
            'launch': Android.launch_app,
            'log': self._log,
            'print': self._log,
            'tag': self._get_tag,
            'get_tag': self._get_tag,
            'set_tag': self._set_tag,
            'definir_tag': self._set_tag,
            'tags': lambda: self.tags.copy(),
            'parar': self._stop_exec,
            'stop': self._stop_exec,
            'aleatorio': self._random,
            'random': self._random,
            'ler_arquivo': self._read,
            'read_file': self._read,
            'escrever_arquivo': self._write,
            'write_file': self._write,
            'time': time,
            'os': os,
            'json': json,
        }
    
    def _log(self, msg):
        line = f"[{time.strftime('%H:%M:%S')}] {msg}\n"
        self.output.write(line)
    
    def _get_tag(self, name, default=None):
        return self.tags.get(name, default)
    
    def _set_tag(self, name, value):
        self.tags[name] = value
    
    def _stop_exec(self):
        self._stop = True
    
    def _random(self, a, b):
        import random
        if isinstance(a, int) and isinstance(b, int):
            return random.randint(a, b)
        return random.uniform(a, b)
    
    def _read(self, path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except:
            return None
    
    def _write(self, path, content):
        try:
            with open(path, 'w') as f:
                f.write(str(content))
            return True
        except:
            return False
    
    def run(self, code, callback=None):
        """Executa codigo em thread separada"""
        self.output = StringIO()
        self._stop = False
        
        def _exec():
            try:
                api = self.get_api()
                exec(code, api)
                result = {'ok': True, 'output': self.output.getvalue()}
            except Exception as e:
                result = {
                    'ok': False,
                    'error': str(e),
                    'trace': traceback.format_exc()
                }
            
            if callback:
                Clock.schedule_once(lambda dt: callback(result))
        
        t = threading.Thread(target=_exec, daemon=True)
        t.start()
        return t
    
    def stop(self):
        self._stop = True


# ============================================================
# DADOS
# ============================================================

if platform == 'android':
    from android.storage import app_storage_path
    DATA_DIR = app_storage_path()
else:
    DATA_DIR = os.path.expanduser('~/.macrovision')

os.makedirs(DATA_DIR, exist_ok=True)
SAVE_FILE = os.path.join(DATA_DIR, 'save.json')


class MacroAction:
    def __init__(self):
        self.name = 'Nova Acao'
        self.type = 'tap'
        self.enabled = True
        self.x = 500
        self.y = 800
        self.x2 = 500
        self.y2 = 400
        self.duration = 300
        self.wait_sec = 1.0
        self.script = ''
        self.key_code = 'KEYCODE_BACK'
        self.text = ''
        self.app_pkg = ''
        self.repeats = 1
        self.delay = 0.5
    
    def to_dict(self):
        return self.__dict__.copy()
    
    @staticmethod
    def from_dict(d):
        a = MacroAction()
        for k, v in d.items():
            if hasattr(a, k):
                setattr(a, k, v)
        return a


class MacroData:
    def __init__(self, name='Novo Macro'):
        self.id = int(time.time() * 1000)
        self.name = name
        self.actions = []
        self.script = ''
        self.tags = {}
        self.images = []
        self.is_running = False
        self.loop = False
        self.loop_count = 0
        self.loop_delay = 1.0
        self.runs = 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'actions': [a.to_dict() for a in self.actions],
            'script': self.script,
            'tags': self.tags,
            'images': self.images,
            'loop': self.loop,
            'loop_count': self.loop_count,
            'loop_delay': self.loop_delay,
            'runs': self.runs,
        }
    
    @staticmethod
    def from_dict(d):
        m = MacroData(d.get('name', 'Macro'))
        m.id = d.get('id', m.id)
        m.script = d.get('script', '')
        m.tags = d.get('tags', {})
        m.images = d.get('images', [])
        m.loop = d.get('loop', False)
        m.loop_count = d.get('loop_count', 0)
        m.loop_delay = d.get('loop_delay', 1.0)
        m.runs = d.get('runs', 0)
        m.actions = [MacroAction.from_dict(a) for a in d.get('actions', [])]
        return m


# ============================================================
# HELPERS
# ============================================================

def make_button(text, color, callback, height=50, font_size=14):
    """Cria botao padronizado"""
    btn = Button(
        text=text,
        size_hint_y=None,
        height=dp(height),
        font_size=dp(font_size),
        bold=True,
        background_normal='',
        background_color=color,
        color=(1, 1, 1, 1)
    )
    btn.bind(on_release=lambda x: callback())
    return btn


def make_label(text, size=14, color=(0.9, 0.9, 0.95, 1), height=30, bold=False):
    """Cria label padronizado"""
    return Label(
        text=text,
        font_size=dp(size),
        color=color,
        size_hint_y=None,
        height=dp(height),
        bold=bold,
        halign='left'
    )


def make_input(text='', hint='', multiline=False, height=45, input_filter=None):
    """Cria input padronizado"""
    return TextInput(
        text=text,
        hint_text=hint,
        multiline=multiline,
        size_hint_y=None,
        height=dp(height),
        font_size=dp(14),
        background_color=(0.08, 0.08, 0.14, 1),
        foreground_color=(0.9, 0.9, 0.95, 1),
        cursor_color=(0, 0.8, 0.8, 1),
        hint_text_color=(0.4, 0.4, 0.5, 1),
        padding=[dp(12), dp(10)],
        input_filter=input_filter,
    )


def show_popup(title, content, size=(0.85, 0.4)):
    """Mostra popup"""
    p = Popup(
        title=title,
        content=content,
        size_hint=size,
        title_color=(1, 1, 1, 1),
        separator_color=(0.3, 0.2, 0.8, 1),
    )
    p.open()
    return p


def show_message(title, msg, duration=2):
    """Mostra mensagem temporaria"""
    p = show_popup(title, Label(text=msg, color=(1, 1, 1, 1)), (0.7, 0.25))
    Clock.schedule_once(lambda dt: p.dismiss(), duration)


# ============================================================
# TELA PRINCIPAL
# ============================================================

class HomeScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(name='home', **kwargs)
        self.app_ref = app
        self._build()
    
    def _build(self):
        self.clear_widgets()
        
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        root.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with root.canvas.before:
            Color(0.04, 0.04, 0.08, 1)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(self._bg, 'pos', root.pos),
                  size=lambda *a: setattr(self._bg, 'size', root.size))
        
        # Titulo
        root.add_widget(make_label('Macro Vision AI', size=26, bold=True,
                                   color=(0, 0.9, 0.85, 1), height=50))
        
        running = sum(1 for m in self.app_ref.macros if m.is_running)
        status = f'{running} em execucao' if running else 'Nenhum ativo'
        root.add_widget(make_label(status, size=13, color=(0.5, 0.5, 0.6, 1), height=25))
        
        # Lista de macros
        scroll = ScrollView()
        self.macro_list = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=dp(10),
            padding=dp(5)
        )
        self.macro_list.bind(minimum_height=self.macro_list.setter('height'))
        
        if not self.app_ref.macros:
            self.macro_list.add_widget(make_label(
                'Nenhum macro criado\nToque em Novo Macro para comecar',
                color=(0.4, 0.4, 0.5, 1),
                height=80
            ))
        else:
            for macro in self.app_ref.macros:
                self.macro_list.add_widget(self._macro_card(macro))
        
        scroll.add_widget(self.macro_list)
        root.add_widget(scroll)
        
        # Botoes
        btns = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        btns.add_widget(make_button(
            'Novo Macro', (0.06, 0.72, 0.5, 1),
            self._new_macro, font_size=15
        ))
        btns.add_widget(make_button(
            'Parar Todos', (0.85, 0.2, 0.2, 1),
            self._stop_all, font_size=15
        ))
        root.add_widget(btns)
        
        # Permissoes
        perm_btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        perm_btns.add_widget(make_button(
            'Overlay', (0.45, 0.25, 0.85, 1),
            Android.request_overlay, height=45, font_size=12
        ))
        perm_btns.add_widget(make_button(
            'Acessibilidade', (0.45, 0.25, 0.85, 1),
            Android.request_accessibility, height=45, font_size=12
        ))
        perm_btns.add_widget(make_button(
            'Config Sistema', (0.45, 0.25, 0.85, 1),
            Android.request_write_settings, height=45, font_size=12
        ))
        root.add_widget(perm_btns)
        
        self.add_widget(root)
    
    def _macro_card(self, macro):
        card = BoxLayout(
            size_hint_y=None,
            height=dp(90),
            spacing=dp(10),
            padding=dp(10)
        )
        
        from kivy.graphics import Color, RoundedRectangle
        with card.canvas.before:
            Color(0.08, 0.08, 0.14, 1)
            card._rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
        card.bind(
            pos=lambda *a: setattr(card._rect, 'pos', card.pos),
            size=lambda *a: setattr(card._rect, 'size', card.size)
        )
        
        # Info
        info = BoxLayout(orientation='vertical', size_hint_x=0.55)
        info.add_widget(make_label(macro.name, size=16, bold=True, height=25))
        
        details = f'{len(macro.actions)} acoes'
        if macro.images:
            details += f' | {len(macro.images)} imgs'
        if macro.tags:
            details += f' | {len(macro.tags)} tags'
        info.add_widget(make_label(details, size=11, color=(0.5, 0.5, 0.6, 1), height=20))
        info.add_widget(make_label(
            f'Execucoes: {macro.runs}',
            size=11, color=(0, 0.7, 0.7, 1), height=20
        ))
        card.add_widget(info)
        
        # Botoes
        btns = BoxLayout(orientation='vertical', size_hint_x=0.45, spacing=dp(5))
        
        run_text = 'Parar' if macro.is_running else 'Executar'
        run_color = (0.85, 0.2, 0.2, 1) if macro.is_running else (0.06, 0.72, 0.5, 1)
        btns.add_widget(make_button(
            run_text, run_color,
            lambda m=macro: self._toggle_run(m),
            height=35, font_size=12
        ))
        
        row = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(35))
        row.add_widget(make_button(
            'Abrir', (0.4, 0.25, 0.85, 1),
            lambda m=macro: self.app_ref.go_macro(m),
            height=35, font_size=12
        ))
        row.add_widget(make_button(
            'Excluir', (0.6, 0.1, 0.1, 1),
            lambda m=macro: self._delete_macro(m),
            height=35, font_size=12
        ))
        btns.add_widget(row)
        
        card.add_widget(btns)
        return card
    
    def _new_macro(self):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
        content.add_widget(make_label('Nome do macro:', height=25))
        name_input = make_input(hint='Meu Macro')
        content.add_widget(name_input)
        
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        popup = show_popup('Novo Macro', content, (0.85, 0.35))
        
        def create():
            name = name_input.text.strip() or f'Macro {len(self.app_ref.macros) + 1}'
            macro = MacroData(name)
            self.app_ref.macros.append(macro)
            self.app_ref.save()
            popup.dismiss()
            self.app_ref.go_macro(macro)
        
        btns.add_widget(make_button('Criar', (0.06, 0.72, 0.5, 1), create))
        btns.add_widget(make_button('Cancelar', (0.4, 0.1, 0.1, 1), popup.dismiss))
        content.add_widget(btns)
    
    def _toggle_run(self, macro):
        macro.is_running = not macro.is_running
        if macro.is_running:
            macro.runs += 1
            self.app_ref.run_macro(macro)
        else:
            self.app_ref.engine.stop()
        self.app_ref.save()
        self._build()
    
    def _delete_macro(self, macro):
        macro.is_running = False
        self.app_ref.macros.remove(macro)
        self.app_ref.save()
        self._build()
    
    def _stop_all(self):
        for m in self.app_ref.macros:
            m.is_running = False
        self.app_ref.engine.stop()
        self.app_ref.save()
        self._build()
    
    def on_pre_enter(self):
        self._build()


# ============================================================
# TELA DO MACRO (com abas)
# ============================================================

class MacroScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(name='macro', **kwargs)
        self.app_ref = app
        self.macro = None
        self.current_tab = 'actions'
    
    def set_macro(self, macro):
        self.macro = macro
        self.current_tab = 'actions'
        self._build()
    
    def _build(self):
        self.clear_widgets()
        if not self.macro:
            return
        
        root = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(8))
        
        from kivy.graphics import Color, Rectangle
        with root.canvas.before:
            Color(0.04, 0.04, 0.08, 1)
            root._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._bg, 'pos', root.pos),
                  size=lambda *a: setattr(root._bg, 'size', root.size))
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        header.add_widget(make_button(
            'Voltar', (0.2, 0.2, 0.3, 1),
            lambda: self.app_ref.go_home(),
            height=45, font_size=13
        ))
        header.add_widget(make_label(self.macro.name, size=18, bold=True, height=45))
        
        run_text = 'Parar' if self.macro.is_running else 'Executar'
        run_color = (0.85, 0.2, 0.2, 1) if self.macro.is_running else (0.06, 0.72, 0.5, 1)
        header.add_widget(make_button(
            run_text, run_color,
            self._toggle_run,
            height=45, font_size=13
        ))
        root.add_widget(header)
        
        # Abas
        tabs = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        
        tab_data = [
            ('Acoes', 'actions'),
            ('Imagens', 'images'),
            ('Codigo', 'code'),
            ('Tags', 'tags'),
            ('Config', 'config'),
        ]
        
        for tab_text, tab_id in tab_data:
            is_active = self.current_tab == tab_id
            color = (0.4, 0.25, 0.85, 1) if is_active else (0.12, 0.12, 0.2, 1)
            tabs.add_widget(make_button(
                tab_text, color,
                lambda t=tab_id: self._switch_tab(t),
                height=45, font_size=12
            ))
        
        root.add_widget(tabs)
        
        # Conteudo da aba
        content = BoxLayout()
        
        if self.current_tab == 'actions':
            content.add_widget(self._build_actions())
        elif self.current_tab == 'images':
            content.add_widget(self._build_images())
        elif self.current_tab == 'code':
            content.add_widget(self._build_code())
        elif self.current_tab == 'tags':
            content.add_widget(self._build_tags())
        elif self.current_tab == 'config':
            content.add_widget(self._build_config())
        
        root.add_widget(content)
        self.add_widget(root)
    
    def _switch_tab(self, tab):
        self.current_tab = tab
        self._build()
    
    # ---- ABA ACOES ----
    
    def _build_actions(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(8))
        
        scroll = ScrollView()
        lst = GridLayout(cols=1, size_hint_y=None, spacing=dp(8), padding=dp(5))
        lst.bind(minimum_height=lst.setter('height'))
        
        if not self.macro.actions:
            lst.add_widget(make_label(
                'Nenhuma acao\nToque em Adicionar Acao',
                color=(0.4, 0.4, 0.5, 1), height=60
            ))
        else:
            for i, action in enumerate(self.macro.actions):
                lst.add_widget(self._action_card(i, action))
        
        scroll.add_widget(lst)
        layout.add_widget(scroll)
        
        layout.add_widget(make_button(
            'Adicionar Acao', (0, 0.7, 0.75, 1),
            self._add_action, height=50, font_size=14
        ))
        
        return layout
    
    def _action_card(self, idx, action):
        card = BoxLayout(size_hint_y=None, height=dp(65), spacing=dp(8), padding=dp(8))
        
        from kivy.graphics import Color, RoundedRectangle
        with card.canvas.before:
            Color(0.08, 0.08, 0.14, 1)
            card._r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
        card.bind(
            pos=lambda *a: setattr(card._r, 'pos', card.pos),
            size=lambda *a: setattr(card._r, 'size', card.size)
        )
        
        # Info
        info = BoxLayout(orientation='vertical', size_hint_x=0.5)
        color = (0.9, 0.9, 0.95, 1) if action.enabled else (0.4, 0.4, 0.5, 1)
        info.add_widget(make_label(action.name, size=13, bold=True, color=color, height=20))
        info.add_widget(make_label(action.type.upper(), size=11, color=(0.5, 0.5, 0.6, 1), height=18))
        card.add_widget(info)
        
        # Botoes
        btns = BoxLayout(size_hint_x=0.5, spacing=dp(5))
        
        toggle_text = 'ON' if action.enabled else 'OFF'
        toggle_color = (0.06, 0.72, 0.5, 1) if action.enabled else (0.85, 0.2, 0.2, 1)
        btns.add_widget(make_button(
            toggle_text, toggle_color,
            lambda a=action: self._toggle_action(a),
            height=40, font_size=11
        ))
        btns.add_widget(make_button(
            'Editar', (0.4, 0.25, 0.85, 1),
            lambda a=action: self.app_ref.go_edit_action(self.macro, a),
            height=40, font_size=11
        ))
        btns.add_widget(make_button(
            'X', (0.6, 0.1, 0.1, 1),
            lambda i=idx: self._delete_action(i),
            height=40, font_size=11
        ))
        card.add_widget(btns)
        
        return card
    
    def _add_action(self):
        action = MacroAction()
        self.app_ref.go_edit_action(self.macro, action, is_new=True)
    
    def _toggle_action(self, action):
        action.enabled = not action.enabled
        self.app_ref.save()
        self._build()
    
    def _delete_action(self, idx):
        if 0 <= idx < len(self.macro.actions):
            self.macro.actions.pop(idx)
            self.app_ref.save()
            self._build()
    
    # ---- ABA IMAGENS ----
    
    def _build_images(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(8))
        
        layout.add_widget(make_label(
            'Imagens de referencia do macro',
            size=13, color=(0.5, 0.5, 0.6, 1), height=25
        ))
        
        scroll = ScrollView()
        lst = GridLayout(cols=2, size_hint_y=None, spacing=dp(8), padding=dp(5))
        lst.bind(minimum_height=lst.setter('height'))
        
        if not self.macro.images:
            lst.add_widget(make_label(
                'Nenhuma imagem\nToque em Adicionar Imagem',
                color=(0.4, 0.4, 0.5, 1), height=60
            ))
        else:
            for i, img_path in enumerate(self.macro.images):
                card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(140), padding=dp(5))
                
                from kivy.graphics import Color, RoundedRectangle
                with card.canvas.before:
                    Color(0.08, 0.08, 0.14, 1)
                    card._r = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
                card.bind(
                    pos=lambda *a, c=card: setattr(c._r, 'pos', c.pos),
                    size=lambda *a, c=card: setattr(c._r, 'size', c.size)
                )
                
                if os.path.exists(img_path):
                    card.add_widget(Image(source=img_path, size_hint_y=0.7))
                else:
                    card.add_widget(make_label('Arquivo nao encontrado', height=40))
                
                fname = os.path.basename(img_path)
                card.add_widget(make_label(fname[:20], size=10, height=20))
                
                card.add_widget(make_button(
                    'Remover', (0.6, 0.1, 0.1, 1),
                    lambda idx=i: self._remove_image(idx),
                    height=30, font_size=11
                ))
                
                lst.add_widget(card)
        
        scroll.add_widget(lst)
        layout.add_widget(scroll)
        
        # BOTAO DE ADICIONAR IMAGEM
        layout.add_widget(make_button(
            'Adicionar Imagem', (0, 0.7, 0.75, 1),
            self._add_image, height=55, font_size=15
        ))
        
        return layout
    
    def _add_image(self):
        """Abre seletor de arquivo para imagem"""
        content = BoxLayout(orientation='vertical', spacing=dp(5))
        
        # Determinar caminho inicial
        if os.path.exists('/storage/emulated/0'):
            start_path = '/storage/emulated/0'
        elif os.path.exists(os.path.expanduser('~/Pictures')):
            start_path = os.path.expanduser('~/Pictures')
        else:
            start_path = os.path.expanduser('~')
        
        # File chooser SEM filtro para mostrar TODOS os arquivos
        fc = FileChooserListView(
            path=start_path,
            size_hint_y=0.8
        )
        content.add_widget(fc)
        
        popup = show_popup('Selecionar Arquivo', content, (0.95, 0.9))
        
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        def do_select():
            if fc.selection:
                path = fc.selection[0]
                self.macro.images.append(path)
                self.app_ref.save()
                popup.dismiss()
                self._build()
            else:
                show_message('Aviso', 'Selecione um arquivo')
        
        btns.add_widget(make_button('Selecionar', (0.06, 0.72, 0.5, 1), do_select))
        btns.add_widget(make_button('Cancelar', (0.5, 0.1, 0.1, 1), popup.dismiss))
        content.add_widget(btns)
    
    def _remove_image(self, idx):
        if 0 <= idx < len(self.macro.images):
            self.macro.images.pop(idx)
            self.app_ref.save()
            self._build()
    
    # ---- ABA CODIGO ----
    
    def _build_code(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(5))
        
        layout.add_widget(make_label(
            'Codigo Python com funcoes de automacao',
            size=12, color=(0.5, 0.5, 0.6, 1), height=22
        ))
        
        default_code = '''# Funcoes: tap, swipe, esperar, digitar,
# home, voltar, screenshot, abrir_app,
# brilho, vibrar, bateria, toast, log,
# tag, set_tag, aleatorio, ler_arquivo,
# escrever_arquivo

log("Iniciando...")
esperar(1)
tap(500, 800)
log("Pronto!")
'''
        
        self.code_input = make_input(
            text=self.macro.script or default_code,
            multiline=True,
            height=250
        )
        self.code_input.size_hint_y = 0.5
        layout.add_widget(self.code_input)
        
        layout.add_widget(make_label('Saida:', size=12, color=(0.5, 0.5, 0.6, 1), height=20))
        
        out_scroll = ScrollView(size_hint_y=0.25)
        self.output_label = Label(
            text='',
            font_size=dp(11),
            color=(0, 0.8, 0.8, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
            markup=True
        )
        self.output_label.bind(texture_size=lambda i, s: setattr(i, 'height', s[1] + dp(10)))
        self.output_label.bind(size=self.output_label.setter('text_size'))
        out_scroll.add_widget(self.output_label)
        layout.add_widget(out_scroll)
        
        btns = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        btns.add_widget(make_button(
            'Executar', (0.06, 0.72, 0.5, 1),
            self._run_code, font_size=13
        ))
        btns.add_widget(make_button(
            'Salvar', (0.4, 0.25, 0.85, 1),
            self._save_code, font_size=13
        ))
        btns.add_widget(make_button(
            'Ajuda', (0.2, 0.2, 0.3, 1),
            self._show_help, font_size=13
        ))
        layout.add_widget(btns)
        
        return layout
    
    def _run_code(self):
        code = self.code_input.text
        self.output_label.text = 'Executando...'
        
        self.app_ref.engine.tags = self.macro.tags.copy()
        
        def on_done(result):
            if result['ok']:
                self.output_label.text = result.get('output', 'Concluido!')
                self.macro.tags.update(self.app_ref.engine.tags)
                self.app_ref.save()
            else:
                self.output_label.text = f"ERRO: {result['error']}\n\n{result.get('trace', '')}"
        
        self.app_ref.engine.run(code, on_done)
    
    def _save_code(self):
        self.macro.script = self.code_input.text
        self.app_ref.save()
        show_message('Salvo', 'Codigo salvo com sucesso!')
    
    def _show_help(self):
        help_text = '''FUNCOES PYTHON DISPONIVEIS

TOQUES:
  tap(x, y) - Toque
  swipe(x1,y1,x2,y2) - Arrastar
  long_press(x, y) - Segurar
  digitar("texto") - Digitar

TEMPO:
  esperar(segundos) - Aguardar

SISTEMA:
  home() - Tela inicial
  voltar() - Botao voltar
  screenshot() - Captura tela
  abrir_app("com.app") - Abrir app

DISPOSITIVO:
  brilho(0-255) - Ajustar brilho
  vibrar(ms) - Vibrar
  bateria() - Nivel bateria

TAGS:
  set_tag("nome", valor)
  tag("nome") - Obter valor
  tags() - Todas as tags

UTILIDADES:
  log("msg") - Registrar
  toast("msg") - Notificacao
  aleatorio(min, max) - Aleatorio
  ler_arquivo(caminho)
  escrever_arquivo(caminho, texto)

CONTROLE:
  parar() - Para execucao
'''
        content = ScrollView()
        lbl = Label(
            text=help_text,
            font_size=dp(12),
            color=(0.9, 0.9, 0.95, 1),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        lbl.bind(texture_size=lambda i, s: setattr(i, 'height', s[1] + dp(20)))
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)
        show_popup('Ajuda Python', content, (0.9, 0.85))
    
    # ---- ABA TAGS ----
    
    def _build_tags(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(5))
        
        layout.add_widget(make_label(
            'Tags: variaveis que voce usa nos scripts',
            size=12, color=(0.5, 0.5, 0.6, 1), height=22
        ))
        
        scroll = ScrollView()
        lst = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        lst.bind(minimum_height=lst.setter('height'))
        
        if not self.macro.tags:
            lst.add_widget(make_label('Nenhuma tag', color=(0.4, 0.4, 0.5, 1), height=40))
        else:
            for name, value in self.macro.tags.items():
                row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
                row.add_widget(make_label(f'{name}:', size=13, color=(0, 0.8, 0.8, 1), height=35))
                row.add_widget(make_label(str(value), size=13, height=35))
                row.add_widget(make_button(
                    'X', (0.6, 0.1, 0.1, 1),
                    lambda n=name: self._del_tag(n),
                    height=35, font_size=11
                ))
                lst.add_widget(row)
        
        scroll.add_widget(lst)
        layout.add_widget(scroll)
        
        # Nova tag
        new_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        self.tag_name = make_input(hint='Nome')
        self.tag_value = make_input(hint='Valor')
        new_row.add_widget(self.tag_name)
        new_row.add_widget(self.tag_value)
        new_row.add_widget(make_button(
            'Add', (0.06, 0.72, 0.5, 1),
            self._add_tag, height=45, font_size=12
        ))
        layout.add_widget(new_row)
        
        return layout
    
    def _add_tag(self):
        name = self.tag_name.text.strip()
        value = self.tag_value.text.strip()
        if name:
            try:
                value = int(value)
            except:
                try:
                    value = float(value)
                except:
                    pass
            self.macro.tags[name] = value
            self.app_ref.save()
            self._build()
    
    def _del_tag(self, name):
        if name in self.macro.tags:
            del self.macro.tags[name]
            self.app_ref.save()
            self._build()
    
    # ---- ABA CONFIG ----
    
    def _build_config(self):
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=dp(10))
        layout.bind(minimum_height=layout.setter('height'))
        
        layout.add_widget(make_label('Nome do Macro', size=12, color=(0.5, 0.5, 0.6, 1), height=22))
        self.cfg_name = make_input(text=self.macro.name)
        layout.add_widget(self.cfg_name)
        
        # Loop
        loop_row = BoxLayout(size_hint_y=None, height=dp(45))
        loop_row.add_widget(make_label('Repetir em loop', height=40))
        self.loop_switch = Switch(active=self.macro.loop, size_hint_x=0.3)
        loop_row.add_widget(self.loop_switch)
        layout.add_widget(loop_row)
        
        count_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        count_row.add_widget(make_label('Repeticoes (0=infinito):', size=12, height=40))
        self.cfg_count = make_input(text=str(self.macro.loop_count), input_filter='int')
        count_row.add_widget(self.cfg_count)
        layout.add_widget(count_row)
        
        delay_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        delay_row.add_widget(make_label('Intervalo (seg):', size=12, height=40))
        self.cfg_delay = make_input(text=str(self.macro.loop_delay), input_filter='float')
        delay_row.add_widget(self.cfg_delay)
        layout.add_widget(delay_row)
        
        layout.add_widget(make_button(
            'Salvar Configuracoes', (0.06, 0.72, 0.5, 1),
            self._save_config, height=50, font_size=14
        ))
        
        layout.add_widget(make_label(
            f'Execucoes: {self.macro.runs}',
            size=12, color=(0, 0.7, 0.7, 1), height=30
        ))
        
        scroll.add_widget(layout)
        return scroll
    
    def _save_config(self):
        self.macro.name = self.cfg_name.text.strip() or 'Macro'
        self.macro.loop = self.loop_switch.active
        try:
            self.macro.loop_count = int(self.cfg_count.text)
        except:
            pass
        try:
            self.macro.loop_delay = float(self.cfg_delay.text)
        except:
            pass
        self.app_ref.save()
        show_message('Salvo', 'Configuracoes salvas!')
    
    def _toggle_run(self):
        self.macro.is_running = not self.macro.is_running
        if self.macro.is_running:
            self.macro.runs += 1
            self.app_ref.run_macro(self.macro)
        else:
            self.app_ref.engine.stop()
        self.app_ref.save()
        self._build()


# ============================================================
# TELA EDITAR ACAO
# ============================================================

class EditActionScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(name='edit_action', **kwargs)
        self.app_ref = app
        self.macro = None
        self.action = None
        self.is_new = False
    
    def set_data(self, macro, action, is_new=False):
        self.macro = macro
        self.action = action
        self.is_new = is_new
        self._build()
    
    def _build(self):
        self.clear_widgets()
        
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        
        from kivy.graphics import Color, Rectangle
        with root.canvas.before:
            Color(0.04, 0.04, 0.08, 1)
            root._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda *a: setattr(root._bg, 'pos', root.pos),
                  size=lambda *a: setattr(root._bg, 'size', root.size))
        
        # Header
        title = 'Nova Acao' if self.is_new else 'Editar Acao'
        header = BoxLayout(size_hint_y=None, height=dp(45))
        header.add_widget(make_button(
            'Voltar', (0.2, 0.2, 0.3, 1),
            lambda: self.app_ref.go_macro(self.macro),
            height=40, font_size=13
        ))
        header.add_widget(make_label(title, size=18, bold=True, height=40))
        root.add_widget(header)
        
        # Content
        scroll = ScrollView()
        content = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(5))
        content.bind(minimum_height=content.setter('height'))
        
        # Nome
        content.add_widget(make_label('Nome:', size=12, color=(0.5, 0.5, 0.6, 1), height=22))
        self.name_input = make_input(text=self.action.name, hint='Nome da acao')
        content.add_widget(self.name_input)
        
        # Tipo
        content.add_widget(make_label('Tipo:', size=12, color=(0.5, 0.5, 0.6, 1), height=22))
        self.type_spinner = Spinner(
            text=self.action.type,
            values=['tap', 'swipe', 'long_press', 'wait', 'script', 'key', 'text', 'app'],
            size_hint_y=None,
            height=dp(45),
            background_color=(0.12, 0.12, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        self.type_spinner.bind(text=lambda *a: self._build())
        content.add_widget(self.type_spinner)
        
        # Opcoes baseadas no tipo
        t = self.type_spinner.text
        
        if t in ['tap', 'long_press']:
            content.add_widget(make_label('Coordenadas:', size=12, color=(0.5, 0.5, 0.6, 1), height=22))
            
            coord = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
            coord.add_widget(make_label('X:', height=40))
            self.x_input = make_input(text=str(self.action.x), input_filter='int')
            coord.add_widget(self.x_input)
            coord.add_widget(make_label('Y:', height=40))
            self.y_input = make_input(text=str(self.action.y), input_filter='int')
            coord.add_widget(self.y_input)
            content.add_widget(coord)
            
            if t == 'long_press':
                content.add_widget(make_label('Duracao (ms):', size=12, height=22))
                self.dur_input = make_input(text=str(self.action.duration), input_filter='int')
                content.add_widget(self.dur_input)
        
        elif t == 'swipe':
            content.add_widget(make_label('De:', size=12, color=(0.5, 0.5, 0.6, 1), height=22))
            coord1 = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
            coord1.add_widget(make_label('X:', height=40))
            self.x_input = make_input(text=str(self.action.x), input_filter='int')
            coord1.add_widget(self.x_input)
            coord1.add_widget(make_label('Y:', height=40))
            self.y_input = make_input(text=str(self.action.y), input_filter='int')
            coord1.add_widget(self.y_input)
            content.add_widget(coord1)
            
            content.add_widget(make_label('Para:', size=12, color=(0.5, 0.5, 0.6, 1), height=22))
            coord2 = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
            coord2.add_widget(make_label('X:', height=40))
            self.x2_input = make_input(text=str(self.action.x2), input_filter='int')
            coord2.add_widget(self.x2_input)
            coord2.add_widget(make_label('Y:', height=40))
            self.y2_input = make_input(text=str(self.action.y2), input_filter='int')
            coord2.add_widget(self.y2_input)
            content.add_widget(coord2)
            
            content.add_widget(make_label('Duracao (ms):', size=12, height=22))
            self.dur_input = make_input(text=str(self.action.duration), input_filter='int')
            content.add_widget(self.dur_input)
        
        elif t == 'wait':
            content.add_widget(make_label('Tempo (segundos):', size=12, height=22))
            self.wait_input = make_input(text=str(self.action.wait_sec), input_filter='float')
            content.add_widget(self.wait_input)
        
        elif t == 'script':
            content.add_widget(make_label('Codigo Python:', size=12, height=22))
            self.script_input = make_input(
                text=self.action.script or 'tap(500, 800)',
                multiline=True,
                height=150
            )
            content.add_widget(self.script_input)
        
        elif t == 'key':
            content.add_widget(make_label('Tecla:', size=12, height=22))
            self.key_spinner = Spinner(
                text=self.action.key_code,
                values=[
                    'KEYCODE_BACK', 'KEYCODE_HOME', 'KEYCODE_APP_SWITCH',
                    'KEYCODE_VOLUME_UP', 'KEYCODE_VOLUME_DOWN',
                    'KEYCODE_ENTER', 'KEYCODE_POWER', 'KEYCODE_CAMERA',
                    'KEYCODE_MENU', 'KEYCODE_SEARCH'
                ],
                size_hint_y=None,
                height=dp(45),
                background_color=(0.12, 0.12, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            content.add_widget(self.key_spinner)
        
        elif t == 'text':
            content.add_widget(make_label('Texto:', size=12, height=22))
            self.text_input = make_input(text=self.action.text, multiline=True, height=80)
            content.add_widget(self.text_input)
        
        elif t == 'app':
            content.add_widget(make_label('Pacote do App:', size=12, height=22))
            self.app_input = make_input(text=self.action.app_pkg, hint='com.example.app')
            content.add_widget(self.app_input)
        
        # Repeticao
        content.add_widget(make_label('Repetir:', size=12, color=(0.5, 0.5, 0.6, 1), height=22))
        rep_row = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        self.repeat_input = make_input(text=str(self.action.repeats), input_filter='int')
        rep_row.add_widget(self.repeat_input)
        rep_row.add_widget(make_label('vezes', height=40))
        content.add_widget(rep_row)
        
        scroll.add_widget(content)
        root.add_widget(scroll)
        
        # Salvar
        footer = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(10))
        footer.add_widget(make_button(
            'Cancelar', (0.2, 0.2, 0.3, 1),
            lambda: self.app_ref.go_macro(self.macro),
            font_size=14
        ))
        footer.add_widget(make_button(
            'Salvar', (0.06, 0.72, 0.5, 1),
            self._save,
            font_size=14
        ))
        root.add_widget(footer)
        
        self.add_widget(root)
    
    def _save(self):
        self.action.name = self.name_input.text.strip() or 'Acao'
        self.action.type = self.type_spinner.text
        
        try:
            self.action.repeats = int(self.repeat_input.text)
        except:
            pass
        
        t = self.action.type
        
        if t in ['tap', 'long_press']:
            try:
                self.action.x = int(self.x_input.text)
                self.action.y = int(self.y_input.text)
            except:
                pass
            if t == 'long_press':
                try:
                    self.action.duration = int(self.dur_input.text)
                except:
                    pass
        
        elif t == 'swipe':
            try:
                self.action.x = int(self.x_input.text)
                self.action.y = int(self.y_input.text)
                self.action.x2 = int(self.x2_input.text)
                self.action.y2 = int(self.y2_input.text)
                self.action.duration = int(self.dur_input.text)
            except:
                pass
        
        elif t == 'wait':
            try:
                self.action.wait_sec = float(self.wait_input.text)
            except:
                pass
        
        elif t == 'script':
            self.action.script = self.script_input.text
        
        elif t == 'key':
            self.action.key_code = self.key_spinner.text
        
        elif t == 'text':
            self.action.text = self.text_input.text
        
        elif t == 'app':
            self.action.app_pkg = self.app_input.text.strip()
        
        if self.is_new:
            self.macro.actions.append(self.action)
        
        self.app_ref.save()
        self.app_ref.go_macro(self.macro)


# ============================================================
# APP
# ============================================================

class MacroVisionApp(App):
    
    def build(self):
        self.title = 'Macro Vision AI'
        Window.clearcolor = (0.04, 0.04, 0.08, 1)
        
        self.macros = []
        self.engine = ScriptEngine()
        
        self.sm = ScreenManager(transition=SlideTransition(duration=0.2))
        
        self.home_screen = HomeScreen(self)
        self.macro_screen = MacroScreen(self)
        self.edit_screen = EditActionScreen(self)
        
        self.sm.add_widget(self.home_screen)
        self.sm.add_widget(self.macro_screen)
        self.sm.add_widget(self.edit_screen)
        
        self.load()
        
        if platform == 'android':
            Android.request_permissions()
        
        return self.sm
    
    def go_home(self):
        self.sm.transition.direction = 'right'
        self.sm.current = 'home'
    
    def go_macro(self, macro):
        self.macro_screen.set_macro(macro)
        self.sm.transition.direction = 'left'
        self.sm.current = 'macro'
    
    def go_edit_action(self, macro, action, is_new=False):
        self.edit_screen.set_data(macro, action, is_new)
        self.sm.transition.direction = 'left'
        self.sm.current = 'edit_action'
    
    def run_macro(self, macro):
        """Executa um macro"""
        if macro.script:
            self.engine.tags = macro.tags.copy()
            
            def on_done(result):
                macro.tags.update(self.engine.tags)
                self.save()
                
                if macro.loop and macro.is_running:
                    if macro.loop_count == 0 or macro.runs < macro.loop_count:
                        Clock.schedule_once(
                            lambda dt: self.run_macro(macro),
                            macro.loop_delay
                        )
            
            self.engine.run(macro.script, on_done)
        
        elif macro.actions:
            def run_actions():
                for action in macro.actions:
                    if not macro.is_running:
                        break
                    if not action.enabled:
                        continue
                    
                    for _ in range(action.repeats):
                        if not macro.is_running:
                            break
                        
                        t = action.type
                        if t == 'tap':
                            Android.tap(action.x, action.y)
                        elif t == 'swipe':
                            Android.swipe(action.x, action.y, action.x2, action.y2, action.duration)
                        elif t == 'long_press':
                            Android.long_press(action.x, action.y, action.duration)
                        elif t == 'wait':
                            time.sleep(action.wait_sec)
                        elif t == 'script':
                            self.engine.run(action.script)
                        elif t == 'key':
                            Android.key(action.key_code)
                        elif t == 'text':
                            Android.type_text(action.text)
                        elif t == 'app':
                            Android.launch_app(action.app_pkg)
                        
                        if action.repeats > 1:
                            time.sleep(action.delay)
                
                if macro.loop and macro.is_running:
                    if macro.loop_count == 0 or macro.runs < macro.loop_count:
                        Clock.schedule_once(
                            lambda dt: threading.Thread(target=run_actions, daemon=True).start(),
                            macro.loop_delay
                        )
            
            threading.Thread(target=run_actions, daemon=True).start()
    
    def save(self):
        try:
            data = {'macros': [m.to_dict() for m in self.macros]}
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Save error: {e}")
    
    def load(self):
        try:
            if os.path.exists(SAVE_FILE):
                with open(SAVE_FILE, 'r') as f:
                    data = json.load(f)
                self.macros = [MacroData.from_dict(d) for d in data.get('macros', [])]
        except Exception as e:
            print(f"Load error: {e}")
    
    def on_pause(self):
        self.save()
        return True
    
    def on_stop(self):
        for m in self.macros:
            m.is_running = False
        self.engine.stop()
        self.save()


if __name__ == '__main__':
    MacroVisionApp().run()