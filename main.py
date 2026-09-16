import os
import hashlib
import io
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp

# Для Android
try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

    ANDROID = True
except ImportError:
    ANDROID = False

NONCE_SIZE = 12


# ============ КРИПТОГРАФИЯ ============

def derive_key(password: str) -> bytes:
    return hashlib.sha256(password.encode('utf-8')).digest()


def encrypt_file_bytes(data: bytes, password: str) -> bytes:
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext


def decrypt_file_bytes(data: bytes, password: str):
    """Возвращает (успех, результат). Результат — либо расшифрованные байты, либо хеш пароля."""
    if len(data) < NONCE_SIZE:
        return False, hashlib.sha256(password.encode('utf-8')).hexdigest()

    nonce = data[:NONCE_SIZE]
    ciphertext = data[NONCE_SIZE:]
    key = derive_key(password)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return True, plaintext
    except Exception:
        return False, hashlib.sha256(password.encode('utf-8')).hexdigest()


# ============ ИНТЕРФЕЙС ============

class StyledButton(Button):
    """Красивая кнопка с градиентом."""

    def __init__(self, bg_color, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = bg_color
        self.font_size = dp(18)
        self.bold = True
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = dp(70)


class HashApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.15, 1)  # Темный фон

        self.selected_file = None
        self.password = ""

        # Главный контейнер
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        # ===== ВЕРХНЯЯ КНОПКА: РАСШИФРОВАТЬ =====
        self.btn_decrypt = StyledButton(
            text="🔓  ПОДСЧЕТ ХЕША\n",
            bg_color=(0.2, 0.6, 0.9, 1),  # Синий
            on_press=self.on_decrypt
        )
        root.add_widget(self.btn_decrypt)

        # ===== ЦЕНТРАЛЬНЫЙ ЛОГОТИП =====
        logo_layout = BoxLayout(orientation='vertical', size_hint_y=0.4)
        with logo_layout.canvas.before:
            Color(0.15, 0.15, 0.25, 1)
            self.logo_bg = Rectangle(pos=logo_layout.pos, size=logo_layout.size)
        logo_layout.bind(pos=self._update_logo, size=self._update_logo)

        self.logo_label = Label(
            text="ХЕШ",
            font_size=dp(80),
            bold=True,
            color=(1, 0.8, 0.2, 1),  # Золотой
            size_hint=(1, 1)
        )
        logo_layout.add_widget(self.logo_label)
        root.add_widget(logo_layout)

        # ===== НИЖНЯЯ КНОПКА: ЗАШИФРОВАТЬ =====
        self.btn_encrypt = StyledButton(
            text="🔒  ХЕШ-ФУНКЦИЯ\n",
            bg_color=(0.2, 0.7, 0.4, 1),  # Зеленый
            on_press=self.on_encrypt
        )
        root.add_widget(self.btn_encrypt)

        # ===== СТАТУС-БАР =====
        self.status_label = Label(
            text="Выберите действие",
            size_hint_y=None,
            height=dp(40),
            color=(0.7, 0.7, 0.7, 1),
            font_size=dp(14)
        )
        root.add_widget(self.status_label)

        # Запрос разрешений на Android
        if ANDROID:
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

        return root

    def _update_logo(self, instance, value):
        self.logo_bg.pos = instance.pos
        self.logo_bg.size = instance.size

    # ===== ДЕЙСТВИЯ =====

    def on_encrypt(self, instance):
        """Зашифровать файл."""
        self._show_file_chooser(mode='encrypt')

    def on_decrypt(self, instance):
        """Расшифровать файл."""
        self._show_file_chooser(mode='decrypt')

    def _show_file_chooser(self, mode: str):
        """Показывает окно выбора файла."""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Путь к файлам
        if ANDROID:
            start_path = primary_external_storage_path()
        else:
            start_path = os.path.expanduser('~')

        file_chooser = FileChooserListView(
            path=start_path,
            filters=['*.docx', '*.enc', '*'],
            dirselect=False
        )
        content.add_widget(file_chooser)

        # Поле пароля
        password_input = TextInput(
            hint_text='Введите пароль',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        content.add_widget(password_input)

        # Кнопки
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        def on_select(btn):
            selection = file_chooser.selection
            if not selection:
                self._show_popup("Ошибка", "Файл не выбран")
                return
            path = selection[0]
            password = password_input.text.strip()
            if not password:
                self._show_popup("Ошибка", "Введите пароль")
                return

            popup.dismiss()

            if mode == 'encrypt':
                self._do_encrypt(path, password)
            else:
                self._do_decrypt(path, password)

        btn_select = Button(text="Выбрать", size_hint_x=0.5)
        btn_select.bind(on_press=on_select)

        btn_cancel = Button(text="Отмена", size_hint_x=0.5)
        btn_cancel.bind(on_press=lambda x: popup.dismiss())

        buttons.add_widget(btn_select)
        buttons.add_widget(btn_cancel)
        content.add_widget(buttons)

        popup = Popup(
            title="Выберите файл" if mode == 'encrypt' else "Выберите .enc файл",
            content=content,
            size_hint=(0.95, 0.9)
        )
        popup.open()

    def _do_encrypt(self, path: str, password: str):
        """Шифрование .docx файла."""
        # Проверка расширения
        if not path.lower().endswith('.docx'):
            self._show_popup("Ошибка", "Можно шифровать только файлы .docx")
            return

        try:
            with open(path, 'rb') as f:
                data = f.read()

            encrypted = encrypt_file_bytes(data, password)

            # Сохраняем рядом с оригиналом
            base = os.path.splitext(path)[0]
            out_path = base + ".enc"

            with open(out_path, 'wb') as f:
                f.write(encrypted)

            self.status_label.text = f"✅ Зашифровано: {os.path.basename(out_path)}"
            self._show_popup("Успех", f"Файл зашифрован:\n{out_path}")

        except Exception as e:
            self._show_popup("Ошибка", str(e))

    def _do_decrypt(self, path: str, password: str):
        try:
            with open(path, 'rb') as f:
                data = f.read()
            
            success, result = decrypt_file_bytes(data, password)
            
            if not success:
                self.status_label.text = "❌ формат хеша"
                self._show_popup("Неверный формат хеша", f"Хеш введённого пароля:\n\n{result}")
                return
            
            # Пароль верный — извлекаем текст с помощью docx2txt
            try:
                import tempfile
                import docx2txt
                import os
                
                # Создаем временный файл в памяти устройства
                with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                    tmp.write(result)
                    tmp_path = tmp.name
                
                # Извлекаем текст
                text = docx2txt.process(tmp_path)
                
                # Удаляем временный файл
                os.remove(tmp_path)
                
                if not text or not text.strip():
                    text = "[Документ пуст или не содержит текста]"
                    
            except Exception as e:
                text = f"⚠ Файл расшифрован, но не является .docx\n\n{str(e)}"
            
            self.status_label.text = "✅ Пароль верный"
            self._show_scrollable_popup("Содержимое документа", text)
            
        except Exception as e:
            self._show_popup("Ошибка", str(e))
    def _show_popup(self, title: str, message: str):
        """Простое всплывающее окно."""
        popup = Popup(
            title=title,
            content=Label(text=message, text_size=(dp(350), None), halign='center'),
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def _show_scrollable_popup(self, title: str, text: str):
        """Окно с прокруткой для длинного текста."""
        scroll = ScrollView(size_hint=(1, 1))
        label = Label(
            text=text,
            size_hint_y=None,
            text_size=(dp(350), None),
            halign='left',
            valign='top'
        )
        label.bind(texture_size=label.setter('size'))
        scroll.add_widget(label)

        popup = Popup(title=title, content=scroll, size_hint=(0.9, 0.8))
        popup.open()


if __name__ == '__main__':
    HashApp().run()