""" Enables logging """

import logging

logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(
    # filename=path.join(BASE_DIR, 'OpenWeatherBot.log'),
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
)
