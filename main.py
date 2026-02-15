"""
Macro Vision AI v1.0
Versão simplificada sem PIL - usa apenas Kivy
"""

import os
import json
import time

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

# Arquivo de dados
if platform == 'android':
    from android.storage import app_storage_path
    DATA_FILE = os.path.join(app_storage_path(), 'macros.json')
else:
    DATA_FILE = 'macros.json'


class ActionExecutor:
    """Executa ações no dispositivo"""
    
    def __init__(self):
        self.is_android = platform == 'android'
        self.log = []
    
    def execute(self, action, x, y):
        """Executa ação nas coordenadas"""
        entry = {'time': time.strftime('%H:%M:%S'), 'action': action, 'x': x, 'y': y}
        
        try:
            if self.is_android:
                if action == 'tap':
                    os.system(f'input tap {x} {y}')
                elif action == 'swipe_up':
                    os.system(f'input swipe {x} {y} {x} {y-300} 300')
                elif action == 'swipe_down':
                    os.system(f'input swipe {x} {y} {x} {y+300} 300')
                elif action == 'swipe_left':
                    os.system(f'input swipe {x} {y} {x-300} {y} 300')
                elif action == 'swipe_right':
                    os.system(f'input swipe {x} {y} {x+300} {y} 300')
                elif action == 'long_press':
                    os.system(f'input swipe {x} {y} {x} {y} 1000')
                entry['result'] = 'OK'
            else:
                print(f"[{action}] ({x}, {y})")
                entry['result'] = 'Simulado'
        except Exception as e:
            entry['result'] = str(e)
        
        self.log.append(entry)
        if len(self.log) > 50:
            self.log = self.log[-50:]
        
        return entry


class MacroImage:
    """Uma imagem de referência"""
    
    def __init__(self, path, tag=None):
        self.path = path
        self.tag = tag or os.path.basename(path).split('.')[0][:15]
        self.prompt = ""
        self.action = "tap"
        self.target_x = 500
        self.target_y = 800
        self.enabled = True
        self.cooldown = 2.0
        self.last_exec = 0
        self.exec_count = 0
    
    def can_execute(self):
        if not self.enabled:
            return False
        return (time.time() - self.last_exec) >= self.cooldown
    
    def to_dict(self):
        return {
            'path': self.path,
            'tag': self.tag,
            'prompt': self.prompt,
            'action': self.action,
            'target_x': self.target_x,
            'target_y': self.target_y,
            'enabled': self.enabled,
            'cooldown': self.cooldown
        }
    
    @staticmethod
    def from_dict(d):
        m = MacroImage(d['path'], d.get('tag'))
        m.prompt = d.get('prompt', '')
        m.action = d.get('action', 'tap')
        m.target_x = d.get('target_x', 500)
        m.target_y = d.get('target_y', 800)
        m.enabled = d.get('enabled', True)
        m.cooldown = d.get('cooldown', 2.0)
        return m


class Macro:
    """Um macro contém imagens e configurações"""
    
    def __init__(self, name, mid):
        self.name = name
        self.id = mid
        self.images = []
        self.is_running = False
        self.interval = 2.0
        self.exec_count = 0
    
    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id,
            'images': [i.to_dict() for i in self.images],
            'interval': self.interval
        }
    
    @staticmethod
    def from_dict(d):
        m = Macro(d['name'], d['id'])
        m.interval = d.get('interval', 2.0)
        for img_d in d.get('images', []):
            try:
                m.images.append(MacroImage.from_dict(img_d))
            except:
                pass
        return m


