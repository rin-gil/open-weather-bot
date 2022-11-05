""" Functions for working with localization """

from json import loads
from pathlib import Path

from tgbot.config import LANGUAGES_DIR, logger


def _create_locale_from_language_files(path_to_lang_dir: str) -> dict[str, dict[str, str]]:
    """
    Gathers language .json files into one dictionary, where key is language code,
    value is a nested dictionary with text fields and their values

    :param path_to_lang_dir: path to the folder with language files
    :return: nested dictionary used for bot dialog messages
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
        logger.critical('Error when gathering language files: %s', ex)
        logger.info('Bot stopped!')
        exit()


_LOCALES: dict[str, dict[str, str]] = _create_locale_from_language_files(LANGUAGES_DIR)


async def get_dialog_message_answer(user_language_code: str, dialog_message_name: str) -> str:
    """
    Returns the bot's message in the language of the Telegram user interface

    :param user_language_code: ISO 639-1 language code
    :param dialog_message_name: dialog message
    :return: bot dialog message answer
    """
    try:
        return _LOCALES.get(user_language_code).get(dialog_message_name)
    except AttributeError:
        logger.error('No translation found for the %s language, EN was used', user_language_code.upper())
        return _LOCALES.get('en').get(dialog_message_name)
