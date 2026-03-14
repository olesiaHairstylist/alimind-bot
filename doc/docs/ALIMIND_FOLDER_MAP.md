ALIMIND
FOLDER MAP

Status: PROJECT MAP
Purpose: Быстрая ориентация в структуре проекта.

1. Корень проекта
alimind_bot/

Главная папка системы.

Содержит:

bot/
data/
assets/
docs/
main.py
2. Главный файл запуска
main.py

Функции:

запуск Telegram-бота

подключение router

инициализация системы

Точка входа всей системы.

3. Папка bot
bot/

Главная папка кода.

Содержит:

core/
handlers/
city_events/
4. bot/core
bot/core/

Ядро системы.

Файлы:

registry.py
formatter.py
text.py
search.py
loader.py

Назначение:

registry.py

реестр всех объектов каталога.

formatter.py

форматирование карточек.

text.py

нормализация текстовых данных.

search.py

поиск по каталогу.

loader.py

загрузка объектов из JSON.

5. bot/handlers
bot/handlers/

Интерфейс Telegram-бота.

Файлы:

start.py
menu.py
city_today.py
emergency_contacts.py
card_sender.py
favorites.py
recents.py
start.py

Главное меню бота.

Функции:

стартовый экран

навигация

возврат в меню

menu.py

Каталог объектов.

Функции:

категории

списки объектов

пагинация

открытие карточек

city_today.py

События города.

Функции:

дежурные аптеки

отключения воды и электричества

emergency_contacts.py

Экстренные службы.

Функции:

отображение контактов

возврат в меню

card_sender.py

Отправка карточек объектов.

favorites.py

Избранные карточки.

recents.py

Последние просмотренные карточки.

6. bot/city_events
bot/city_events/

Модуль событий города.

Файлы:

storage.py
render.py
update.py
scheduler.py
storage.py

Работа с JSON событиями.

render.py

Формирование текста событий.

update.py

Обновление данных событий.

scheduler.py

Планировщик обновлений.

7. Папка data
data/

Все данные бота.

Структура:

data/
objects/
events/
8. data/objects
data/objects/

Каталог объектов.

Примеры файлов:

BEAUTY_01.json
CAFE_01.json
TAXI_01.json
SPORT_01.json

Каждый файл — карточка.

9. data/events
data/events/

События города.

Структура:

pharmacies/
electricity/
water/
emergency_contacts/
10. assets
assets/

Медиафайлы.

Примеры:

start.png

Используется для стартового экрана.

11. docs
docs/

Документация проекта.

Файлы:

NAVIGATION_REVISION_01.md
ALIMIND_SYSTEM_ARCHITECTURE.md
ALIMIND_FOLDER_MAP.md
12. Архитектурная схема

Проект построен по принципу:

INTERFACE
↓
LOGIC
↓
DATA

Где:

handlers → интерфейс
core → логика
data → данные
13. Принцип развития

Система строится так, чтобы новые модули можно было добавлять без изменения ядра.

Пример:

недвижимость
туризм
транспорт
медицина

Каждый модуль можно подключить как отдельный handler.

14. Текущее состояние
AliMind Bot
Core: Stable
Navigation: Stabilized
Architecture: Modular