from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
import threading
import webbrowser
import os
import time
from datetime import datetime
import urllib.parse

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Кастомный обработчик HTTP запросов с логированием"""
    
    def log_message(self, format, *args):
        """Кастомное логирование запросов"""
        # Игнорируем запросы к favicon.ico и файлам разработчика
        if 'favicon.ico' in format or '.well-known' in format:
            return
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{timestamp} - {self.address_string()} - {format % args}")
    
    def do_GET(self):
        # Если путь указывает на директорию, показываем index.html
        if self.path == '/':
            self.path = '/index.html'
        
        # Игнорируем запросы к favicon.ico
        if self.path == '/favicon.ico':
            self.send_response(204)  # No Content
            self.end_headers()
            return
            
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def translate_path(self, path):
        # Обработка путей для статических файлов
        path = urllib.parse.unquote(path)
        if path.startswith('/static/'):
            return os.path.join(os.getcwd(), path[1:])
        return SimpleHTTPRequestHandler.translate_path(self, path)

class ServerManager:
    def __init__(self, port=8000, host='0.0.0.0'):
        self.port = port
        self.host = host
        self.server = None
        self.server_thread = None
        self.is_running = False
        
    def get_local_ip(self):
        """Получает локальный IP адрес"""
        try:
            # Создаем временное соединение чтобы получить локальный IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def get_public_ip(self):
        """Пытается получить публичный IP адрес"""
        try:
            import requests
            response = requests.get('https://api.ipify.org', timeout=5)
            return response.text
        except:
            return None
    
    def check_static_files(self):
        """Проверяет наличие необходимых статических файлов"""
        required_files = {
            'images': [
                'static/images/work1.jpg',
                'static/images/work2.jpg', 
                'static/images/work3.jpg',
                'static/images/employee1.jpg',
                'static/images/employee2.jpg',
                'static/images/employee3.jpg',
                'static/images/about.jpg',
                'static/images/hero-bg.jpg'
            ],
            'videos': [
                'static/videos/demo.mp4'
            ]
        }
        
        missing_files = []
        
        for category, files in required_files.items():
            for file_path in files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
        
        return missing_files
    
    def create_sample_images(self):
        """Создает образцы изображений если они отсутствуют"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import os
            
            # Создаем директории если их нет
            os.makedirs('static/images', exist_ok=True)
            os.makedirs('static/videos', exist_ok=True)
            
            # Создаем образцы изображений
            images_to_create = [
                ('static/images/work1.jpg', 'Проект 1', (800, 600)),
                ('static/images/work2.jpg', 'Проект 2', (800, 600)),
                ('static/images/work3.jpg', 'Проект 3', (800, 600)),
                ('static/images/employee1.jpg', 'Иван Петров', (600, 600)),
                ('static/images/employee2.jpg', 'Сергей Иванов', (600, 600)),
                ('static/images/employee3.jpg', 'Алексей Смирнов', (600, 600)),
                ('static/images/about.jpg', 'О компании', (800, 600)),
                ('static/images/hero-bg.jpg', 'МастерДом', (1200, 800))
            ]
            
            for file_path, text, size in images_to_create:
                if not os.path.exists(file_path):
                    img = Image.new('RGB', size, color=(73, 109, 137))
                    d = ImageDraw.Draw(img)
                    
                    # Простой текст (без шрифта)
                    bbox = d.textbbox((0,0), text)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    x = (size[0] - text_width) / 2
                    y = (size[1] - text_height) / 2
                    
                    d.text((x, y), text, fill=(255, 255, 255))
                    img.save(file_path)
                    print(f"✅ Создан образец: {file_path}")
            
            # Создаем пустой видео файл (заглушку)
            video_path = 'static/videos/demo.mp4'
            if not os.path.exists(video_path):
                with open(video_path, 'w') as f:
                    f.write("Это заглушка для видео файла")
                print(f"⚠️  Создана заглушка для видео: {video_path}")
                print("   Замените его настоящим видеофайлом")
                
        except ImportError:
            print("❌ Для создания образцов установите Pillow: pip install Pillow")
            return False
        except Exception as e:
            print(f"❌ Ошибка при создании образцов: {e}")
            return False
            
        return True
    
    def start_server(self):
        """Запускает HTTP сервер в отдельном потоке"""
        server_address = (self.host, self.port)
        self.server = HTTPServer(server_address, CustomHTTPRequestHandler)
        self.is_running = True
        
        def run_server():
            while self.is_running:
                self.server.handle_request()
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print("=" * 60)
        print("🚀 СЕРВЕР ЗАПУЩЕН УСПЕШНО!")
        print("=" * 60)
        
        # Проверяем статические файлы
        missing_files = self.check_static_files()
        if missing_files:
            print("\n⚠️  ОТСУТСТВУЮТ ФАЙЛЫ:")
            for file in missing_files:
                print(f"   ❌ {file}")
            print("\n🔄 Попытка создать образцы файлов...")
            if self.create_sample_images():
                print("✅ Образцы файлов созданы успешно!")
            else:
                print("❌ Не удалось создать образцы файлов")
        
        # Выводим информацию о доступных адресах
        local_ip = self.get_local_ip()
        public_ip = self.get_public_ip()
        
        print(f"\n📁 Папка с сайтом: {os.path.abspath('.')}")
        print(f"🌐 Порт: {self.port}")
        print("\n📍 ДОСТУПНЫЕ АДРЕСА:")
        print(f"   Локальный:  http://localhost:{self.port}")
        print(f"   В сети:     http://{local_ip}:{self.port}")
        
        if public_ip:
            print(f"   Публичный:  http://{public_ip}:{self.port}")
            print("\n💡 Для доступа из интернета:")
            print(f"   Откройте в браузере: http://{public_ip}:{self.port}")
            print("   ⚠️  Убедитесь, что порт открыт в брандмауэре!")
        else:
            print("\n⚠️  Не удалось определить публичный IP")
            print("   Для доступа из интернета настройте проброс портов на роутере")
        
        print("\n📊 Логи запросов (игнорируются favicon и служебные запросы)")
        print("=" * 60)
        
        # Автоматически открываем в браузере
        try:
            webbrowser.open(f'http://localhost:{self.port}')
            print("🌐 Браузер открыт автоматически")
        except:
            print("❌ Не удалось открыть браузер автоматически")
    
    def generate_qr_code(self, url):
        """Генерирует QR-код для быстрого доступа с мобильных устройств"""
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_path = "site_qr.png"
            qr_img.save(qr_path)
            print(f"📱 QR-код сохранен как: {qr_path}")
            return qr_path
        except ImportError:
            print("💡 Установите 'qrcode' для генерации QR-кода: pip install qrcode[pil]")
            return None
    
    def check_port_availability(self):
        """Проверяет доступность порта"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', self.port))
        sock.close()
        return result == 0
    
    def stop_server(self):
        """Останавливает сервер"""
        self.is_running = False
        if self.server:
            self.server.shutdown()
        print("\n🛑 Сервер остановлен")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Запуск сервера для сайта МастерДом')
    parser.add_argument('--port', '-p', type=int, default=8000, 
                       help='Порт для запуска сервера (по умолчанию: 8000)')
    parser.add_argument('--host', default='0.0.0.0', 
                       help='Хост для запуска сервера (по умолчанию: 0.0.0.0)')
    parser.add_argument('--no-browser', action='store_true', 
                       help='Не открывать браузер автоматически')
    parser.add_argument('--qr', action='store_true', 
                       help='Сгенерировать QR-код для доступа')
    parser.add_argument('--create-samples', action='store_true',
                       help='Создать образцы изображений если они отсутствуют')
    
    args = parser.parse_args()
    
    # Проверяем существование index.html
    if not os.path.exists('index.html'):
        print("❌ ОШИБКА: Файл index.html не найден в текущей директории!")
        print("Убедитесь, что вы запускаете скрипт из папки с сайтом")
        return
    
    # Проверяем доступность порта
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        temp_sock.bind(('0.0.0.0', args.port))
        temp_sock.close()
    except OSError:
        print(f"❌ Порт {args.port} уже занят!")
        print("Используйте другой порт: python server.py --port 8080")
        return
    
    # Запускаем сервер
    server_manager = ServerManager(port=args.port, host=args.host)
    
    # Создаем образцы если нужно
    if args.create_samples:
        server_manager.create_sample_images()
    
    try:
        server_manager.start_server()
        
        # Генерируем QR-код если запрошено
        if args.qr:
            local_ip = server_manager.get_local_ip()
            server_manager.generate_qr_code(f"http://{local_ip}:{args.port}")
        
        print("\n⚡ Сервер работает... Нажмите Ctrl+C для остановки")
        
        # Бесконечный цикл для поддержания работы сервера
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Получен сигнал прерывания...")
        server_manager.stop_server()
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        server_manager.stop_server()

if __name__ == '__main__':
    main()
