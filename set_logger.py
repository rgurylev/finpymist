from settings import LOG_DIR

import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
#            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
             'format': "%(asctime)s %(name)s %(levelname)s %(message)s"
        },

    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'log_file_handler': {
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'examples.log',
            'formatter':  'standard',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'ERROR',
            'propagate': False
        },
        'finpymist': {
            'handlers': ['default', 'log_file_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}
logging.config.dictConfig(LOGGING_CONFIG)
