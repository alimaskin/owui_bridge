import os

# Структура содержимого проекта (без самой верхней папки)
project_structure = [
    "app/__init__.py",
    "app/config.py",
    "app/db.py",
    "app/sender.py",
    "app/transfer.py",
    "app/scheduler.py",
    "tests/__init__.py",  # Папка для тестов
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "requirements.dev.txt",
    ".env",
    ".env.prod",
    ".gitignore",
    "README.md",
]

def create_project_structure():
    for file_path in project_structure:
        # Создаем директории, если их еще нет
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        # Создаем пустой файл
        with open(file_path, 'w') as f:
            pass  # Создаем пустой файл

if __name__ == "__main__":
    create_project_structure()
    print("Содержимое проекта создано в текущей папке!")

