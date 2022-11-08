""" Functions for working with localization """

from json import loads
from os.path import isfile, join
from pathlib import Path


class Localization:
    """ A class for working with localization """

    def __init__(self, path: str, logger) -> None:
        """
        defines the path to the folder with the language files

        :param path: path to the folder with the language files
        :param logger: logger (object of logging.Logger class)
        """
        self._lang_folder = path
        self._logger = logger
        self._translate = self.init()

    def init(self) -> dict[str, dict[str, str]]:
        """
        Gathers language .json files into one dictionary, where key is language code,
        value is a nested dictionary with text fields and their values

        :return: nested dictionary used for bot dialog messages
        """
        try:
            if not isfile(join(self._lang_folder, 'en.json')):
                raise Exception('The default translation file en.json does not exist in the lang folder')
            dialogue_messages: dict[str, dict[str, str]] = {}
            for lang_file in Path(self._lang_folder).glob('*.json'):
                with open(file=lang_file, mode='r', encoding='utf-8') as file:
                    lang_file_content: str = file.read()
                    dialogue_messages.update(dict({str(lang_file)[-7:-5]: loads(lang_file_content)}))
            return dialogue_messages
        except Exception as ex:
            self._logger.critical('Error when gathering language files: %s', ex)
            self._logger.info('Bot stopped!')
            exit()

    async def get_translate(self, lang: str, translation: str) -> str:
        """
        Returns the bot's message in the language of the Telegram user interface

        :param lang: ISO 639-1 language code
        :param translation: dialog message
        :return: bot answer in the user's local language
        """
        try:
            return self._translate.get(lang).get(translation)
        except AttributeError:
            self._logger.error('No translation found for the %s language, EN was used', lang.upper())
            return self._translate.get('en').get(translation)
