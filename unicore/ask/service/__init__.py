from pyramid.config import Configurator
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)

    # sqlalchemy setup
    config.scan('%s.models' % __name__)
    config.scan('%s.questions_api' % __name__)
    return config.make_wsgi_app()
