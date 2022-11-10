<p align="center">
    <img src="https://repository-images.githubusercontent.com/559574279/ac1f8317-c07c-4c0f-a4e4-c49ae01237cd" alt="Open Weather Bot" width="640">
</p>

<p align="center">
    <a href="https://www.python.org/downloads/release/python-3108/"><img src="https://img.shields.io/badge/python-v3.10-informational" alt="python version"></a>
    <a href="https://pypi.org/project/aiogram/2.22.1/"><img src="https://img.shields.io/badge/aiogram-v2.22.1-informational" alt="aiogram version"></a>
    <a href="https://pypi.org/project/aiohttp/3.8.1/"><img src="https://img.shields.io/badge/aiohttp-v3.8.1-informational" alt="aiohttp version"></a>
    <a href="https://pypi.org/project/aioschedule/0.5.2/"><img src="https://img.shields.io/badge/aioschedule-v0.5.2-informational" alt="aioschedule version"></a>
    <a href="https://pypi.org/project/aiosqlite/0.17.0/"><img src="https://img.shields.io/badge/aiosqlite-v0.17.0-informational" alt="aiosqlite version"></a>
    <a href="https://pypi.org/project/environs/9.5.0/"><img src="https://img.shields.io/badge/environs-v9.5.0-informational" alt="environs version"></a>
    <a href="https://pypi.org/project/Pillow/9.3.0/"><img src="https://img.shields.io/badge/Pillow-v9.3.0-informational" alt="Pillow version"></a>
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/LICENCE"><img src="https://img.shields.io/badge/licence-MIT-success" alt="MIT licence"></a>
</p>

<p align="right">
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/README.md">
        <img align="right" src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/icons/flags/united-kingdom_24x24.png" alt="En"></a>
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/README.ua.md">
        <img align="right" src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/icons/flags/ukraine_24x24.png" alt="Ua">
    </a>
</p>

## Open Weather Bot

Телеграм бот, показывающий прогноз погоды.
Рабочая версия доступна по ссылке [https://t.me/OpenWeatherSmartBot](https://t.me/OpenWeatherSmartBot)

### Возможности

* Поиск города по названию или координатам
* Показ текущей погоды и прогноза на 24 часа
* Обновление прогноза погоды каждые 3 часа

### Установка

```
git clone https://github.com/rin-gil/OpenWeatherBot.git
cd OpenWeatherBot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mv .env.dist .env
```

<img align="right" width="300" src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/projects/OpenWeatherBot/screenshot_ru.png" alt="Главный экран OpenWeatherBot">

### Настройка и запуск

* Зарегистрируйте нового бота у [@BotFather](https://t.me/BotFather) и скопируйте полученный токен
* Вставьте токен бота в файл .env
* Зарегистрируйте учетную запись на сайте [OpenWeatherMap](https://home.openweathermap.org/users/sign_in)
* Создайте [API ключ](https://home.openweathermap.org/api_keys) и скопируйте его в файл .env
* Вставьте свой id Телеграм в файл .env
* Узнать свой id можно, например, написав боту [@getmyid_bot](https://t.me/getmyid_bot)
* Запуск бота через файл bot.py `python bot.py`

### Локализация

* Бот автоматически определяет язык пользователя, исходя из настроек Телеграм
* Файлы перевода хранятся в папке [/tgbot/lang](https://github.com/rin-gil/OpenWeatherBot/tree/master/tgbot/lang)
* Чтобы добавить свой язык, скопируйте один из языковых файлов в папке и переименуйте его в соответствии со стандартом [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
* Переведите строки в файле, сохраните его в папку [/tgbot/lang](https://github.com/rin-gil/OpenWeatherBot/tree/master/tgbot/lang) и перезапустите бота

### Разработчики

* [Ringil](https://github.com/rin-gil)

### Лицензии

* Исходный код **Open Weather Bot** доступен по лицензии [MIT](https://github.com/rin-gil/OpenWeatherBot/blob/master/LICENCE)
* Данные о прогнозе погоды предоставлены сервисом [OpenWeather](https://openweathermap.org/)
* Иконки погоды от [www.wishforge.games](https://freeicons.io/profile/2257) c [freeicons.io](https://freeicons.io/)
