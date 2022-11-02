from json import loads
from pathlib import Path
from tgbot.config import LANGUAGES_DIR, logger


def _create_locale_from_language_files(path_to_lang_dir: str) -> dict[str, dict[str, str]]:
    """
    Gathers language .json files into one dictionary, where key is language code,
    value is a nested dictionary with text fields and their values

    :param path_to_lang_dir: Path to the folder with language files
    :return: Nested dictionary used for bot dialog messages
    """
    try:
        if not Path(f'{path_to_lang_dir}\\en.json').is_file():
            raise Exception('The default translation file en.json does not exist in the lang folder')
        dialogue_messages: dict[str, dict[str, str]] = {}
        for lang_file in Path(path_to_lang_dir).glob('*.json'):
            with open(file=lang_file, mode='r', encoding='utf-8') as file:
                lang_file_content: str = file.read()
                dialogue_messages.update(dict({str(lang_file)[-7:-5]: loads(lang_file_content)}))
        return dialogue_messages
    except Exception as ex:
        logger.critical(f'Error when gathering language files: {ex}')
        logger.info('Bot stopped!')
        exit()


_LOCALES: dict[str, dict[str, str]] = _create_locale_from_language_files(LANGUAGES_DIR)


def get_bot_message(language_code: str, bot_message: str) -> str:
    """
    Returns the bot's message in the language of the Telegram user interface

    :param language_code: language code
    :param bot_message: bot message
    :return: bot answer
    """
    try:
        return _LOCALES.get(language_code).get(bot_message)
    except AttributeError:
        logger.error(f'No translation found for the {language_code.upper()} language, EN was used')
        return _LOCALES.get('en').get(bot_message)
