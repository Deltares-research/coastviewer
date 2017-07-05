import logging

import connexion
import geojson
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
    return datasets.jarkus.kml_overview()