class ImageConfigScreen(BoxLayout):
    """Tela de configuração de uma imagem"""
    
    def __init__(self, macro, img, app, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(8), **kwargs)
        self.macro = macro
        self.img = img
        self.app = app
        
        # Header
        h = BoxLayout(size_hint_y=None, height=dp(45))
        h.add_widget(Button(text='< Voltar', size_hint_x=0.3,
                           on_press=lambda x: app.open_macro(macro)))
        h.add_widget(Label(text=f'⚙ {img.tag}', bold=True))
        self.add_widget(h)
        
        # Scroll
        scroll = ScrollView()
        content = GridLayout(cols=1, size_hint_y=None, spacing=dp(10), padding=dp(5))
        content.bind(minimum_height=content.setter('height'))
        
        # Preview
        if os.path.exists(img.path):
            preview = Image(source=img.path, size_hint_y=None, height=dp(150))
            content.add_widget(preview)
        
        # TAG
        content.add_widget(Label(text='🏷 TAG:', size_hint_y=None, height=dp(25)))
        self.tag_input = TextInput(text=img.tag, multiline=False,
                                   size_hint_y=None, height=dp(40))
        content.add_widget(self.tag_input)
        
        # PROMPT
        content.add_widget(Label(text='📝 Descrição/Prompt:', size_hint_y=None, height=dp(25)))
        self.prompt_input = TextInput(
            text=img.prompt,
            hint_text='Ex: Botão de ataque, Ícone de loja...',
            multiline=True, size_hint_y=None, height=dp(70)
        )
        content.add_widget(self.prompt_input)
        
        # AÇÃO
        content.add_widget(Label(text='🎯 Ação:', size_hint_y=None, height=dp(25)))
        self.action_spinner = Spinner(
            text=img.action,
            values=['tap', 'swipe_up', 'swipe_down', 'swipe_left', 'swipe_right', 'long_press'],
            size_hint_y=None, height=dp(45)
        )
        content.add_widget(self.action_spinner)
        
        # COORDENADAS
        content.add_widget(Label(text='📍 Coordenadas do toque:', size_hint_y=None, height=dp(25)))
        
        coord_box = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        coord_box.add_widget(Label(text='X:', size_hint_x=0.15))
        self.x_input = TextInput(text=str(img.target_x), multiline=False,
                                 input_filter='int', size_hint_x=0.35)
        coord_box.add_widget(self.x_input)
        coord_box.add_widget(Label(text='Y:', size_hint_x=0.15))
        self.y_input = TextInput(text=str(img.target_y), multiline=False,
                                 input_filter='int', size_hint_x=0.35)
        coord_box.add_widget(self.y_input)
        content.add_widget(coord_box)
        
        # Botão para pegar coordenadas
        content.add_widget(Button(
            text='📱 Tocar na tela para capturar coordenadas',
            size_hint_y=None, height=dp(45),
            background_color=(0.3, 0.3, 0.6, 1),
            on_press=self.capture_coords
        ))
        
        # COOLDOWN
        cd_box = BoxLayout(size_hint_y=None, height=dp(45))
        cd_box.add_widget(Label(text='⏱ Cooldown (seg):', size_hint_x=0.6))
        self.cd_input = TextInput(text=str(img.cooldown), multiline=False,
                                  input_filter='float', size_hint_x=0.4)
        cd_box.add_widget(self.cd_input)
        content.add_widget(cd_box)
        
        # ATIVO
        active_box = BoxLayout(size_hint_y=None, height=dp(45))
        active_box.add_widget(Label(text='✅ Ativo:', size_hint_x=0.7))
        self.active_switch = Switch(active=img.enabled, size_hint_x=0.3)
        active_box.add_widget(self.active_switch)
        content.add_widget(active_box)
        
        # Stats
        content.add_widget(Label(
            text=f'📊 Execuções: {img.exec_count}',
            size_hint_y=None, height=dp(30),
            color=(0.5, 0.8, 0.5, 1)
        ))
        
        scroll.add_widget(content)
        self.add_widget(scroll)
        
        # Botão Salvar
        self.add_widget(Button(
            text='💾 SALVAR',
            size_hint_y=None, height=dp(55),
            background_color=(0, 0.7, 0.3, 1),
            on_press=self.save
        ))
    
    def capture_coords(self, inst):
        popup_content = BoxLayout(orientation='vertical', padding=dp(20))
        popup_content.add_widget(Label(
            text='Toque em qualquer lugar desta tela\npara capturar as coordenadas',
            halign='center'
        ))
        
        self.coord_popup = Popup(
            title='📍 Capturar Coordenadas',
            content=popup_content,
            size_hint=(0.9, 0.7)
        )
        
        def on_touch(instance, touch):
            if self.coord_popup.collide_point(*touch.pos):
                # Converter para coordenadas de tela reais
                x = int(touch.pos[0] * 2)  # Aproximação
                y = int((Window.height - touch.pos[1]) * 2)
                self.x_input.text = str(x)
                self.y_input.text = str(y)
                self.coord_popup.dismiss()
                return True
            return False
        
        popup_content.bind(on_touch_down=on_touch)
        self.coord_popup.open()
    
    def save(self, inst):
        self.img.tag = self.tag_input.text.strip() or self.img.tag
        self.img.prompt = self.prompt_input.text.strip()
        self.img.action = self.action_spinner.text
        self.img.enabled = self.active_switch.active
        
        try:
            self.img.target_x = int(self.x_input.text)
        except:
            pass
        try:
            self.img.target_y = int(self.y_input.text)
        except:
            pass
        try:
            self.img.cooldown = float(self.cd_input.text)
        except:
            pass
        
        self.app.save_data()
        
        popup = Popup(
            title='✅ Salvo!',
            content=Label(text=f'{self.img.tag}\n{self.img.action} em ({self.img.target_x}, {self.img.target_y})'),
            size_hint=(0.7, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)


class MacroScreen(BoxLayout):
    """Tela de um macro"""
    
    def __init__(self, macro, app, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(5), **kwargs)
        self.macro = macro
        self.app = app
        self.executor = ActionExecutor()
        self._timer = None
        
        # Header
        h = BoxLayout(size_hint_y=None, height=dp(50))
        h.add_widget(Button(text='< Voltar', size_hint_x=0.25,
                           on_press=lambda x: self.go_back()))
        h.add_widget(Label(text=f'🎯 {macro.name}', bold=True))
        
        status = '🟢' if macro.is_running else '🔴'
        self.status_label = Label(text=status, size_hint_x=0.1, font_size='20sp')
        h.add_widget(self.status_label)
        self.add_widget(h)
        
        # Info
        self.info_label = Label(
            text=f'📷 {len(macro.images)} imagens | Intervalo: {macro.interval}s',
            size_hint_y=None, height=dp(30),
            font_size='12sp', color=(0.6, 0.8, 1, 1)
        )
        self.add_widget(self.info_label)
        
        # Intervalo
        interval_box = BoxLayout(size_hint_y=None, height=dp(40), padding=dp(5))
        interval_box.add_widget(Label(text='⏱ Intervalo (seg):', size_hint_x=0.5))
        self.interval_input = TextInput(
            text=str(macro.interval), multiline=False,
            input_filter='float', size_hint_x=0.3
        )
        interval_box.add_widget(self.interval_input)
        interval_box.add_widget(Button(
            text='OK', size_hint_x=0.2,
            on_press=self.update_interval
        ))
        self.add_widget(interval_box)
        
        # Lista de imagens
        img_scroll = ScrollView(size_hint_y=0.45)
        self.img_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(5), padding=dp(5))
        self.img_layout.bind(minimum_height=self.img_layout.setter('height'))
        img_scroll.add_widget(self.img_layout)
        self.add_widget(img_scroll)
        
        # Log
        self.add_widget(Label(text='📋 Log:', size_hint_y=None, height=dp(25),
                             font_size='13sp', color=(1, 1, 0, 1)))
        
        log_scroll = ScrollView(size_hint_y=0.2)
        self.log_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(2))
        self.log_layout.bind(minimum_height=self.log_layout.setter('height'))
        log_scroll.add_widget(self.log_layout)
        self.add_widget(log_scroll)
        
        # Botões
        btns = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5), padding=dp(5))
        
        btns.add_widget(Button(
            text='📷\nAdd', font_size='12sp',
            background_color=(0, 0.6, 0.3, 1),
            on_press=self.add_image
        ))
        
        self.toggle_btn = Button(
            text='⏸\nParar' if macro.is_running else '▶\nIniciar',
            font_size='12sp',
            background_color=(0.8, 0.2, 0, 1) if macro.is_running else (0, 0.5, 0.8, 1),
            on_press=self.toggle
        )
        btns.add_widget(self.toggle_btn)
        
        btns.add_widget(Button(
            text='🧪\nTestar', font_size='12sp',
            background_color=(0.5, 0.3, 0.7, 1),
            on_press=self.test_action
        ))
        
        btns.add_widget(Button(
            text='🗑\nLimpar', font_size='12sp',
            background_color=(0.5, 0.1, 0.1, 1),
            on_press=self.clear_log
        ))
        
        self.add_widget(btns)
        
        self._refresh_images()
        self._log_update = Clock.schedule_interval(self._update_log, 1.0)
        
        if macro.is_running:
            self._start_timer()
    
    def _refresh_images(self):
        self.img_layout.clear_widgets()
        
        if not self.macro.images:
            self.img_layout.add_widget(Label(
                text='Nenhuma imagem.\nClique em "Add" para adicionar.',
                size_hint_y=None, height=dp(60), color=(0.5, 0.5, 0.5, 1)
            ))
            return
        
        for i, img in enumerate(self.macro.images):
            card = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(5))
            
            # Preview
            if os.path.exists(img.path):
                preview = Image(source=img.path, size_hint_x=0.2)
            else:
                preview = Label(text='?', size_hint_x=0.2)
            card.add_widget(preview)
            
            # Info
            info = BoxLayout(orientation='vertical', size_hint_x=0.45)
            color = (0, 1, 1, 1) if img.enabled else (0.5, 0.5, 0.5, 1)
            info.add_widget(Label(text=f'🏷 {img.tag}', color=color, font_size='13sp'))
            info.add_widget(Label(
                text=f'🎯 {img.action}',
                font_size='11sp', color=(0.7, 0.7, 0.7, 1)
            ))
            info.add_widget(Label(
                text=f'📍 ({img.target_x}, {img.target_y})',
                font_size='10sp', color=(0.6, 0.6, 0.6, 1)
            ))
            card.add_widget(info)
            
            # Botões
            btns = BoxLayout(orientation='vertical', size_hint_x=0.35, spacing=dp(2))
            btns.add_widget(Button(
                text='⚙ Config', font_size='11sp',
                on_press=lambda x, im=img: self.app.open_image_config(self.macro, im)
            ))
            btns.add_widget(Button(
                text='🗑 Excluir', font_size='11sp',
                background_color=(0.6, 0.1, 0.1, 1),
                on_press=lambda x, idx=i: self.delete_image(idx)
            ))
            card.add_widget(btns)
            
            self.img_layout.add_widget(card)
        
        self.info_label.text = f'📷 {len(self.macro.images)} imagens | Intervalo: {self.macro.interval}s'
    
    def add_image(self, inst):
        content = BoxLayout(orientation='vertical')
        
        path = '/storage/emulated/0' if os.path.exists('/storage/emulated/0') else os.path.expanduser('~')
        fc = FileChooserListView(path=path, filters=['*.png', '*.jpg', '*.jpeg'], size_hint_y=0.6)
        content.add_widget(fc)
        
        # Tag
        tag_box = BoxLayout(size_hint_y=None, height=dp(40))
        tag_box.add_widget(Label(text='Tag:', size_hint_x=0.2))
        tag_input = TextInput(hint_text='nome-imagem', multiline=False)
        tag_box.add_widget(tag_input)
        content.add_widget(tag_box)
        
        # Coordenadas
        coord_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        coord_box.add_widget(Label(text='X:', size_hint_x=0.1))
        x_input = TextInput(text='500', input_filter='int', multiline=False, size_hint_x=0.2)
        coord_box.add_widget(x_input)
        coord_box.add_widget(Label(text='Y:', size_hint_x=0.1))
        y_input = TextInput(text='800', input_filter='int', multiline=False, size_hint_x=0.2)
        coord_box.add_widget(y_input)
        content.add_widget(coord_box)
        
        popup = Popup(title='📷 Adicionar Imagem', content=content, size_hint=(0.95, 0.95))
        
        btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        
        def do_add(x):
            if fc.selection:
                fpath = fc.selection[0]
                mi = MacroImage(fpath, tag_input.text.strip() or None)
                try:
                    mi.target_x = int(x_input.text)
                    mi.target_y = int(y_input.text)
                except:
                    pass
                self.macro.images.append(mi)
                self.app.save_data()
                self._refresh_images()
                popup.dismiss()
        
        btns.add_widget(Button(text='✅ Adicionar', background_color=(0, 0.7, 0, 1), on_press=do_add))
        btns.add_widget(Button(text='❌ Cancelar', background_color=(0.7, 0, 0, 1), on_press=popup.dismiss))
        content.add_widget(btns)
        popup.open()
    
    def delete_image(self, idx):
        if 0 <= idx < len(self.macro.images):
            self.macro.images.pop(idx)
            self.app.save_data()
            self._refresh_images()
    
    def update_interval(self, inst):
        try:
            self.macro.interval = float(self.interval_input.text)
            self.app.save_data()
            self.info_label.text = f'✅ Intervalo: {self.macro.interval}s'
            if self.macro.is_running:
                self._stop_timer()
                self._start_timer()
        except:
            pass
    
    def toggle(self, inst):
        if self.macro.is_running:
            self._stop()
        else:
            self._start()
    
    def _start(self):
        if not self.macro.images:
            self.info_label.text = '⚠ Adicione imagens primeiro!'
            return
        
        active = [i for i in self.macro.images if i.enabled]
        if not active:
            self.info_label.text = '⚠ Ative pelo menos uma imagem!'
            return
        
        self.macro.is_running = True
        self._start_timer()
        self.toggle_btn.text = '⏸\nParar'
        self.toggle_btn.background_color = (0.8, 0.2, 0, 1)
        self.status_label.text = '🟢'
        self.info_label.text = f'▶ Executando a cada {self.macro.interval}s'
    
    def _stop(self):
        self.macro.is_running = False
        self._stop_timer()
        self.toggle_btn.text = '▶\nIniciar'
        self.toggle_btn.background_color = (0, 0.5, 0.8, 1)
        self.status_label.text = '🔴'
        self.info_label.text = '⏹ Parado'
    
    def _start_timer(self):
        self._stop_timer()
        self._timer = Clock.schedule_interval(self._execute_cycle, self.macro.interval)
    
    def _stop_timer(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None
    
    def _execute_cycle(self, dt):
        """Executa um ciclo de ações"""
        for img in self.macro.images:
            if img.enabled and img.can_execute():
                result = self.executor.execute(img.action, img.target_x, img.target_y)
                img.last_exec = time.time()
                img.exec_count += 1
                self.macro.exec_count += 1
    
    def test_action(self, inst):
        """Testa a primeira ação ativa"""
        for img in self.macro.images:
            if img.enabled:
                result = self.executor.execute(img.action, img.target_x, img.target_y)
                self.info_label.text = f'🧪 Testou: {img.tag} → {result.get("result", "?")}'
                return
        self.info_label.text = '⚠ Nenhuma imagem ativa!'
    
    def _update_log(self, dt):
        self.log_layout.clear_widgets()
        
        if not self.executor.log:
            self.log_layout.add_widget(Label(
                text='Nenhuma ação ainda...',
                size_hint_y=None, height=dp(25),
                font_size='11sp', color=(0.4, 0.4, 0.4, 1)
            ))
        else:
            for entry in reversed(self.executor.log[-8:]):
                color = (0, 1, 0, 1) if entry.get('result') == 'OK' else (1, 0.5, 0, 1)
                text = f"[{entry['time']}] {entry['action']} ({entry['x']},{entry['y']}) → {entry['result']}"
                self.log_layout.add_widget(Label(
                    text=text, size_hint_y=None, height=dp(22),
                    font_size='10sp', color=color
                ))
    
    def clear_log(self, inst):
        self.executor.log = []
        self.macro.exec_count = 0
        self._update_log(0)
    
    def go_back(self):
        if hasattr(self, '_log_update'):
            self._log_update.cancel()
        self.app.show_main()


class MainScreen(BoxLayout):
    """Tela principal"""
    
    def __init__(self, app, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.app = app
        
        # Título
        title = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10))
        title.add_widget(Label(
            text='🤖 Macro Vision AI',
            font_size='24sp', bold=True, color=(0, 1, 1, 1)
        ))
        self.add_widget(title)
        
        # Status
        running = sum(1 for m in app.macros if m.is_running)
        status = f'🟢 {running} ativo(s)' if running else '🔴 Nenhum ativo'
        self.add_widget(Label(
            text=f'{status}\n\n📌 Como usar:\n1. Crie um macro\n2. Adicione imagens de referência\n3. Configure as coordenadas de toque\n4. Inicie!',
            size_hint_y=None, height=dp(120),
            font_size='12sp', color=(0.7, 0.7, 0.7, 1)
        ))
        
        # Lista
        scroll = ScrollView(size_hint_y=0.5)
        self.macro_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(8), padding=dp(10))
        self.macro_layout.bind(minimum_height=self.macro_layout.setter('height'))
        scroll.add_widget(self.macro_layout)
        self.add_widget(scroll)
        
        # Botões
        btns = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(5), padding=dp(5))
        btns.add_widget(Button(
            text='➕ Novo Macro',
            background_color=(0, 0.6, 0.3, 1),
            font_size='15sp', bold=True,
            on_press=self.new_macro
        ))
        btns.add_widget(Button(
            text='⏹ Parar Todos',
            background_color=(0.6, 0.1, 0.1, 1),
            font_size='15sp',
            on_press=self.stop_all
        ))
        self.add_widget(btns)
        
        self.add_widget(Label(
            text=f'Total: {len(app.macros)} macros',
            size_hint_y=None, height=dp(25),
            font_size='11sp', color=(0.5, 0.5, 0.5, 1)
        ))
        
        self._refresh()
    
    def _refresh(self):
        self.macro_layout.clear_widgets()
        
        if not self.app.macros:
            self.macro_layout.add_widget(Label(
                text='Nenhum macro.\nClique em "Novo Macro" para criar.',
                size_hint_y=None, height=dp(80), color=(0.5, 0.5, 0.5, 1)
            ))
            return
        
        for m in self.app.macros:
            card = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(5), padding=dp(5))
            
            card.add_widget(Label(
                text='🟢' if m.is_running else '🔴',
                size_hint_x=0.08, font_size='18sp'
            ))
            
            info = BoxLayout(orientation='vertical', size_hint_x=0.5)
            info.add_widget(Label(text=f'🎯 {m.name}', font_size='14sp', bold=True))
            info.add_widget(Label(
                text=f'📷 {len(m.images)} imgs | ⏱ {m.interval}s',
                font_size='10sp', color=(0.6, 0.6, 0.6, 1)
            ))
            card.add_widget(info)
            
            btns = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=dp(2))
            btns.add_widget(Button(
                text='📂 Abrir', font_size='12sp',
                on_press=lambda x, mac=m: self.app.open_macro(mac)
            ))
            btns.add_widget(Button(
                text='🗑', font_size='12sp',
                background_color=(0.5, 0.1, 0.1, 1),
                on_press=lambda x, mac=m: self.delete_macro(mac)
            ))
            card.add_widget(btns)
            
            self.macro_layout.add_widget(card)
    
    def new_macro(self, inst):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        content.add_widget(Label(text='Nome do macro:', size_hint_y=None, height=dp(30)))
        name_input = TextInput(hint_text='Ex: Farm Gold', multiline=False, size_hint_y=None, height=dp(45))
        content.add_widget(name_input)
        
        popup = Popup(title='➕ Novo Macro', content=content, size_hint=(0.85, 0.35))
        
        btns = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        def create(x):
            mid = len(self.app.macros) + 1
            name = name_input.text.strip() or f'Macro #{mid}'
            self.app.macros.append(Macro(name, mid))
            self.app.save_data()
            self._refresh()
            popup.dismiss()
        
        btns.add_widget(Button(text='✅ Criar', background_color=(0, 0.7, 0, 1), on_press=create))
        btns.add_widget(Button(text='❌ Cancelar', background_color=(0.5, 0.1, 0.1, 1), on_press=popup.dismiss))
        content.add_widget(btns)
        popup.open()
    
    def delete_macro(self, macro):
        macro.is_running = False
        self.app.macros.remove(macro)
        self.app.save_data()
        self._refresh()
    
    def stop_all(self, inst):
        for m in self.app.macros:
            m.is_running = False
        self._refresh()


class MacroVisionApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.macros = []
        self.root_widget = None
    
    def build(self):
        self.title = 'Macro Vision AI'
        Window.clearcolor = (0.06, 0.06, 0.1, 1)
        
        self.root_widget = BoxLayout()
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
            ])
        except:
            pass
    
    def show_main(self):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(MainScreen(self))
    
    def open_macro(self, macro):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(MacroScreen(macro, self))
    
    def open_image_config(self, macro, img):
        self.root_widget.clear_widgets()
        self.root_widget.add_widget(ImageConfigScreen(macro, img, self))
    
    def save_data(self):
        try:
            data = {'macros': [m.to_dict() for m in self.macros]}
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Erro salvando: {e}")
    
    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                self.macros = [Macro.from_dict(d) for d in data.get('macros', [])]
        except Exception as e:
            print(f"Erro carregando: {e}")
    
    def on_pause(self):
        self.save_data()
        return True
    
    def on_resume(self):
        pass
    
    def on_stop(self):
        self.save_data()


if __name__ == '__main__':
    MacroVisionApp().run() 
