"""
Macro Vision AI v3.0
Sistema completo de automacao com overlay e acessibilidade
"""

import os
import sys
import json
import time
import threading
import traceback
from io import StringIO

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform, get_color_from_hex
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty, ListProperty, BooleanProperty, ObjectProperty


# ============================================================
# TEMA E CORES
# ============================================================

class Colors:
    BG = get_color_from_hex('#08080f')
    BG_SECONDARY = get_color_from_hex('#0f0f1a')
    BG_CARD = get_color_from_hex('#151525')
    BG_CARD_LIGHT = get_color_from_hex('#1a1a30')
    
    PRIMARY = get_color_from_hex('#7c3aed')
    PRIMARY_DARK = get_color_from_hex('#5b21b6')
    PRIMARY_LIGHT = get_color_from_hex('#a78bfa')
    
    ACCENT = get_color_from_hex('#06b6d4')
    ACCENT_DARK = get_color_from_hex('#0891b2')
    
    SUCCESS = get_color_from_hex('#10b981')
    WARNING = get_color_from_hex('#f59e0b')
    DANGER = get_color_from_hex('#ef4444')
    
    TEXT = get_color_from_hex('#f1f5f9')
    TEXT_SECONDARY = get_color_from_hex('#94a3b8')
    TEXT_MUTED = get_color_from_hex('#475569')
    
    OVERLAY = (0.05, 0.05, 0.1, 0.95)


# ============================================================
# ANDROID HELPERS
# ============================================================

class AndroidHelper:
    """Funcoes de integracao com Android"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.is_android = platform == 'android'
        
        if self.is_android:
            try:
                from jnius import autoclass
                
                self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
                self.Context = autoclass('android.content.Context')
                self.Intent = autoclass('android.content.Intent')
                self.Settings = autoclass('android.provider.Settings')
                self.Uri = autoclass('android.net.Uri')
                self.Build = autoclass('android.os.Build')
                self.PowerManager = autoclass('android.os.PowerManager')
                self.WindowManager = autoclass('android.view.WindowManager')
                self.LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
                self.View = autoclass('android.view.View')
                self.TextView = autoclass('android.widget.TextView')
                self.Button = autoclass('android.widget.Button')
                self.LinearLayout = autoclass('android.widget.LinearLayout')
                self.Gravity = autoclass('android.view.Gravity')
                self.PixelFormat = autoclass('android.graphics.PixelFormat')
                self.Toast = autoclass('android.widget.Toast')
                self.NotificationChannel = None
                self.NotificationManager = None
                
                if self.Build.VERSION.SDK_INT >= 26:
                    self.NotificationChannel = autoclass('android.app.NotificationChannel')
                    self.NotificationManager = autoclass('android.app.NotificationManager')
                
                self.activity = self.PythonActivity.mActivity
                
            except Exception as e:
                print(f"Erro ao inicializar Android: {e}")
    
    def request_overlay_permission(self):
        """Solicita permissao de overlay"""
        if not self.is_android:
            return True
        
        try:
            if not self.Settings.canDrawOverlays(self.activity):
                intent = self.Intent(
                    self.Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    self.Uri.parse(f"package:{self.activity.getPackageName()}")
                )
                self.activity.startActivity(intent)
                return False
            return True
        except Exception as e:
            print(f"Erro overlay permission: {e}")
            return False
    
    def has_overlay_permission(self):
        """Verifica permissao de overlay"""
        if not self.is_android:
            return True
        try:
            return self.Settings.canDrawOverlays(self.activity)
        except:
            return False
    
    def request_accessibility_permission(self):
        """Abre configuracoes de acessibilidade"""
        if not self.is_android:
            return
        
        try:
            intent = self.Intent(self.Settings.ACTION_ACCESSIBILITY_SETTINGS)
            self.activity.startActivity(intent)
        except Exception as e:
            print(f"Erro accessibility: {e}")
    
    def request_write_settings_permission(self):
        """Solicita permissao para modificar configuracoes"""
        if not self.is_android:
            return True
        
        try:
            if not self.Settings.System.canWrite(self.activity):
                intent = self.Intent(
                    self.Settings.ACTION_MANAGE_WRITE_SETTINGS,
                    self.Uri.parse(f"package:{self.activity.getPackageName()}")
                )
                self.activity.startActivity(intent)
                return False
            return True
        except:
            return False
    
    def show_toast(self, message):
        """Mostra toast"""
        if not self.is_android:
            print(f"TOAST: {message}")
            return
        
        try:
            from android.runnable import run_on_ui_thread
            
            @run_on_ui_thread
            def _show():
                self.Toast.makeText(self.activity, message, self.Toast.LENGTH_SHORT).show()
            
            _show()
        except Exception as e:
            print(f"Toast error: {e}")
    
    def tap(self, x, y):
        """Executa toque na tela"""
        if self.is_android:
            os.system(f'input tap {x} {y}')
        return True
    
    def swipe(self, x1, y1, x2, y2, duration=300):
        """Executa swipe"""
        if self.is_android:
            os.system(f'input swipe {x1} {y1} {x2} {y2} {duration}')
        return True
    
    def long_press(self, x, y, duration=1000):
        """Toque longo"""
        if self.is_android:
            os.system(f'input swipe {x} {y} {x} {y} {duration}')
        return True
    
    def key_event(self, keycode):
        """Envia evento de tecla"""
        if self.is_android:
            os.system(f'input keyevent {keycode}')
        return True
    
    def text_input(self, text):
        """Digita texto"""
        if self.is_android:
            safe_text = text.replace(' ', '%s').replace("'", "\\'")
            os.system(f"input text '{safe_text}'")
        return True
    
    def screenshot(self, path='/sdcard/screenshot.png'):
        """Captura tela"""
        if self.is_android:
            os.system(f'screencap -p {path}')
        return path
    
    def get_screen_size(self):
        """Retorna tamanho da tela"""
        if self.is_android:
            try:
                wm = self.activity.getWindowManager()
                display = wm.getDefaultDisplay()
                from jnius import autoclass
                Point = autoclass('android.graphics.Point')
                size = Point()
                display.getSize(size)
                return (size.x, size.y)
            except:
                pass
        return (1080, 1920)
    
    def set_brightness(self, value):
        """Define brilho (0-255)"""
        if self.is_android:
            try:
                self.Settings.System.putInt(
                    self.activity.getContentResolver(),
                    self.Settings.System.SCREEN_BRIGHTNESS,
                    int(value)
                )
            except:
                pass
    
    def get_battery_level(self):
        """Retorna nivel da bateria"""
        if self.is_android:
            try:
                from jnius import autoclass
                BatteryManager = autoclass('android.os.BatteryManager')
                bm = self.activity.getSystemService(self.Context.BATTERY_SERVICE)
                return bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
            except:
                pass
        return 100
    
    def vibrate(self, duration=100):
        """Vibra o dispositivo"""
        if self.is_android:
            try:
                from jnius import autoclass
                Vibrator = autoclass('android.os.Vibrator')
                vibrator = self.activity.getSystemService(self.Context.VIBRATOR_SERVICE)
                vibrator.vibrate(duration)
            except:
                pass
    
    def launch_app(self, package_name):
        """Abre um aplicativo"""
        if self.is_android:
            try:
                pm = self.activity.getPackageManager()
                intent = pm.getLaunchIntentForPackage(package_name)
                if intent:
                    self.activity.startActivity(intent)
                    return True
            except:
                pass
        return False
    
    def go_home(self):
        """Vai para home"""
        self.key_event('KEYCODE_HOME')
    
    def go_back(self):
        """Pressiona voltar"""
        self.key_event('KEYCODE_BACK')
    
    def open_recents(self):
        """Abre apps recentes"""
        self.key_event('KEYCODE_APP_SWITCH')
    
    def open_notifications(self):
        """Abre painel de notificacoes"""
        if self.is_android:
            os.system('cmd statusbar expand-notifications')
    
    def open_quick_settings(self):
        """Abre configuracoes rapidas"""
        if self.is_android:
            os.system('cmd statusbar expand-settings')


# ============================================================
# CONFIGURACAO
# ============================================================

android = AndroidHelper()

if platform == 'android':
    from android.storage import app_storage_path
    DATA_DIR = app_storage_path()
else:
    DATA_DIR = os.path.expanduser('~/.macrovision')

os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, 'data.json')


# ============================================================
# WIDGETS CUSTOMIZADOS
# ============================================================

class RoundedButton(Button):
    """Botao com cantos arredondados e animacao"""
    
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        
        self._bg_color = bg_color or Colors.PRIMARY
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.color = Colors.TEXT
        self.bold = True
        
        with self.canvas.before:
            self._color_instruction = Color(*self._bg_color)
            self._rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size
    
    def on_press(self):
        anim = Animation(size=(self.width * 0.95, self.height * 0.95), duration=0.05)
        anim.start(self)
    
    def on_release(self):
        anim = Animation(size=(self.width / 0.95, self.height / 0.95), duration=0.05)
        anim.start(self)
    
    def set_color(self, color):
        self._bg_color = color
        self._color_instruction.rgba = color


class RoundedCard(BoxLayout):
    """Card com fundo arredondado"""
    
    def __init__(self, bg_color=None, radius=16, **kwargs):
        super().__init__(**kwargs)
        
        self._bg_color = bg_color or Colors.BG_CARD
        self._radius = dp(radius)
        
        with self.canvas.before:
            Color(*self._bg_color)
            self._rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self._radius]
            )
        
        self.bind(pos=self._update, size=self._update)
    
    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


class ModernInput(TextInput):
    """Campo de texto moderno"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.background_color = Colors.BG_CARD
        self.foreground_color = Colors.TEXT
        self.cursor_color = Colors.ACCENT
        self.hint_text_color = Colors.TEXT_MUTED
        self.padding = [dp(15), dp(12)]
        self.font_size = dp(14)


