#!/usr/bin/env python3

import logging

import connexion

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.add_api('swagger.yaml', arguments={'title': 'This is the coastal-viewer api. It provides services to acquire data of coasts around the world'})
    app.run(port=8080)
