<p align="center">
    <img src="https://repository-images.githubusercontent.com/559574279/ac1f8317-c07c-4c0f-a4e4-c49ae01237cd" alt="Open Weather Bot" width="640">
</p>

<p align="center">
    <a href="https://www.python.org/downloads/release/python-3108/">
        <img src="https://img.shields.io/badge/python-v3.10-informational" alt="python version">
    </a>
    <a href="https://pypi.org/project/aiogram/2.25.1/">
        <img src="https://img.shields.io/badge/aiogram-v2.25.1-informational" alt="aiogram version">
    </a>
    <a href="https://pypi.org/project/aiohttp/3.8.3/">
        <img src="https://img.shields.io/badge/aiohttp-v3.8.3-informational" alt="aiohttp version">
    </a>
    <a href="https://pypi.org/project/aiosqlite/0.19.0/">
        <img src="https://img.shields.io/badge/aiosqlite-v0.19.0-informational" alt="aiosqlite version">
    </a>
    <a href="https://pypi.org/project/APScheduler/3.10.1/">
        <img src="https://img.shields.io/badge/APScheduler-v3.10.1-informational" alt="APScheduler version">
    </a>
    <a href="https://pypi.org/project/environs/9.5.0/">
        <img src="https://img.shields.io/badge/environs-v9.5.0-informational" alt="environs version">
    </a>
    <a href="https://pypi.org/project/Pillow/10.0.0/">
        <img src="https://img.shields.io/badge/Pillow-v10.0.0-informational" alt="Pillow version">
    </a>
    <a href="https://pypi.org/project/tzlocal/5.0.1/">
        <img src="https://img.shields.io/badge/tzlocal-v5.0.1-informational" alt="tzlocal version">
    </a>
    <a href="https://github.com/psf/black">
        <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-black.svg">
    </a>
    <a href="https://github.com/rin-gil/OpenWeatherBot/actions/workflows/tests.yml">
        <img src="https://github.com/rin-gil/OpenWeatherBot/actions/workflows/tests.yml/badge.svg" alt="Code tests">
    </a>
    <a href="https://github.com/rin-gil/OpenWeatherBot/actions/workflows/codeql.yml">
        <img src="https://github.com/rin-gil/OpenWeatherBot/actions/workflows/codeql.yml/badge.svg" alt="Code tests">
    </a>
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/LICENCE">
        <img src="https://img.shields.io/badge/licence-MIT-success" alt="MIT licence">
    </a>
</p>

<p align="right">
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/README.md">
        <img src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/icons/flags/united-kingdom_24x24.png" alt="En"></a>
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/README.ua.md">
        <img src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/icons/flags/ukraine_24x24.png" alt="Ua">
    </a>
</p>

## Open Weather Bot

Телеграм бот, показывающий прогноз погоды.
Рабочая версия доступна по ссылке [@OpenWeatherSmartBot](https://t.me/OpenWeatherSmartBot)

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

* С версии 1.1.0 в бот добавлена локализация для английского, украинского и русского языка
* Для добавления перевода на свой язык, сделайте следующее:
  1. перейдите в папку с ботом
  2. активируйте виртуальное окружение:

     `source venv/bin/activate`
  3. создайте файл перевода на ваш язык, где **{language}** - код языка по стандарту [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

     `pybabel init --input-file=tgbot/locales/tgbot.pot --output-dir=tgbot/locales --domain=tgbot --locale={language}`
  4. переведите строки в файле **locales/{language}/LC_MESSAGES/tgbot.po**
  5. скомпилируйте перевод командой:

     `pybabel compile --directory=tgbot/locales --domain=tgbot`
  6. перезапустите бота
* При изменениях строк для перевода в коде, вам нужно будет полностью пересоздать и скомпилировать файлы 
  перевода для всех локализаций:
  1. извлечь строки для перевода из кода:

     `pybabel extract --input-dirs=./tgbot --output-file=tgbot/locales/tgbot.pot --sort-by-file --project=OpenWeatherBot`
  2. создать файлы перевода для всех локализаций:

     `pybabel init --input-file=tgbot/locales/tgbot.pot --output-dir=tgbot/locales --domain=tgbot --locale={language}`
  3. скомпилировать переводы:

     `pybabel compile --directory=tgbot/locales --domain=tgbot`
* Более подробно об этом можно прочитать в примере из документации [aiogram](https://docs.aiogram.dev/en/latest/examples/i18n_example.html)

### Разработчики

* [Ringil](https://github.com/rin-gil)

### Лицензии

* Исходный код **Open Weather Bot** доступен по лицензии [MIT](https://github.com/rin-gil/OpenWeatherBot/blob/master/LICENCE)
* Данные о прогнозе погоды предоставлены сервисом [OpenWeather](https://openweathermap.org/)
* Иконки погоды от [www.wishforge.games](https://freeicons.io/profile/2257) c [freeicons.io](https://freeicons.io/)