class TabButton(RoundedButton):
    """Botao de aba"""
    
    active = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._update_style()
        self.bind(active=lambda *a: self._update_style())
    
    def _update_style(self):
        if self.active:
            self.set_color(Colors.PRIMARY)
        else:
            self.set_color(Colors.BG_CARD)


# ============================================================
# SCRIPT ENGINE
# ============================================================

class ScriptEngine:
    """Motor de execucao de scripts Python com tags"""
    
    def __init__(self, app):
        self.app = app
        self.output = StringIO()
        self.running = False
        self.tags = {}
        self._stop = False
        
        # Funcoes disponiveis nos scripts
        self.api = {
            # Toque e gestos
            'tap': self._tap,
            'toque': self._tap,
            'swipe': self._swipe,
            'arrastar': self._swipe,
            'long_press': self._long_press,
            'segurar': self._long_press,
            
            # Tempo
            'wait': self._wait,
            'esperar': self._wait,
            'sleep': self._wait,
            
            # Texto
            'digitar': self._type_text,
            'type_text': self._type_text,
            
            # Sistema
            'screenshot': self._screenshot,
            'capturar': self._screenshot,
            'home': self._home,
            'voltar': self._back,
            'back': self._back,
            'recentes': self._recents,
            'notificacoes': self._notifications,
            
            # Dispositivo
            'brilho': self._brightness,
            'vibrar': self._vibrate,
            'bateria': self._battery,
            'tela': self._screen_size,
            
            # Apps
            'abrir_app': self._launch_app,
            'launch': self._launch_app,
            
            # Utilidades
            'log': self._log,
            'print': self._log,
            'toast': self._toast,
            'aleatorio': self._random,
            'random': self._random,
            
            # Loop e controle
            'repetir': self._repeat,
            'repeat': self._repeat,
            'loop': self._loop,
            'parar': self._stop_script,
            'stop': self._stop_script,
            
            # Tags
            'definir_tag': self._set_tag,
            'set_tag': self._set_tag,
            'tag': self._get_tag,
            'get_tag': self._get_tag,
            'tags': self._get_all_tags,
            
            # Arquivos
            'ler': self._read_file,
            'read': self._read_file,
            'escrever': self._write_file,
            'write': self._write_file,
            
            # HTTP
            'http_get': self._http_get,
            'http_post': self._http_post,
            
            # Condicoes
            'se_bateria_menor': self._if_battery_less,
            'se_bateria_maior': self._if_battery_more,
            
            # Modulos
            'time': time,
            'os': os,
            'json': json,
        }
    
    # === TOQUE E GESTOS ===
    
    def _tap(self, x, y):
        """Toca na posicao"""
        android.tap(x, y)
        self._log(f"Toque em ({x}, {y})")
        return True
    
    def _swipe(self, x1, y1, x2, y2, duracao=300):
        """Arrasta na tela"""
        android.swipe(x1, y1, x2, y2, duracao)
        self._log(f"Swipe ({x1},{y1}) para ({x2},{y2})")
        return True
    
    def _long_press(self, x, y, duracao=1000):
        """Toque longo"""
        android.long_press(x, y, duracao)
        self._log(f"Toque longo em ({x}, {y})")
        return True
    
    # === TEMPO ===
    
    def _wait(self, segundos):
        """Espera X segundos"""
        time.sleep(segundos)
        return True
    
    # === TEXTO ===
    
    def _type_text(self, texto):
        """Digita texto"""
        android.text_input(texto)
        self._log(f"Digitou: {texto[:20]}...")
        return True
    
    # === SISTEMA ===
    
    def _screenshot(self, caminho=None):
        """Captura tela"""
        path = caminho or os.path.join(DATA_DIR, f'screen_{int(time.time())}.png')
        android.screenshot(path)
        self._log(f"Screenshot: {path}")
        return path
    
    def _home(self):
        """Vai para home"""
        android.go_home()
        self._log("Home")
        return True
    
    def _back(self):
        """Volta"""
        android.go_back()
        self._log("Voltar")
        return True
    
    def _recents(self):
        """Apps recentes"""
        android.open_recents()
        self._log("Recentes")
        return True
    
    def _notifications(self):
        """Abre notificacoes"""
        android.open_notifications()
        self._log("Notificacoes")
        return True
    
    # === DISPOSITIVO ===
    
    def _brightness(self, valor):
        """Define brilho (0-255)"""
        android.set_brightness(valor)
        self._log(f"Brilho: {valor}")
        return True
    
    def _vibrate(self, ms=100):
        """Vibra"""
        android.vibrate(ms)
        return True
    
    def _battery(self):
        """Retorna nivel da bateria"""
        level = android.get_battery_level()
        self._log(f"Bateria: {level}%")
        return level
    
    def _screen_size(self):
        """Retorna tamanho da tela"""
        return android.get_screen_size()
    
    # === APPS ===
    
    def _launch_app(self, pacote):
        """Abre aplicativo"""
        result = android.launch_app(pacote)
        self._log(f"Abrir app: {pacote}")
        return result
    
    # === UTILIDADES ===
    
    def _log(self, mensagem):
        """Loga mensagem"""
        timestamp = time.strftime('%H:%M:%S')
        line = f"[{timestamp}] {mensagem}\n"
        self.output.write(line)
        print(line, end='')
    
    def _toast(self, mensagem):
        """Mostra toast"""
        android.show_toast(mensagem)
        return True
    
    def _random(self, min_val, max_val):
        """Numero aleatorio"""
        import random
        if isinstance(min_val, int) and isinstance(max_val, int):
            return random.randint(min_val, max_val)
        return random.uniform(min_val, max_val)
    
    # === LOOP E CONTROLE ===
    
    def _repeat(self, funcao, vezes, intervalo=0):
        """Repete funcao"""
        for i in range(vezes):
            if self._stop:
                break
            funcao()
            if intervalo > 0 and i < vezes - 1:
                time.sleep(intervalo)
    
    def _loop(self, funcao, intervalo=1):
        """Loop infinito"""
        while not self._stop:
            funcao()
            time.sleep(intervalo)
    
    def _stop_script(self):
        """Para execucao"""
        self._stop = True
    
    # === TAGS ===
    
    def _set_tag(self, nome, valor):
        """Define uma tag"""
        self.tags[nome] = valor
        self._log(f"Tag '{nome}' = {valor}")
        return True
    
    def _get_tag(self, nome, padrao=None):
        """Obtem valor de tag"""
        return self.tags.get(nome, padrao)
    
    def _get_all_tags(self):
        """Retorna todas as tags"""
        return self.tags.copy()
    
    # === ARQUIVOS ===
    
    def _read_file(self, caminho):
        """Le arquivo"""
        try:
            with open(caminho, 'r') as f:
                return f.read()
        except:
            return None
    
    def _write_file(self, caminho, conteudo):
        """Escreve arquivo"""
        try:
            with open(caminho, 'w') as f:
                f.write(conteudo)
            return True
        except:
            return False
    
    # === HTTP ===
    
    def _http_get(self, url):
        """GET request"""
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=10) as r:
                return r.read().decode()
        except:
            return None
    
    def _http_post(self, url, dados):
        """POST request"""
        try:
            import urllib.request
            data = json.dumps(dados).encode()
            req = urllib.request.Request(url, data=data)
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.read().decode()
        except:
            return None
    
    # === CONDICOES ===
    
    def _if_battery_less(self, nivel, funcao):
        """Executa se bateria menor que"""
        if self._battery() < nivel:
            funcao()
    
    def _if_battery_more(self, nivel, funcao):
        """Executa se bateria maior que"""
        if self._battery() > nivel:
            funcao()
    
    # === EXECUCAO ===
    
    def execute(self, code, callback=None):
        """Executa codigo"""
        self.output = StringIO()
        self._stop = False
        self.running = True
        
        def run():
            try:
                exec(code, self.api.copy())
                result = {
                    'success': True,
                    'output': self.output.getvalue()
                }
            except Exception as e:
                result = {
                    'success': False,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
            
            self.running = False
            
            if callback:
                Clock.schedule_once(lambda dt: callback(result))
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Para execucao"""
        self._stop = True


# ============================================================
# OVERLAY FLUTUANTE
# ============================================================

class OverlayWidget(FloatLayout):
    """Widget de overlay flutuante"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.visible = False
        self.minimized = False
        
        with self.canvas.before:
            Color(*Colors.OVERLAY)
            self._bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)]
            )
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self._build_ui()
    
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
    
    def _build_ui(self):
        # Container principal
        main = BoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(8)
        )
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(40))
        
        title = Label(
            text='Macro Vision',
            font_size=dp(14),
            bold=True,
            color=Colors.TEXT,
            size_hint_x=0.6
        )
        header.add_widget(title)
        
        min_btn = RoundedButton(
            text='-',
            size_hint=(None, 1),
            width=dp(35),
            bg_color=Colors.WARNING,
            font_size=dp(16)
        )
        min_btn.bind(on_release=lambda x: self.toggle_minimize())
        header.add_widget(min_btn)
        
        close_btn = RoundedButton(
            text='X',
            size_hint=(None, 1),
            width=dp(35),
            bg_color=Colors.DANGER,
            font_size=dp(14)
        )
        close_btn.bind(on_release=lambda x: self.hide())
        header.add_widget(close_btn)
        
        main.add_widget(header)
        
        # Content (pode ser minimizado)
        self.content = BoxLayout(orientation='vertical', spacing=dp(8))
        
        # Status
        self.status_label = Label(
            text='Pronto',
            font_size=dp(12),
            color=Colors.ACCENT,
            size_hint_y=None,
            height=dp(25)
        )
        self.content.add_widget(self.status_label)
        
        # Botoes de acao rapida
        quick_btns = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(45))
        
        tap_btn = RoundedButton(
            text='Tap',
            bg_color=Colors.PRIMARY,
            font_size=dp(11)
        )
        tap_btn.bind(on_release=lambda x: self._quick_tap())
        quick_btns.add_widget(tap_btn)
        
        swipe_btn = RoundedButton(
            text='Swipe',
            bg_color=Colors.ACCENT,
            font_size=dp(11)
        )
        swipe_btn.bind(on_release=lambda x: self._quick_swipe())
        quick_btns.add_widget(swipe_btn)
        
        ss_btn = RoundedButton(
            text='Foto',
            bg_color=Colors.SUCCESS,
            font_size=dp(11)
        )
        ss_btn.bind(on_release=lambda x: self._quick_screenshot())
        quick_btns.add_widget(ss_btn)
        
        self.content.add_widget(quick_btns)
        
        # Macro rapido
        macro_btns = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(40))
        
        self.macro_spinner = Spinner(
            text='Selecionar Macro',
            values=[],
            size_hint_x=0.6,
            font_size=dp(11)
        )
        macro_btns.add_widget(self.macro_spinner)
        
        run_btn = RoundedButton(
            text='Executar',
            size_hint_x=0.4,
            bg_color=Colors.SUCCESS,
            font_size=dp(11)
        )
        run_btn.bind(on_release=lambda x: self._run_selected_macro())
        macro_btns.add_widget(run_btn)
        
        self.content.add_widget(macro_btns)
        
        main.add_widget(self.content)
        self.add_widget(main)
    
    def show(self):
        """Mostra overlay"""
        self.visible = True
        self.opacity = 0
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self)
        self._update_macros()
    
    def hide(self):
        """Esconde overlay"""
        def _hide(*args):
            self.visible = False
        
        anim = Animation(opacity=0, duration=0.2)
        anim.bind(on_complete=_hide)
        anim.start(self)
    
    def toggle_minimize(self):
        """Minimiza/expande"""
        self.minimized = not self.minimized
        if self.minimized:
            self.content.opacity = 0
            self.content.disabled = True
            anim = Animation(height=dp(50), duration=0.2)
        else:
            self.content.opacity = 1
            self.content.disabled = False
            anim = Animation(height=dp(200), duration=0.2)
        anim.start(self)
    
    def _update_macros(self):
        """Atualiza lista de macros"""
        self.macro_spinner.values = [m.name for m in self.app.macros]
    
    def _quick_tap(self):
        """Tap rapido no centro"""
        w, h = android.get_screen_size()
        android.tap(w // 2, h // 2)
        self.status_label.text = f'Tap em ({w//2}, {h//2})'
    
    def _quick_swipe(self):
        """Swipe rapido para cima"""
        w, h = android.get_screen_size()
        android.swipe(w // 2, h * 0.7, w // 2, h * 0.3, 300)
        self.status_label.text = 'Swipe para cima'
    
    def _quick_screenshot(self):
        """Screenshot rapido"""
        path = android.screenshot()
        self.status_label.text = f'Salvo: {os.path.basename(path)}'
    
    def _run_selected_macro(self):
        """Executa macro selecionado"""
        name = self.macro_spinner.text
        for macro in self.app.macros:
            if macro.name == name:
                self.app.execute_macro(macro)
                self.status_label.text = f'Executando: {name}'
                break


# ============================================================
# MODELOS DE DADOS
# ============================================================

class MacroAction:
    """Uma acao do macro"""
    
    TYPES = [
        ('tap', 'Toque'),
        ('swipe', 'Arrastar'),
        ('long_press', 'Segurar'),
        ('wait', 'Esperar'),
        ('script', 'Codigo Python'),
        ('key', 'Tecla'),
        ('text', 'Digitar'),
        ('app', 'Abrir App'),
    ]
    
    def __init__(self):
        self.type = 'tap'
        self.name = 'Nova Acao'
        self.enabled = True
        self.x = 500
        self.y = 800
        self.x2 = 500
        self.y2 = 400
        self.duration = 300
        self.wait_time = 1.0
        self.script_code = ''
        self.key_code = 'KEYCODE_BACK'
        self.text = ''
        self.app_package = ''
        self.repeat = 1
        self.repeat_delay = 0.5
    
    def to_dict(self):
        return self.__dict__.copy()
    
    @staticmethod
    def from_dict(d):
        a = MacroAction()
        for k, v in d.items():
            if hasattr(a, k):
                setattr(a, k, v)
        return a


class Macro:
    """Um macro com acoes e codigo"""
    
    def __init__(self, name='Novo Macro'):
        self.id = int(time.time() * 1000)
        self.name = name
        self.description = ''
        self.actions = []
        self.script = ''  # Codigo Python do macro
        self.tags = {}  # Tags personalizadas
        self.is_running = False
        self.loop = False
        self.loop_count = 0
        self.loop_delay = 1.0
        self.created_at = time.strftime('%d/%m/%Y %H:%M')
        self.run_count = 0
    
    def get_default_script(self):
        return '''# Codigo Python do Macro
# 
# FUNCOES DISPONIVEIS:
#
# TOQUES:
#   tap(x, y)              - Toca na posicao
#   swipe(x1, y1, x2, y2)  - Arrasta
#   long_press(x, y)       - Toque longo
#   digitar("texto")       - Digita texto
#
# TEMPO:
#   esperar(segundos)      - Aguarda
#
# SISTEMA:
#   home()                 - Vai para home
#   voltar()               - Pressiona voltar
#   screenshot()           - Captura tela
#   abrir_app("pacote")    - Abre aplicativo
#
# DISPOSITIVO:
#   brilho(0-255)          - Define brilho
#   vibrar(ms)             - Vibra
#   bateria()              - Retorna nivel
#
# TAGS (variaveis salvas):
#   definir_tag("nome", valor)
#   tag("nome")
#
# UTILIDADES:
#   log("mensagem")        - Registra log
#   toast("mensagem")      - Mostra notificacao
#   aleatorio(min, max)    - Numero aleatorio
#
# LOOPS:
#   repetir(funcao, vezes, intervalo)
#   loop(funcao, intervalo)  # Infinito
#   parar()                  # Para execucao
#
# EXEMPLO:
log("Iniciando macro...")
esperar(1)

for i in range(3):
    tap(500, 800)
    esperar(0.5)
    log(f"Toque {i + 1}")

toast("Macro finalizado!")
'''
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'actions': [a.to_dict() for a in self.actions],
            'script': self.script,
            'tags': self.tags,
            'loop': self.loop,
            'loop_count': self.loop_count,
            'loop_delay': self.loop_delay,
            'created_at': self.created_at,
            'run_count': self.run_count,
        }
    
    @staticmethod
    def from_dict(d):
        m = Macro(d.get('name', 'Macro'))
        m.id = d.get('id', m.id)
        m.description = d.get('description', '')
        m.script = d.get('script', '')
        m.tags = d.get('tags', {})
        m.loop = d.get('loop', False)
        m.loop_count = d.get('loop_count', 0)
        m.loop_delay = d.get('loop_delay', 1.0)
        m.created_at = d.get('created_at', '')
        m.run_count = d.get('run_count', 0)
        m.actions = [MacroAction.from_dict(a) for a in d.get('actions', [])]
        return m


# ============================================================
# TELAS
# ============================================================

class HeaderWidget(BoxLayout):
    """Header da tela"""
    
    def __init__(self, title='', show_back=False, back_callback=None, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(15), dp(10)],
            spacing=dp(10),
            **kwargs
        )
        
        with self.canvas.before:
            Color(*Colors.BG_SECONDARY)
            self._rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[0, 0, dp(20), dp(20)]
            )
        self.bind(pos=self._update, size=self._update)
        
        if show_back:
            back = RoundedButton(
                text='Voltar',
                size_hint=(None, 1),
                width=dp(80),
                bg_color=Colors.BG_CARD,
                font_size=dp(13)
            )
            back.bind(on_release=lambda x: back_callback() if back_callback else None)
            self.add_widget(back)
        
        self.add_widget(Label(
            text=title,
            font_size=dp(18),
            bold=True,
            color=Colors.TEXT
        ))
        
        if show_back:
            self.add_widget(Widget(size_hint=(None, 1), width=dp(80)))
    
    def _update(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size


class ActionEditScreen(BoxLayout):
    """Tela de edicao de acao"""
    
    def __init__(self, action, macro, app, is_new=False, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        self.action = action
        self.macro = macro
        self.app = app
        self.is_new = is_new
        
        with self.canvas.before:
            Color(*Colors.BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Header
        self.add_widget(HeaderWidget(
            title='Nova Acao' if is_new else 'Editar Acao',
            show_back=True,
            back_callback=lambda: app.open_macro(macro)
        ))
        
        # Content
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(12),
            padding=dp(15)
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Nome
        content.add_widget(self._label('Nome'))
        self.name_input = ModernInput(
            text=action.name,
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(self.name_input)
        
        # Tipo
        content.add_widget(self._label('Tipo de Acao'))
        self.type_spinner = Spinner(
            text=dict(MacroAction.TYPES).get(action.type, action.type),
            values=[t[1] for t in MacroAction.TYPES],
            size_hint_y=None,
            height=dp(45),
            background_color=Colors.BG_CARD,
            color=Colors.TEXT
        )
        self.type_spinner.bind(text=self._on_type_change)
        content.add_widget(self.type_spinner)
        
        # Container de opcoes (muda com tipo)
        self.options_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10)
        )
        self.options_box.bind(minimum_height=self.options_box.setter('height'))
        content.add_widget(self.options_box)
        
        # Repeticao
        content.add_widget(self._label('Repeticao'))
        repeat_box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        repeat_box.add_widget(Label(text='Repetir:', color=Colors.TEXT_SECONDARY, size_hint_x=0.3))
        self.repeat_input = ModernInput(
            text=str(action.repeat),
            input_filter='int',
            multiline=False,
            size_hint_x=0.3
        )
        repeat_box.add_widget(self.repeat_input)
        repeat_box.add_widget(Label(text='vezes', color=Colors.TEXT_SECONDARY, size_hint_x=0.2))
        content.add_widget(repeat_box)
        
        scroll.add_widget(content)
        self.add_widget(scroll)
        
        # Footer
        footer = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(15), spacing=dp(15))
        
        cancel = RoundedButton(text='Cancelar', bg_color=Colors.BG_CARD)
        cancel.bind(on_release=lambda x: app.open_macro(macro))
        footer.add_widget(cancel)
        
        save = RoundedButton(text='Salvar', bg_color=Colors.SUCCESS)
        save.bind(on_release=lambda x: self._save())
        footer.add_widget(save)
        
        self.add_widget(footer)
        
        self._build_options()
    
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
    
    def _label(self, text):
        return Label(
            text=text,
            font_size=dp(13),
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
    
    def _on_type_change(self, spinner, text):
        # Mapear texto para tipo
        for t_id, t_name in MacroAction.TYPES:
            if t_name == text:
                self.action.type = t_id
                break
        self._build_options()
    
    def _build_options(self):
        self.options_box.clear_widgets()
        t = self.action.type
        
        if t in ['tap', 'long_press']:
            self._add_coords('Posicao')
            if t == 'long_press':
                self._add_duration()
        
        elif t == 'swipe':
            self._add_coords('Inicio', '')
            self._add_coords('Fim', '2')
            self._add_duration()
        
        elif t == 'wait':
            self._add_wait()
        
        elif t == 'script':
            self._add_script()
        
        elif t == 'key':
            self._add_key()
        
        elif t == 'text':
            self._add_text()
        
        elif t == 'app':
            self._add_app()
    
    def _add_coords(self, label, suffix=''):
        self.options_box.add_widget(self._label(label))
        
        box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        box.add_widget(Label(text='X:', color=Colors.TEXT, size_hint_x=0.1))
        
        x_input = ModernInput(
            text=str(getattr(self.action, f'x{suffix}', 500)),
            input_filter='int',
            multiline=False,
            size_hint_x=0.35
        )
        setattr(self, f'x{suffix}_input', x_input)
        box.add_widget(x_input)
        
        box.add_widget(Label(text='Y:', color=Colors.TEXT, size_hint_x=0.1))
        
        y_input = ModernInput(
            text=str(getattr(self.action, f'y{suffix}', 800)),
            input_filter='int',
            multiline=False,
            size_hint_x=0.35
        )
        setattr(self, f'y{suffix}_input', y_input)
        box.add_widget(y_input)
        
        self.options_box.add_widget(box)
        
        # Capturar coords
        cap_btn = RoundedButton(
            text='Tocar para capturar coordenadas',
            size_hint_y=None,
            height=dp(40),
            bg_color=Colors.PRIMARY
        )
        cap_btn.bind(on_release=lambda x: self._capture_coords(suffix))
        self.options_box.add_widget(cap_btn)
    
    def _add_duration(self):
        self.options_box.add_widget(self._label('Duracao (ms)'))
        self.duration_input = ModernInput(
            text=str(self.action.duration),
            input_filter='int',
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        self.options_box.add_widget(self.duration_input)
    
    def _add_wait(self):
        self.options_box.add_widget(self._label('Tempo (segundos)'))
        self.wait_input = ModernInput(
            text=str(self.action.wait_time),
            input_filter='float',
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        self.options_box.add_widget(self.wait_input)
    
    def _add_script(self):
        self.options_box.add_widget(self._label('Codigo Python'))
        self.script_input = ModernInput(
            text=self.action.script_code or '# Seu codigo aqui\ntap(500, 800)',
            multiline=True,
            size_hint_y=None,
            height=dp(150)
        )
        self.options_box.add_widget(self.script_input)
    
    def _add_key(self):
        self.options_box.add_widget(self._label('Tecla'))
        self.key_spinner = Spinner(
            text=self.action.key_code,
            values=[
                'KEYCODE_BACK', 'KEYCODE_HOME', 'KEYCODE_APP_SWITCH',
                'KEYCODE_VOLUME_UP', 'KEYCODE_VOLUME_DOWN', 'KEYCODE_POWER',
                'KEYCODE_ENTER', 'KEYCODE_TAB', 'KEYCODE_SPACE',
                'KEYCODE_MENU', 'KEYCODE_SEARCH', 'KEYCODE_CAMERA'
            ],
            size_hint_y=None,
            height=dp(45)
        )
        self.options_box.add_widget(self.key_spinner)
    
    def _add_text(self):
        self.options_box.add_widget(self._label('Texto para digitar'))
        self.text_input = ModernInput(
            text=self.action.text,
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        self.options_box.add_widget(self.text_input)
    
    def _add_app(self):
        self.options_box.add_widget(self._label('Pacote do App'))
        self.app_input = ModernInput(
            text=self.action.app_package,
            hint_text='com.exemplo.app',
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        self.options_box.add_widget(self.app_input)
    
    def _capture_coords(self, suffix):
        content = BoxLayout(orientation='vertical', padding=dp(30))
        content.add_widget(Label(
            text='Toque em qualquer lugar\npara capturar a posicao',
            halign='center',
            font_size=dp(16),
            color=Colors.TEXT
        ))
        
        popup = Popup(
            title='Capturar Coordenadas',
            content=content,
            size_hint=(0.9, 0.6)
        )
        
        def on_touch(instance, touch):
            x = int(touch.pos[0] * 2.5)
            y = int((Window.height - touch.pos[1]) * 2.5)
            
            x_inp = getattr(self, f'x{suffix}_input', None)
            y_inp = getattr(self, f'y{suffix}_input', None)
            
            if x_inp:
                x_inp.text = str(x)
            if y_inp:
                y_inp.text = str(y)
            
            popup.dismiss()
            return True
        
        content.bind(on_touch_down=on_touch)
        popup.open()
    
    def _save(self):
        self.action.name = self.name_input.text.strip() or 'Acao'
        
        try:
            self.action.repeat = int(self.repeat_input.text)
        except:
            pass
        
        t = self.action.type
        
        if t in ['tap', 'long_press']:
            try:
                self.action.x = int(self.x_input.text)
                self.action.y = int(self.y_input.text)
            except:
                pass
            if t == 'long_press' and hasattr(self, 'duration_input'):
                try:
                    self.action.duration = int(self.duration_input.text)
                except:
                    pass
        
        elif t == 'swipe':
            try:
                self.action.x = int(self.x_input.text)
                self.action.y = int(self.y_input.text)
                self.action.x2 = int(self.x2_input.text)
                self.action.y2 = int(self.y2_input.text)
                self.action.duration = int(self.duration_input.text)
            except:
                pass
        
        elif t == 'wait':
            try:
                self.action.wait_time = float(self.wait_input.text)
            except:
                pass
        
        elif t == 'script':
            self.action.script_code = self.script_input.text
        
        elif t == 'key':
            self.action.key_code = self.key_spinner.text
        
        elif t == 'text':
            self.action.text = self.text_input.text
        
        elif t == 'app':
            self.action.app_package = self.app_input.text
        
        if self.is_new:
            self.macro.actions.append(self.action)
        
        self.app.save_data()
        self.app.open_macro(self.macro)


class MacroScreen(BoxLayout):
    """Tela do macro com abas"""
    
    def __init__(self, macro, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        self.macro = macro
        self.app = app
        self._timer = None
        self._log_lines = []
        
        with self.canvas.before:
            Color(*Colors.BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Header
        self.add_widget(HeaderWidget(
            title=macro.name,
            show_back=True,
            back_callback=lambda: self._go_back()
        ))
        
        # Abas
        tab_bar = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(10), spacing=dp(8))
        
        self.tab_actions = TabButton(text='Acoes', active=True, font_size=dp(13))
        self.tab_actions.bind(on_release=lambda x: self._show_tab('actions'))
        tab_bar.add_widget(self.tab_actions)
        
        self.tab_code = TabButton(text='Codigo', font_size=dp(13))
        self.tab_code.bind(on_release=lambda x: self._show_tab('code'))
        tab_bar.add_widget(self.tab_code)
        
        self.tab_tags = TabButton(text='Tags', font_size=dp(13))
        self.tab_tags.bind(on_release=lambda x: self._show_tab('tags'))
        tab_bar.add_widget(self.tab_tags)
        
        self.tab_config = TabButton(text='Config', font_size=dp(13))
        self.tab_config.bind(on_release=lambda x: self._show_tab('config'))
        tab_bar.add_widget(self.tab_config)
        
        self.add_widget(tab_bar)
        
        # Container de conteudo
        self.content = BoxLayout()
        self.add_widget(self.content)
        
        # Footer
        footer = BoxLayout(size_hint_y=None, height=dp(65), padding=dp(10), spacing=dp(10))
        
        add_btn = RoundedButton(text='Adicionar Acao', bg_color=Colors.ACCENT, font_size=dp(13))
        add_btn.bind(on_release=lambda x: self._add_action())
        footer.add_widget(add_btn)
        
        self.run_btn = RoundedButton(
            text='Parar' if macro.is_running else 'Executar',
            bg_color=Colors.DANGER if macro.is_running else Colors.SUCCESS,
            font_size=dp(13)
        )
        self.run_btn.bind(on_release=lambda x: self._toggle_run())
        footer.add_widget(self.run_btn)
        
        self.add_widget(footer)
        
        self._show_tab('actions')
        
        self._log_update = Clock.schedule_interval(self._update_log, 1)
    
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
    
    def _show_tab(self, tab):
        # Reset tabs
        self.tab_actions.active = tab == 'actions'
        self.tab_code.active = tab == 'code'
        self.tab_tags.active = tab == 'tags'
        self.tab_config.active = tab == 'config'
        
        self.content.clear_widgets()
        
        if tab == 'actions':
            self._build_actions_tab()
        elif tab == 'code':
            self._build_code_tab()
        elif tab == 'tags':
            self._build_tags_tab()
        elif tab == 'config':
            self._build_config_tab()
    
    def _build_actions_tab(self):
        layout = BoxLayout(orientation='vertical')
        
        scroll = ScrollView()
        self.actions_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(8),
            padding=dp(10)
        )
        self.actions_list.bind(minimum_height=self.actions_list.setter('height'))
        
        if not self.macro.actions:
            self.actions_list.add_widget(Label(
                text='Nenhuma acao configurada\nClique em Adicionar Acao',
                color=Colors.TEXT_MUTED,
                size_hint_y=None,
                height=dp(80),
                halign='center'
            ))
        else:
            for i, action in enumerate(self.macro.actions):
                card = self._action_card(i, action)
                self.actions_list.add_widget(card)
        
        scroll.add_widget(self.actions_list)
        layout.add_widget(scroll)
        
        self.content.add_widget(layout)
    
    def _action_card(self, index, action):
        card = RoundedCard(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(70),
            padding=dp(12),
            spacing=dp(10)
        )
        
        # Indicador de status
        indicator = Widget(size_hint=(None, 1), width=dp(5))
        color = Colors.SUCCESS if action.enabled else Colors.DANGER
        with indicator.canvas:
            Color(*color)
            RoundedRectangle(pos=indicator.pos, size=indicator.size, radius=[dp(2)])
        card.add_widget(indicator)
        
        # Info
        info = BoxLayout(orientation='vertical', size_hint_x=0.5)
        
        name = Label(
            text=action.name,
            font_size=dp(14),
            bold=True,
            color=Colors.TEXT if action.enabled else Colors.TEXT_MUTED,
            halign='left'
        )
        name.bind(size=name.setter('text_size'))
        info.add_widget(name)
        
        type_name = dict(MacroAction.TYPES).get(action.type, action.type)
        detail = Label(
            text=type_name,
            font_size=dp(11),
            color=Colors.TEXT_SECONDARY,
            halign='left'
        )
        detail.bind(size=detail.setter('text_size'))
        info.add_widget(detail)
        
        card.add_widget(info)
        
        # Botoes
        btns = BoxLayout(size_hint_x=0.4, spacing=dp(6))
        
        toggle = RoundedButton(
            text='ON' if action.enabled else 'OFF',
            bg_color=Colors.SUCCESS if action.enabled else Colors.DANGER,
            font_size=dp(10),
            size_hint_x=0.3
        )
        toggle.bind(on_release=lambda x, a=action: self._toggle_action(a))
        btns.add_widget(toggle)
        
        edit = RoundedButton(
            text='Editar',
            bg_color=Colors.PRIMARY,
            font_size=dp(10),
            size_hint_x=0.4
        )
        edit.bind(on_release=lambda x, a=action: self.app.edit_action(self.macro, a))
        btns.add_widget(edit)
        
        delete = RoundedButton(
            text='X',
            bg_color=Colors.DANGER,
            font_size=dp(10),
            size_hint_x=0.2
        )
        delete.bind(on_release=lambda x, i=index: self._delete_action(i))
        btns.add_widget(delete)
        
        card.add_widget(btns)
        
        return card
    
    def _build_code_tab(self):
        """Aba de codigo Python"""
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Instrucoes
        layout.add_widget(Label(
            text='Codigo Python com funcoes de automacao',
            font_size=dp(12),
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(25)
        ))
        
        # Editor
        self.code_input = ModernInput(
            text=self.macro.script or self.macro.get_default_script(),
            multiline=True,
            font_size=dp(12)
        )
        layout.add_widget(self.code_input)
        
        # Output
        layout.add_widget(Label(
            text='Saida:',
            font_size=dp(12),
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(20)
        ))
        
        output_scroll = ScrollView(size_hint_y=0.25)
        self.output_label = Label(
            text='',
            font_size=dp(11),
            color=Colors.ACCENT,
            halign='left',
            valign='top',
            size_hint_y=None
        )
        self.output_label.bind(texture_size=lambda i, s: setattr(self.output_label, 'height', s[1]))
        output_scroll.add_widget(self.output_label)
        layout.add_widget(output_scroll)
        
        # Botoes
        btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        
        run_code = RoundedButton(text='Executar Codigo', bg_color=Colors.SUCCESS, font_size=dp(12))
        run_code.bind(on_release=lambda x: self._run_code())
        btns.add_widget(run_code)
        
        save_code = RoundedButton(text='Salvar', bg_color=Colors.PRIMARY, font_size=dp(12))
        save_code.bind(on_release=lambda x: self._save_code())
        btns.add_widget(save_code)
        
        help_btn = RoundedButton(text='Ajuda', bg_color=Colors.BG_CARD, font_size=dp(12))
        help_btn.bind(on_release=lambda x: self._show_help())
        btns.add_widget(help_btn)
        
        layout.add_widget(btns)
        
        self.content.add_widget(layout)
    
    def _build_tags_tab(self):
        """Aba de tags personalizadas"""
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Info
        layout.add_widget(Label(
            text='Tags sao variaveis que voce pode usar nos scripts',
            font_size=dp(12),
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(25)
        ))
        
        # Lista de tags
        scroll = ScrollView()
        self.tags_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(8)
        )
        self.tags_list.bind(minimum_height=self.tags_list.setter('height'))
        
        self._refresh_tags()
        
        scroll.add_widget(self.tags_list)
        layout.add_widget(scroll)
        
        # Nova tag
        new_box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(8))
        
        self.tag_name_input = ModernInput(
            hint_text='Nome',
            multiline=False,
            size_hint_x=0.35
        )
        new_box.add_widget(self.tag_name_input)
        
        self.tag_value_input = ModernInput(
            hint_text='Valor',
            multiline=False,
            size_hint_x=0.35
        )
        new_box.add_widget(self.tag_value_input)
        
        add_tag = RoundedButton(
            text='Adicionar',
            size_hint_x=0.3,
            bg_color=Colors.SUCCESS,
            font_size=dp(12)
        )
        add_tag.bind(on_release=lambda x: self._add_tag())
        new_box.add_widget(add_tag)
        
        layout.add_widget(new_box)
        
        self.content.add_widget(layout)
    
    def _refresh_tags(self):
        self.tags_list.clear_widgets()
        
        if not self.macro.tags:
            self.tags_list.add_widget(Label(
                text='Nenhuma tag definida',
                color=Colors.TEXT_MUTED,
                size_hint_y=None,
                height=dp(40)
            ))
        else:
            for name, value in self.macro.tags.items():
                row = RoundedCard(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(50),
                    padding=dp(10),
                    spacing=dp(10)
                )
                
                row.add_widget(Label(
                    text=f'{name}:',
                    color=Colors.ACCENT,
                    font_size=dp(13),
                    size_hint_x=0.3
                ))
                
                row.add_widget(Label(
                    text=str(value),
                    color=Colors.TEXT,
                    font_size=dp(13),
                    size_hint_x=0.5
                ))
                
                del_btn = RoundedButton(
                    text='X',
                    size_hint_x=0.2,
                    bg_color=Colors.DANGER,
                    font_size=dp(12)
                )
                del_btn.bind(on_release=lambda x, n=name: self._delete_tag(n))
                row.add_widget(del_btn)
                
                self.tags_list.add_widget(row)
    
    def _add_tag(self):
        name = self.tag_name_input.text.strip()
        value = self.tag_value_input.text.strip()
        
        if name:
            # Tentar converter para numero
            try:
                value = int(value)
            except:
                try:
                    value = float(value)
                except:
                    pass
            
            self.macro.tags[name] = value
            self.app.save_data()
            
            self.tag_name_input.text = ''
            self.tag_value_input.text = ''
            self._refresh_tags()
    
    def _delete_tag(self, name):
        if name in self.macro.tags:
            del self.macro.tags[name]
            self.app.save_data()
            self._refresh_tags()
    
    def _build_config_tab(self):
        """Aba de configuracoes"""
        scroll = ScrollView()
        layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(12),
            padding=dp(15)
        )
        layout.bind(minimum_height=layout.setter('height'))
        
        # Nome
        layout.add_widget(Label(
            text='Nome do Macro',
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(20)
        ))
        self.name_input = ModernInput(
            text=self.macro.name,
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        layout.add_widget(self.name_input)
        
        # Descricao
        layout.add_widget(Label(
            text='Descricao',
            color=Colors.TEXT_SECONDARY,
            size_hint_y=None,
            height=dp(20)
        ))
        self.desc_input = ModernInput(
            text=self.macro.description,
            multiline=True,
            size_hint_y=None,
            height=dp(70)
        )
        layout.add_widget(self.desc_input)
        
        # Loop
        loop_box = BoxLayout(size_hint_y=None, height=dp(45))
        loop_box.add_widget(Label(text='Repetir em loop', color=Colors.TEXT, size_hint_x=0.7))
        self.loop_switch = Switch(active=self.macro.loop, size_hint_x=0.3)
        loop_box.add_widget(self.loop_switch)
        layout.add_widget(loop_box)
        
        # Loop count
        count_box = BoxLayout(size_hint_y=None, height=dp(45))
        count_box.add_widget(Label(text='Repeticoes (0 = infinito):', color=Colors.TEXT, size_hint_x=0.6))
        self.loop_count_input = ModernInput(
            text=str(self.macro.loop_count),
            input_filter='int',
            multiline=False,
            size_hint_x=0.4
        )
        count_box.add_widget(self.loop_count_input)
        layout.add_widget(count_box)
        
        # Loop delay
        delay_box = BoxLayout(size_hint_y=None, height=dp(45))
        delay_box.add_widget(Label(text='Intervalo (seg):', color=Colors.TEXT, size_hint_x=0.6))
        self.loop_delay_input = ModernInput(
            text=str(self.macro.loop_delay),
            input_filter='float',
            multiline=False,
            size_hint_x=0.4
        )
        delay_box.add_widget(self.loop_delay_input)
        layout.add_widget(delay_box)
        
        # Permissoes
        layout.add_widget(Label(
            text='Permissoes do Sistema',
            color=Colors.ACCENT,
            size_hint_y=None,
            height=dp(30),
            halign='left'
        ))
        
        overlay_btn = RoundedButton(
            text='Solicitar Permissao de Overlay',
            size_hint_y=None,
            height=dp(45),
            bg_color=Colors.PRIMARY
        )
        overlay_btn.bind(on_release=lambda x: android.request_overlay_permission())
        layout.add_widget(overlay_btn)
        
        access_btn = RoundedButton(
            text='Configurar Acessibilidade',
            size_hint_y=None,
            height=dp(45),
            bg_color=Colors.PRIMARY
        )
        access_btn.bind(on_release=lambda x: android.request_accessibility_permission())
        layout.add_widget(access_btn)
        
        settings_btn = RoundedButton(
            text='Permitir Modificar Configuracoes',
            size_hint_y=None,
            height=dp(45),
            bg_color=Colors.PRIMARY
        )
        settings_btn.bind(on_release=lambda x: android.request_write_settings_permission())
        layout.add_widget(settings_btn)
        
        # Salvar
        save_btn = RoundedButton(
            text='Salvar Configuracoes',
            size_hint_y=None,
            height=dp(50),
            bg_color=Colors.SUCCESS
        )
        save_btn.bind(on_release=lambda x: self._save_config())
        layout.add_widget(save_btn)
        
        # Estatisticas
        layout.add_widget(Label(
            text=f'Criado em: {self.macro.created_at}\nExecutado: {self.macro.run_count} vezes',
            color=Colors.TEXT_MUTED,
            size_hint_y=None,
            height=dp(40)
        ))
        
        scroll.add_widget(layout)
        self.content.add_widget(scroll)
    
    def _add_action(self):
        self.app.edit_action(self.macro, MacroAction(), is_new=True)
    
    def _toggle_action(self, action):
        action.enabled = not action.enabled
        self.app.save_data()
        self._show_tab('actions')
    
    def _delete_action(self, index):
        if 0 <= index < len(self.macro.actions):
            self.macro.actions.pop(index)
            self.app.save_data()
            self._show_tab('actions')
    
    def _run_code(self):
        code = self.code_input.text
        self.output_label.text = 'Executando...\n'
        
        # Adicionar tags ao engine
        self.app.script_engine.tags = self.macro.tags.copy()
        
        def callback(result):
            if result['success']:
                self.output_label.text = result.get('output', 'Concluido!')
                # Salvar tags modificadas
                self.macro.tags.update(self.app.script_engine.tags)
                self.app.save_data()
            else:
                self.output_label.text = f"ERRO: {result['error']}\n\n{result.get('traceback', '')}"
        
        self.app.script_engine.execute(code, callback)
    
    def _save_code(self):
        self.macro.script = self.code_input.text
        self.app.save_data()
        android.show_toast('Codigo salvo!')
    
    def _save_config(self):
        self.macro.name = self.name_input.text.strip() or 'Macro'
        self.macro.description = self.desc_input.text.strip()
        self.macro.loop = self.loop_switch.active
        
        try:
            self.macro.loop_count = int(self.loop_count_input.text)
        except:
            pass
        
        try:
            self.macro.loop_delay = float(self.loop_delay_input.text)
        except:
            pass
        
        self.app.save_data()
        android.show_toast('Configuracoes salvas!')
    
    def _show_help(self):
        help_text = '''FUNCOES DISPONIVEIS

TOQUES:
  tap(x, y) - Toque simples
  swipe(x1,y1,x2,y2) - Arrastar
  long_press(x, y) - Toque longo
  digitar("texto") - Digita texto

TEMPO:
  esperar(segundos) - Aguarda
  
SISTEMA:
  home() - Ir para home
  voltar() - Botao voltar
  screenshot() - Capturar tela
  abrir_app("pacote") - Abrir app
  notificacoes() - Abrir painel

DISPOSITIVO:
  brilho(0-255) - Ajustar brilho
  vibrar(ms) - Vibrar
  bateria() - Nivel da bateria
  tela() - Tamanho da tela

TAGS:
  definir_tag("nome", valor)
  tag("nome") - Obter valor
  tags() - Todas as tags

UTILIDADES:
  log("msg") - Registrar log
  toast("msg") - Mostrar notificacao
  aleatorio(min, max) - Numero aleatorio

LOOPS:
  repetir(func, vezes, intervalo)
  loop(func, intervalo) - Infinito
  parar() - Parar execucao

CONDICOES:
  se_bateria_menor(nivel, func)
  se_bateria_maior(nivel, func)
'''
        
        scroll = ScrollView()
        label = Label(
            text=help_text,
            font_size=dp(12),
            color=Colors.TEXT,
            halign='left',
            valign='top',
            size_hint_y=None
        )
        label.bind(texture_size=lambda i, s: setattr(label, 'height', s[1] + dp(20)))
        label.bind(size=label.setter('text_size'))
        scroll.add_widget(label)
        
        popup = Popup(
            title='Ajuda - Funcoes Python',
            content=scroll,
            size_hint=(0.95, 0.85)
        )
        popup.open()
    
    def _toggle_run(self):
        if self.macro.is_running:
            self._stop_macro()
        else:
            self._start_macro()
    
    def _start_macro(self):
        self.macro.is_running = True
        self.macro.run_count += 1
        
        self.run_btn.text = 'Parar'
        self.run_btn.set_color(Colors.DANGER)
        
        self.app.save_data()
        self.app.execute_macro(self.macro)
    
    def _stop_macro(self):
        self.macro.is_running = False
        self.app.script_engine.stop()
        
        self.run_btn.text = 'Executar'
        self.run_btn.set_color(Colors.SUCCESS)
        
        if self._timer:
            self._timer.cancel()
            self._timer = None
    
    def _update_log(self, dt):
        pass
    
    def _go_back(self):
        if hasattr(self, '_log_update'):
            self._log_update.cancel()
        self.app.show_main()


class MainScreen(BoxLayout):
    """Tela principal"""
    
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        
        self.app = app
        
        with self.canvas.before:
            Color(*Colors.BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Header
        header = BoxLayout(
            size_hint_y=None,
            height=dp(100),
            padding=dp(20)
        )
        
        title_box = BoxLayout(orientation='vertical')
        title_box.add_widget(Label(
            text='Macro Vision AI',
            font_size=dp(26),
            bold=True,
            color=Colors.TEXT
        ))
        
        running = sum(1 for m in app.macros if m.is_running)
        status = f'{running} macro(s) em execucao' if running else 'Nenhum macro ativo'
        title_box.add_widget(Label(
            text=status,
            font_size=dp(13),
            color=Colors.ACCENT if running else Colors.TEXT_SECONDARY
        ))
        
        header.add_widget(title_box)
        
        # Botao overlay
        overlay_btn = RoundedButton(
            text='Overlay',
            size_hint=(None, None),
            size=(dp(70), dp(40)),
            bg_color=Colors.PRIMARY,
            font_size=dp(11)
        )
        overlay_btn.bind(on_release=lambda x: app.toggle_overlay())
        header.add_widget(overlay_btn)
        
        self.add_widget(header)
        
        # Lista de macros
        scroll = ScrollView()
        self.macro_list = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=dp(15)
        )
        self.macro_list.bind(minimum_height=self.macro_list.setter('height'))
        scroll.add_widget(self.macro_list)
        self.add_widget(scroll)
        
        # Footer
        footer = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(15), spacing=dp(15))
        
        new_btn = RoundedButton(text='Novo Macro', bg_color=Colors.SUCCESS, font_size=dp(14))
        new_btn.bind(on_release=lambda x: self._new_macro())
        footer.add_widget(new_btn)
        
        stop_btn = RoundedButton(text='Parar Todos', bg_color=Colors.DANGER, font_size=dp(14))
        stop_btn.bind(on_release=lambda x: self._stop_all())
        footer.add_widget(stop_btn)
        
        self.add_widget(footer)
        
        self._refresh()
    
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
    
    def _refresh(self):
        self.macro_list.clear_widgets()
        
        if not self.app.macros:
            self.macro_list.add_widget(Label(
                text='Nenhum macro criado\nClique em Novo Macro para comecar',
                color=Colors.TEXT_MUTED,
                size_hint_y=None,
                height=dp(100),
                halign='center'
            ))
        else:
            for macro in self.app.macros:
                card = self._macro_card(macro)
                self.macro_list.add_widget(card)
    
    def _macro_card(self, macro):
        card = RoundedCard(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(90),
            padding=dp(15),
            spacing=dp(12)
        )
        
        # Status
        status_color = Colors.SUCCESS if macro.is_running else Colors.DANGER
        status = Widget(size_hint=(None, 1), width=dp(8))
        with status.canvas:
            Color(*status_color)
            RoundedRectangle(pos=status.pos, size=status.size, radius=[dp(4)])
        card.add_widget(status)
        
        # Info
        info = BoxLayout(orientation='vertical', size_hint_x=0.5)
        
        info.add_widget(Label(
            text=macro.name,
            font_size=dp(15),
            bold=True,
            color=Colors.TEXT,
            halign='left'
        ))
        
        info.add_widget(Label(
            text=f'{len(macro.actions)} acoes | {len(macro.tags)} tags',
            font_size=dp(11),
            color=Colors.TEXT_SECONDARY,
            halign='left'
        ))
        
        info.add_widget(Label(
            text=f'Execucoes: {macro.run_count}',
            font_size=dp(10),
            color=Colors.ACCENT,
            halign='left'
        ))
        
        card.add_widget(info)
        
        # Botoes
        btns = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=dp(6))
        
        run_btn = RoundedButton(
            text='Parar' if macro.is_running else 'Executar',
            bg_color=Colors.DANGER if macro.is_running else Colors.SUCCESS,
            font_size=dp(11)
        )
        run_btn.bind(on_release=lambda x, m=macro: self._toggle_macro(m))
        btns.add_widget(run_btn)
        
        row = BoxLayout(spacing=dp(6))
        
        open_btn = RoundedButton(text='Abrir', bg_color=Colors.PRIMARY, font_size=dp(11))
        open_btn.bind(on_release=lambda x, m=macro: self.app.open_macro(m))
        row.add_widget(open_btn)
        
        del_btn = RoundedButton(text='X', bg_color=Colors.DANGER, font_size=dp(11), size_hint_x=0.3)
        del_btn.bind(on_release=lambda x, m=macro: self._delete_macro(m))
        row.add_widget(del_btn)
        
        btns.add_widget(row)
        card.add_widget(btns)
        
        return card
    
    def _new_macro(self):
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        content.add_widget(Label(
            text='Nome do macro:',
            color=Colors.TEXT,
            size_hint_y=None,
            height=dp(25)
        ))
        
        name_input = ModernInput(
            hint_text='Meu Macro',
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(name_input)
        
        popup = Popup(
            title='Novo Macro',
            content=content,
            size_hint=(0.85, 0.35)
        )
        
        btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        
        def create(x):
            name = name_input.text.strip() or f'Macro {len(self.app.macros) + 1}'
            macro = Macro(name)
            self.app.macros.append(macro)
            self.app.save_data()
            popup.dismiss()
            self.app.open_macro(macro)
        
        create_btn = RoundedButton(text='Criar', bg_color=Colors.SUCCESS)
        create_btn.bind(on_release=create)
        btns.add_widget(create_btn)
        
        cancel_btn = RoundedButton(text='Cancelar', bg_color=Colors.DANGER)
        cancel_btn.bind(on_release=popup.dismiss)
        btns.add_widget(cancel_btn)
        
        content.add_widget(btns)
        popup.open()
    
    def _toggle_macro(self, macro):
        macro.is_running = not macro.is_running
        if macro.is_running:
            macro.run_count += 1
            self.app.execute_macro(macro)
        else:
            self.app.script_engine.stop()
        self.app.save_data()
        self._refresh()
    
    def _delete_macro(self, macro):
        macro.is_running = False
        self.app.macros.remove(macro)
        self.app.save_data()
        self._refresh()
    
    def _stop_all(self):
        for m in self.app.macros:
            m.is_running = False
        self.app.script_engine.stop()
        self.app.save_data()
        self._refresh()


# ============================================================
# APP PRINCIPAL
# ============================================================

class MacroVisionApp(App):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.macros = []
        self.root_widget = None
        self.script_engine = None
        self.overlay = None
    
    def build(self):
        self.title = 'Macro Vision AI'
        Window.clearcolor = Colors.BG
        
        self.root_widget = FloatLayout()
        self.script_engine = ScriptEngine(self)
        
        # Container principal
        self.main_container = BoxLayout()
        self.root_widget.add_widget(self.main_container)
        
        # Overlay
        self.overlay = OverlayWidget(self)
        self.overlay.size_hint = (0.85, None)
        self.overlay.height = dp(200)
        self.overlay.pos_hint = {'center_x': 0.5, 'top': 0.95}
        self.overlay.opacity = 0
        self.root_widget.add_widget(self.overlay)
        
        self.load_data()
        self.show_main()
        
        if platform == 'android':
            self._request_permissions()
        
        return self.root_widget
    
    def _request_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.INTERNET,
            ])
        except:
            pass
    
    def show_main(self):
        self.main_container.clear_widgets()
        self.main_container.add_widget(MainScreen(self))
    
    def open_macro(self, macro):
        self.main_container.clear_widgets()
        self.main_container.add_widget(MacroScreen(macro, self))
    
    def edit_action(self, macro, action, is_new=False):
        self.main_container.clear_widgets()
        self.main_container.add_widget(ActionEditScreen(action, macro, self, is_new))
    
    def toggle_overlay(self):
        if self.overlay.visible:
            self.overlay.hide()
        else:
            if android.has_overlay_permission():
                self.overlay.show()
            else:
                android.request_overlay_permission()
    
    def execute_macro(self, macro):
        """Executa um macro"""
        # Se tem script, executa
        if macro.script:
            self.script_engine.tags = macro.tags.copy()
            
            def callback(result):
                macro.tags.update(self.script_engine.tags)
                self.save_data()
                
                if macro.loop and macro.is_running:
                    if macro.loop_count == 0 or macro.run_count < macro.loop_count:
                        Clock.schedule_once(
                            lambda dt: self.execute_macro(macro),
                            macro.loop_delay
                        )
            
            self.script_engine.execute(macro.script, callback)
        
        # Executa acoes
        elif macro.actions:
            self._execute_actions(macro)
    
    def _execute_actions(self, macro, loop_num=1):
        """Executa acoes do macro"""
        def run():
            for action in macro.actions:
                if not macro.is_running:
                    break
                if not action.enabled:
                    continue
                
                for _ in range(action.repeat):
                    if not macro.is_running:
                        break
                    
                    self._execute_action(action)
                    
                    if action.repeat > 1:
                        time.sleep(action.repeat_delay)
            
            # Loop
            if macro.is_running and macro.loop:
                if macro.loop_count == 0 or loop_num < macro.loop_count:
                    Clock.schedule_once(
                        lambda dt: self._execute_actions(macro, loop_num + 1),
                        macro.loop_delay
                    )
        
        threading.Thread(target=run, daemon=True).start()
    
    def _execute_action(self, action):
        """Executa uma acao"""
        t = action.type
        
        if t == 'tap':
            android.tap(action.x, action.y)
        
        elif t == 'swipe':
            android.swipe(action.x, action.y, action.x2, action.y2, action.duration)
        
        elif t == 'long_press':
            android.long_press(action.x, action.y, action.duration)
        
        elif t == 'wait':
            time.sleep(action.wait_time)
        
        elif t == 'script':
            if action.script_code:
                self.script_engine.execute(action.script_code)
        
        elif t == 'key':
            android.key_event(action.key_code)
        
        elif t == 'text':
            android.text_input(action.text)
        
        elif t == 'app':
            android.launch_app(action.app_package)
    
    def save_data(self):
        try:
            data = {'macros': [m.to_dict() for m in self.macros]}
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f'Erro salvando: {e}')
    
    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                self.macros = [Macro.from_dict(d) for d in data.get('macros', [])]
        except Exception as e:
            print(f'Erro carregando: {e}')
    
    def on_pause(self):
        self.save_data()
        return True
    
    def on_resume(self):
        pass
    
    def on_stop(self):
        for m in self.macros:
            m.is_running = False
        self.script_engine.stop()
        self.save_data()


if __name__ == '__main__':
    MacroVisionApp().run()