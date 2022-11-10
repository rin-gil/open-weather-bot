<p align="center">
    <img src="https://repository-images.githubusercontent.com/559574279/ac1f8317-c07c-4c0f-a4e4-c49ae01237cd" alt="Open Weather Bot" width="640">
</p>

<p align="center">
    <a href="https://www.python.org/downloads/release/python-3108/"><img src="https://img.shields.io/badge/python-v3.10-informational" alt="python version"></a>
    <a href="https://pypi.org/project/aiogram/2.22.1/"><img src="https://img.shields.io/badge/aiogram-2.22.1-informational" alt="aiogram version"></a>
    <a href="https://pypi.org/project/aiohttp/3.8.1/"><img src="https://img.shields.io/badge/aiohttp-3.8.1-informational" alt="aiohttp version"></a>
    <a href="https://pypi.org/project/aioschedule/0.5.2/"><img src="https://img.shields.io/badge/aioschedule-0.5.2-informational" alt="aioschedule version"></a>
    <a href="https://pypi.org/project/aiosqlite/0.17.0/"><img src="https://img.shields.io/badge/aiosqlite-0.17.0-informational" alt="aiosqlite version"></a>
    <a href="https://pypi.org/project/environs/9.5.0/"><img src="https://img.shields.io/badge/environs-v9.5.0-informational" alt="environs version"></a>
    <a href="https://pypi.org/project/Pillow/9.3.0/"><img src="https://img.shields.io/badge/Pillow-v9.3.0-informational" alt="Pillow version"></a>
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/LICENCE"><img src="https://img.shields.io/badge/licence-MIT-success" alt="MIT licence"></a>
</p>

<p align="right">
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/README.ru.md">
        <img align="right" src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/icons/flags/russia_24x24.png" alt="Ru"></a>
    <a href="https://github.com/rin-gil/OpenWeatherBot/blob/master/README.ua.md">
        <img align="right" src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/icons/flags/ukraine_24x24.png" alt="Ua">
    </a>
</p>

## Open Weather Bot

Telegram bot that shows the weather forecast.
The working version is available at [https://t.me/OpenWeatherSmartBot](https://t.me/OpenWeatherSmartBot)

### Features

* City search by name or coordinates
* 24-hour weather and forecast display
* Updating weather forecast every 3 hours

### Installation

```
git clone https://github.com/rin-gil/OpenWeatherBot.git
cd OpenWeatherBot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mv .env.dist .env
```

<img align="right" width="200" src="https://raw.githubusercontent.com/rin-gil/rin-gil/main/assets/img/projects/OpenWeatherBot/screenshot_en.png" alt="OpenWeatherBot home screen">

### Setup and run

* Register a new bot with [@BotFather](https://t.me/BotFather) and copy the received token
* Paste the bot's token into the .env file
* Register an account at [OpenWeatherMap](https://home.openweathermap.org/users/sign_in)
* Create [API key](https://home.openweathermap.org/api_keys) and copy it to .env file
* Paste your Telegram id into the .env file
* Find out your id, for example, by writing bot [@getmyid_bot](https://t.me/getmyid_bot)
* Launch the bot via the bot.py file `python bot.py`

### Localization

* Bot automatically detects user language based on Telegram settings
* Translation files are stored in the [/tgbot/lang](https://github.com/rin-gil/OpenWeatherBot/tree/master/tgbot/lang) folder
* To add your language, copy one of the language files in the folder and rename it according to the standard [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
* Translate lines in the file, save it in the [/tgbot/lang](https://github.com/rin-gil/OpenWeatherBot/tree/master/tgbot/lang) folder and restart the bot

### Developers

* [Ringil](https://github.com/rin-gil)

### Licenses

* The source code of **Open Weather Bot** is available under the [MIT](https://github.com/rin-gil/OpenWeatherBot/blob/master/LICENCE) license
* Weather data provided by [OpenWeather](https://openweathermap.org/)
* Weather icons by [www.wishforge.games](https://freeicons.io/profile/2257) on [freeicons.io](https://freeicons.io/)
