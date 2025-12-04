import sqlite3
import os
from datetime import datetime
from pathlib import Path

class DatabaseSetup:
    def __init__(self, db_file="smartphone_defects.db"):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Подключиться к базе данных"""
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.conn.row_factory = sqlite3.Row  # Для доступа по именам колонок
        return self.conn
    
    def disconnect(self):
        """Отключиться от базы данных"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Создать все таблицы базы данных"""
        # Таблица ролей пользователей
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_role (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT NOT NULL UNIQUE,
            description TEXT
        )
        ''')
        
        # Таблица пользователей
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            full_name TEXT,
            role_id INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME,
            FOREIGN KEY (role_id) REFERENCES user_role(id)
        )
        ''')
        
        # Таблица производителей
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS manufacturer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            country TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица моделей смартфонов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS smartphone_model (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            release_year INTEGER,
            screen_type TEXT CHECK(screen_type IN ('OLED', 'LCD', 'AMOLED', 'IPS', 'TFT')),
            screen_size REAL,
            ram_gb INTEGER,
            storage_gb INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id),
            UNIQUE(manufacturer_id, model_name)
        )
        ''')
        
        # Таблица типов дефектов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect_type (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица локаций дефектов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect_location (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица уровней серьезности
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS severity_level (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_name TEXT NOT NULL UNIQUE,
            score INTEGER NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица устройств
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS device (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            imei TEXT UNIQUE,
            serial_number TEXT UNIQUE,
            color TEXT,
            production_date DATE,
            purchase_date DATE,
            warranty_until DATE,
            current_owner TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES smartphone_model(id)
        )
        ''')
        
        # Таблица дефектов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            defect_type_id INTEGER NOT NULL,
            location_id INTEGER NOT NULL,
            severity_id INTEGER NOT NULL,
            detected_by_user_id INTEGER,
            detection_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            length_mm REAL,
            width_mm REAL,
            depth_mm REAL,
            description TEXT,
            is_repaired BOOLEAN DEFAULT FALSE,
            repair_date DATETIME,
            repair_cost REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES device(id),
            FOREIGN KEY (defect_type_id) REFERENCES defect_type(id),
            FOREIGN KEY (location_id) REFERENCES defect_location(id),
            FOREIGN KEY (severity_id) REFERENCES severity_level(id),
            FOREIGN KEY (detected_by_user_id) REFERENCES app_user(id)
        )
        ''')
        
        # Таблица изображений дефектов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect_image (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            defect_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            image_data BLOB,
            capture_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_verified BOOLEAN DEFAULT FALSE,
            verified_by_user_id INTEGER,
            verification_date DATETIME,
            verification_notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (defect_id) REFERENCES defect(id),
            FOREIGN KEY (verified_by_user_id) REFERENCES app_user(id)
        )
        ''')
        
        # Таблица техников
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS technician (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            specialization TEXT,
            hire_date DATE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Таблица диагностики
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnosis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            defect_id INTEGER NOT NULL,
            technician_id INTEGER NOT NULL,
            diagnosis_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            conclusion TEXT,
            recommended_action TEXT,
            estimated_cost REAL,
            estimated_time_hours INTEGER,
            priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'critical')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (defect_id) REFERENCES defect(id),
            FOREIGN KEY (technician_id) REFERENCES technician(id)
        )
        ''')
        
        # Таблица ремонтов
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS repair (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            defect_id INTEGER NOT NULL,
            technician_id INTEGER NOT NULL,
            start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_date DATETIME,
            repair_type TEXT,
            cost REAL,
            status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled', 'on_hold')),
            parts_used TEXT,
            labor_hours REAL,
            warranty_until DATE,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (defect_id) REFERENCES defect(id),
            FOREIGN KEY (technician_id) REFERENCES technician(id)
        )
        ''')
        
        # Таблица логов операций
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS operation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            table_name TEXT,
            record_id INTEGER,
            operation TEXT CHECK(operation IN ('insert', 'update', 'delete')),
            old_values TEXT,
            new_values TEXT,
            operation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES app_user(id)
        )
        ''')
        
        self.conn.commit()
        print("Таблицы успешно созданы")
    
    def insert_sample_data(self):
        """Вставить тестовые данные"""
        # Роли пользователей
        roles = [
            ('Администратор', 'Полный доступ ко всем функциям'),
            ('Менеджер', 'Управление данными, просмотр отчетов'),
            ('Техник', 'Внесение данных о дефектах и ремонтах'),
            ('Оператор', 'Внесение базовой информации'),
            ('Просмотр', 'Только чтение данных')
        ]
        self.cursor.executemany(
            'INSERT INTO user_role (role_name, description) VALUES (?, ?)', 
            roles
        )
        
        # Пользователи (пароль: password123)
        users = [
            ('admin', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 
             'admin@company.com', 'Администратор Системы', 1),
            ('manager', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
             'manager@company.com', 'Менеджер Отдела', 2),
            ('tech1', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
             'tech1@company.com', 'Техник Иванов', 3),
            ('operator1', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',
             'operator@company.com', 'Оператор Петрова', 4)
        ]
        self.cursor.executemany('''
            INSERT INTO app_user (username, password_hash, email, full_name, role_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', users)
        
        # Производители
        manufacturers = [
            ('Apple', 'США'),
            ('Samsung', 'Южная Корея'),
            ('Xiaomi', 'Китай'),
            ('Huawei', 'Китай'),
            ('OnePlus', 'Китай'),
            ('Google', 'США'),
            ('Sony', 'Япония'),
            ('Nokia', 'Финляндия'),
            ('Realme', 'Китай'),
            ('OPPO', 'Китай')
        ]
        self.cursor.executemany(
            'INSERT INTO manufacturer (name, country) VALUES (?, ?)', 
            manufacturers
        )
        
        # Типы дефектов
        defect_types = [
            ('Царапина', 'Поверхностное повреждение защитного стекла'),
            ('Глубокая царапина', 'Царапина, затрагивающая слои под стеклом'),
            ('Скол', 'Локальное повреждение края экрана'),
            ('Трещина', 'Линейное повреждение экрана'),
            ('Паутина', 'Множественные радиальные трещины'),
            ('Пятно', 'Повреждение дисплея под стеклом'),
            ('Выгорание', 'Выгорание пикселей OLED дисплея'),
            ('Битый пиксель', 'Неработающий пиксель на дисплее'),
            ('Попадание влаги', 'Следы влаги под стеклом'),
            ('Отслоение', 'Отслоение защитного стекла')
        ]
        self.cursor.executemany(
            'INSERT INTO defect_type (name, description) VALUES (?, ?)', 
            defect_types
        )
        
        # Локации дефектов
        locations = [
            ('Верхний левый угол', 'Левый верхний угол экрана'),
            ('Верхний край', 'Верхняя часть экрана'),
            ('Верхний правый угол', 'Правый верхний угол экрана'),
            ('Левый край', 'Левая боковая часть экрана'),
            ('Центр', 'Центральная часть экрана'),
            ('Правый край', 'Правая боковая часть экрана'),
            ('Нижний левый угол', 'Левый нижний угол экрана'),
            ('Нижний край', 'Нижняя часть экрана'),
            ('Нижний правый угол', 'Правый нижний угол экрана'),
            ('Весь экран', 'Повреждение по всей площади экрана')
        ]
        self.cursor.executemany(
            'INSERT INTO defect_location (name, description) VALUES (?, ?)', 
            locations
        )
        
        # Уровни серьезности
        severity_levels = [
            ('Минимальный', 1, 'Не влияет на использование'),
            ('Незначительный', 2, 'Визуальный дефект, не влияет на функциональность'),
            ('Умеренный', 3, 'Частично влияет на использование'),
            ('Серьезный', 4, 'Существенно влияет на использование'),
            ('Критический', 5, 'Устройство неисправно')
        ]
        self.cursor.executemany('''
            INSERT INTO severity_level (level_name, score, description) 
            VALUES (?, ?, ?)
        ''', severity_levels)
        
        # Модели смартфонов
        smartphone_models = [
            (1, 'iPhone 13', 2021, 'OLED', 6.1, 4, 128),
            (1, 'iPhone 13 Pro', 2021, 'OLED', 6.1, 6, 256),
            (1, 'iPhone SE (2022)', 2022, 'LCD', 4.7, 4, 64),
            (2, 'Galaxy S22', 2022, 'AMOLED', 6.1, 8, 128),
            (2, 'Galaxy S22 Ultra', 2022, 'AMOLED', 6.8, 12, 256),
            (2, 'Galaxy A53', 2022, 'AMOLED', 6.5, 6, 128),
            (3, 'Redmi Note 11 Pro', 2022, 'AMOLED', 6.67, 6, 128),
            (3, 'Xiaomi 12', 2022, 'AMOLED', 6.28, 8, 256),
            (4, 'P50 Pro', 2021, 'OLED', 6.6, 8, 256),
            (5, '10 Pro', 2022, 'AMOLED', 6.7, 12, 256)
        ]
        self.cursor.executemany('''
            INSERT INTO smartphone_model 
            (manufacturer_id, model_name, release_year, screen_type, screen_size, ram_gb, storage_gb) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', smartphone_models)
        
        # Техники
        technicians = [
            ('Иванов Алексей Сергеевич', 'ivanov@service.com', '+79161234567', 
             'Замена дисплеев, полировка', '2020-05-15'),
            ('Петрова Мария Владимировна', 'petrova@service.com', '+79167654321', 
             'Диагностика, ремонт плат', '2021-02-10'),
            ('Сидоров Дмитрий Алексеевич', 'sidorov@service.com', '+79169998877', 
             'Ремонт после попадания влаги', '2019-11-23'),
            ('Козлова Анна Игоревна', 'kozlova@service.com', '+79165554433',
             'Калибровка дисплеев', '2022-03-20')
        ]
        self.cursor.executemany('''
            INSERT INTO technician 
            (name, email, phone, specialization, hire_date) 
            VALUES (?, ?, ?, ?, ?)
        ''', technicians)
        
        # Устройства
        devices = [
            (1, '354678901234567', 'SN123456789', 'Синий', '2021-09-01', '2021-10-15', '2023-10-15', 'Иванов И.И.'),
            (4, '456789012345678', 'SN234567890', 'Черный', '2022-03-15', '2022-04-20', '2024-04-20', 'Петров П.П.'),
            (7, '567890123456789', 'SN345678901', 'Белый', '2022-05-20', '2022-06-10', '2024-06-10', 'Сидоров С.С.'),
            (10, '678901234567890', 'SN456789012', 'Серый', '2022-07-10', '2022-08-05', '2024-08-05', 'Козлова К.К.')
        ]
        self.cursor.executemany('''
            INSERT INTO device 
            (model_id, imei, serial_number, color, production_date, purchase_date, warranty_until, current_owner) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', devices)
        
        # Дефекты
        defects = [
            (1, 1, 8, 2, 3, '2022-10-15 09:30:00', 15.2, 0.1, 0.01, 'Длинная тонкая царапина', False, None, None),
            (1, 3, 9, 3, 3, '2022-10-15 09:30:00', 2.5, 2.5, 0.5, 'Скол в левом нижнем углу', False, None, None),
            (2, 4, 5, 4, 3, '2022-11-02 14:15:00', 35.0, 0.5, None, 'Трещина от верха до центра', False, None, None),
            (3, 1, 5, 1, 3, '2022-11-10 11:20:00', 8.7, 0.05, 0.005, 'Несколько мелких царапин', True, '2022-11-12', 1500.0),
            (4, 6, 10, 5, 3, '2022-11-25 16:45:00', None, None, None, 'Паутина по всему экрану', False, None, None)
        ]
        self.cursor.executemany('''
            INSERT INTO defect 
            (device_id, defect_type_id, location_id, severity_id, detected_by_user_id, detection_date, 
             length_mm, width_mm, depth_mm, description, is_repaired, repair_date, repair_cost) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', defects)
        
        # Изображения дефектов
        images = [
            (1, 'images/defect_1_1.jpg', None, '2022-10-15 09:32:00', True, 3, '2022-10-15 10:15:00', 'Хорошо видна царапина'),
            (1, 'images/defect_1_2.jpg', None, '2022-10-15 09:33:00', True, 3, '2022-10-15 10:15:00', 'Под другим углом'),
            (2, 'images/defect_2_1.jpg', None, '2022-11-02 14:20:00', True, 3, '2022-11-02 15:30:00', 'Скол хорошо виден'),
            (3, 'images/defect_3_1.jpg', None, '2022-11-10 11:25:00', False, None, None, None),
            (4, 'images/defect_4_1.jpg', None, '2022-11-25 16:50:00', True, 2, '2022-11-25 17:30:00', 'Множественные трещины')
        ]
        self.cursor.executemany('''
            INSERT INTO defect_image 
            (defect_id, image_path, image_data, capture_date, is_verified, verified_by_user_id, 
             verification_date, verification_notes) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', images)
        
        # Диагностики
        diagnoses = [
            (1, 1, '2022-10-15 10:00:00', 'Поверхностная царапина, не влияет на функциональность', 
             'Полировка экрана', 1500.0, 1, 'low'),
            (2, 1, '2022-10-15 10:05:00', 'Скол края экрана, возможны дальнейшие повреждения', 
             'Замена защитного стекла', 3000.0, 2, 'medium'),
            (3, 2, '2022-11-02 15:00:00', 'Сквозная трещина, требуется замена экрана', 
             'Полная замена дисплея', 12000.0, 4, 'high'),
            (5, 3, '2022-11-25 17:00:00', 'Множественные трещины, дисплей не функционирует', 
             'Замена дисплейного модуля', 8500.0, 3, 'critical')
        ]
        self.cursor.executemany('''
            INSERT INTO diagnosis 
            (defect_id, technician_id, diagnosis_date, conclusion, recommended_action, 
             estimated_cost, estimated_time_hours, priority) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', diagnoses)
        
        # Ремонты
        repairs = [
            (1, 1, '2022-10-15 10:30:00', '2022-10-15 11:15:00', 'Полировка', 1500.0, 
             'completed', 'Специальная паста для полировки', 1.0, '2023-10-15', 'Качество хорошее'),
            (3, 2, '2022-11-03 10:00:00', '2022-11-03 12:30:00', 'Замена дисплея', 12000.0, 
             'completed', 'Оригинальный дисплей Samsung', 2.5, '2023-11-03', 'Установлен оригинальный дисплей'),
            (5, 1, '2022-11-26 10:00:00', None, 'Замена дисплейного модуля', 8500.0, 
             'in_progress', 'Модуль OnePlus', None, None, 'Ожидается доставка детали')
        ]
        self.cursor.executemany('''
            INSERT INTO repair 
            (defect_id, technician_id, start_date, end_date, repair_type, cost, status, 
             parts_used, labor_hours, warranty_until, notes) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', repairs)
        
        self.conn.commit()
        print("Тестовые данные успешно добавлены")
    
    def create_database(self):
        """Создать полную базу данных с тестовыми данными"""
        print(f"Создание базы данных: {self.db_file}")
        
        # Проверяем, существует ли файл
        if os.path.exists(self.db_file):
            backup = f"{self.db_file}.backup"
            print(f"Файл уже существует. Создаю резервную копию: {backup}")
            os.rename(self.db_file, backup)
        
        self.connect()
        self.create_tables()
        self.insert_sample_data()
        self.disconnect()
        
        print(f"\nБаза данных '{self.db_file}' успешно создана!")
        print("\nДанные для входа:")
        print("Логин: admin, manager, tech1, operator1")
        print("Пароль для всех: password123")

if __name__ == "__main__":
    db_setup = DatabaseSetup()
    db_setup.create_database()
