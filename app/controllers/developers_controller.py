import logging

import flask

import datasets.jarkus

logger = logging.getLogger(__name__)


def transect(id) -> object:
    logger.info(flask.request)
    return {}


def transect_kml(id) -> str:
    return "<kml></kml>"


def transect_overview() -> list:
    logger.info(flask.request)
    return []


def transect_overview_kml() -> str:
    lines = datasets.jarkus.overview()
    return flask.render_template('lod.kml', lines=lines)
