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
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/README.ru.md">
        <img align="right" src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/icons/flags/russia_24x24.png" alt="Ru">
    </a>
</p>

## Open Weather Bot

Телеграм-бот, який показує прогноз погоди.
Робоча версія доступна за посиланням [https://t.me/OpenWeatherSmartBot](https://t.me/OpenWeatherSmartBot)

### Можливості

* Пошук міста за назвою або координатами
* Показ поточної погоди та прогнозу на 24 години
* Оновлення прогнозу погоди кожні 3 години

### Установлення

```
git clone https://github.com/rin-gil/OpenWeatherBot.git
cd OpenWeatherBot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mv .env.dist .env
```

<img align="right" width="300" src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/projects/OpenWeatherBot/screenshot_ua.png" alt="Головний екран OpenWeatherBot">

### Налаштування та запуск

* Зареєструйте нового бота у [@BotFather](https://t.me/BotFather) і скопіюйте отриманий токен
* Вставте токен бота у файл .env
* Зареєструйте обліковий запис на сайті [OpenWeatherMap](https://home.openweathermap.org/users/sign_in)
* Створіть [API ключ](https://home.openweathermap.org/api_keys) і скопіюйте його у файл .env
* Вставте свій id Телеграм у файл .env
* Дізнатися свій id можна, наприклад, написавши боту [@getmyid_bot](https://t.me/getmyid_bot)
* Запуск бота через файл bot.py `python bot.py`

### Локалізація

* Бот автоматично визначає мову користувача, виходячи з налаштувань Телеграм
* Файли перекладу зберігаються в папці [/tgbot/lang](https://github.com/rin-gil/OpenWeatherBot/tree/master/tgbot/lang)
* Щоб додати свою мову, скопіюйте один із мовних файлів у папці та перейменуйте його відповідно до стандарту [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
* Переведіть рядки у файлі, збережіть його в папку [/tgbot/lang](https://github.com/rin-gil/OpenWeatherBot/tree/master/tgbot/lang) та перезапустіть бота

### Розробники

* [Ringil](https://github.com/rin-gil)

### Ліцензії

* Вихідний код **Open Weather Bot** доступний за ліцензією [MIT](https://github.com/rin-gil/OpenWeatherBot/blob/master/LICENCE)
* Дані про прогноз погоди надані сервісом [OpenWeather](https://openweathermap.org/)
* Іконки погоди від [www.wishforge.games](https://freeicons.io/profile/2257) c [freeicons.io](https://freeicons.io/)
