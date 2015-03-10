import os
from ConfigParser import ConfigParser
from unittest import TestCase

from webtest import TestApp

from unicore.hub.service import main


config_file_path = os.path.join(os.path.dirname(__file__), 'test.ini')


def get_test_settings():
    here = os.path.dirname(__file__)
    config = ConfigParser()
    config.read(config_file_path)
    settings = dict(config.items('app:unicore.hub.service',
                                 vars={'here': here}))
    return (here, config_file_path, settings)


def make_app(working_dir, config_file_path, settings,
             extra_environ={}):
    app = TestApp(main({
        '__file__': config_file_path,
        'here': working_dir,
    }, **settings), extra_environ=extra_environ)
    return app


class BaseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        # set up app
        working_dir, config_file_path, settings = get_test_settings()
        cls.working_dir = working_dir
        cls.config_file_path = config_file_path
        cls.settings = settings
        cls.app = make_app(
            working_dir=working_dir,
            config_file_path=config_file_path,
            settings=settings)
