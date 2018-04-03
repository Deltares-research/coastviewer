# -*- coding: utf-8 -*-

"""Console script for coastviewer."""

import logging
import functools

import click
import connexion

import flask
from . import controllers
from . import ee_controllers

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def make_app():
    """create the main application"""
    app = connexion.App(__name__, specification_dir='./swagger/')
    title = """
    This is the coastal-viewer api.
    It provides services to acquire data of coasts around the world.
    """
    api = app.add_api(
        'swagger.yaml',
        arguments={
            'title': title
        }
    )

    logger.debug(api)

    # make sure the function keeps the __name__ 'index' and __docs__
    index = functools.wraps(controllers.index)(
        # already fill in the api parameter
        functools.partial(controllers.index, api=api)
    )
    app.add_url_rule('/', 'index', index)
    static = flask.Blueprint('static', __name__, static_folder='static')
    app.app.register_blueprint(static)
    app.app.register_blueprint(ee_controllers.ee_pages)
    return app


@click.command()
@click.option(
    '--debug/--no-debug',
    default=False,
    help='Start application in debugger mode.'
)
def main(debug, args=None):
    """Console script for coastviewer."""
    # configure logging
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    app = make_app()
    app.run(debug=debug)


if __name__ == "__main__":
    main()
