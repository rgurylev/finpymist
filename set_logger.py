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
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'log_file_handler': {
            'class': 'logging.FileHandler',
            'filename': 'examples.log',
            'formatter': 'standard',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        'bonds': {
            'handlers': ['default', 'log_file_handler'],
            'level': 'INFO',
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
