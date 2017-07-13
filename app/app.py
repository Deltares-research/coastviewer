#!/usr/bin/env python3

import logging

import connexion

logging.basicConfig(level=logging.DEBUG)


def make_app():
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'This is the coastal-viewer api. It provides services to acquire data of coasts around the world'})
    return app

app = make_app()

if __name__ == '__main__':
    app.run(port=8080)
