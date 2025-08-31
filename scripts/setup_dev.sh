#!/bin/bash
# scripts/setup_dev.sh - Автоматическая настройка проекта для разработки

set -e  # Остановить выполнение при ошибке

echo "🚀 Настройка проекта MOEX ISS Client..."

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Проверка Python версии
check_python_version() {
    log_info "Проверка версии Python..."
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    required_version="3.8"
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_success "Python $python_version - OK"
    else
        log_error "Требуется Python 3.8+, установлен: $python_version"
        exit 1
    fi
}

# Создание структуры папок
create_directories() {
    log_info "Создание структуры папок..."
    
    # Основные папки
    mkdir -p src/moex_client/{auth,client,config,models,cli}
    mkdir -p tests/fixtures
    mkdir -p scripts
    mkdir -p data/{raw,processed}
    mkdir -p logs
    
    # Создание __init__.py файлов
    touch src/moex_client/__init__.py
    touch src/moex_client/auth/__init__.py
    touch src/moex_client/client/__init__.py
    touch src/moex_client/config/__init__.py
    touch src/moex_client/models/__init__.py
    touch src/moex_client/cli/__init__.py
    touch tests/__init__.py
    
    log_success "Структура папок создана"
}

# Создание виртуального окружения
setup_virtual_environment() {
    log_info "Настройка виртуального окружения..."
    
    if [ -d "venv" ]; then
        log_warning "Виртуальное окружение уже существует"
        read -p "Пересоздать виртуальное окружение? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            log_info "Старое виртуальное окружение удалено"
        else
            log_info "Используем существующее виртуальное окружение"
            return 0
        fi
    fi
    
    python3 -m venv venv
    log_success "Виртуальное окружение создано"
    
    # Активация виртуального окружения
    source venv/bin/activate
    
    # Обновление pip
    log_info "Обновление pip..."
    pip install --upgrade pip
    log_success "pip обновлен"
}

# Установка зависимостей
install_dependencies() {
    log_info "Установка зависимостей..."
    
    # Активация виртуального окружения
    source venv/bin/activate
    
    # Установка основных зависимостей
    pip install -e ".[dev]"
    
    log_success "Зависимости установлены"
}

# Инициализация Git репозитория
setup_git() {
    log_info "Настройка Git репозитория..."
    
    if [ -d ".git" ]; then
        log_warning "Git репозиторий уже существует"
    else
        git init
        log_success "Git репозиторий инициализирован"
    fi
    
    # Добавление файлов в git
    git add .
    if git diff --staged --quiet; then
        log_info "Нет изменений для коммита"
    else
        git commit -m "Initial project setup with modern structure" || log_warning "Коммит не удался (возможно уже существует)"
        log_success "Начальный коммит создан"
    fi
}

# Настройка переменных окружения
setup_environment() {
    log_info "Настройка переменных окружения..."
    
    if [ -f ".env" ]; then
        log_warning "Файл .env уже существует"
    else
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Файл .env создан из .env.example"
            log_warning "⚠️  ВАЖНО: Отредактируйте файл .env и добавьте ваши учетные данные MOEX"
            log_warning "    MOEX_USERNAME=ваш_логин"
            log_warning "    MOEX_PASSWORD=ваш_пароль"
        else
            log_error "Файл .env.example не найден"
        fi
    fi
}

# Проверка настройки
verify_setup() {
    log_info "Проверка настройки проекта..."
    
    # Активация виртуального окружения
    source venv/bin/activate
    
    # Проверка импорта основных модулей
    if python -c "import requests, click, rich, pydantic" 2>/dev/null; then
        log_success "Основные зависимости установлены корректно"
    else
        log_error "Проблема с установкой зависимостей"
        return 1
    fi
    
    # Проверка структуры проекта
    if [ -f "pyproject.toml" ] && [ -f "requirements.txt" ] && [ -d "src/moex_client" ]; then
        log_success "Структура проекта корректна"
    else
        log_error "Проблема со структурой проекта"
        return 1
    fi
}

# Вывод инструкций
show_next_steps() {
    echo ""
    log_success "🎉 Проект успешно настроен!"
    echo ""
    log_info "Следующие шаги:"
    echo "  1. Активируйте виртуальное окружение:"
    echo "     source venv/bin/activate"
    echo ""
    echo "  2. Отредактируйте файл .env и добавьте свои учетные данные MOEX:"
    echo "     nano .env"
    echo ""
    echo "  3. Запустите тесты:"
    echo "     pytest"
    echo ""
    echo "  4. Проверьте форматирование кода:"
    echo "     black src/ tests/"
    echo "     isort src/ tests/"
    echo ""
    log_info "Готово к разработке! 🚀"
}

# Основная функция
main() {
    echo "========================================"
    echo "  MOEX ISS Client - Setup Script"
    echo "========================================"
    echo ""
    
    check_python_version
    create_directories
    setup_virtual_environment
    install_dependencies
    setup_git
    setup_environment
    verify_setup
    show_next_steps
}

# Запуск скрипта
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi