#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `coastviewer` package."""

import pytest

from click.testing import CliRunner

from coastviewer import coastviewer
from coastviewer import cli

from coastviewer import controllers

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')

@pytest.fixture
def client():
    """create a test app"""
    app = cli.make_app()
    with app.app.test_client() as client:
        yield client



def test_main(client):
    """test getting main page"""
    resp = client.get('/')
    assert resp.status_code == 200


def test_transects(client):
    """test getting transect information"""
    resp = client.get('/coastviewer/1.1.0/transects')
    assert resp.status_code == 200
    assert resp.content_type == 'application/json'


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert 'Show this message and exit.' in help_result.output
