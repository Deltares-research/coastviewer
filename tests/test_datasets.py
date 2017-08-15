#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `coastviewer` package."""

import pytest

from coastviewer import datasets

TRANSECTS = [7003900, 4000100]


def test_get_transect_data():
    """Test the CLI."""
    for id_ in TRANSECTS:
        data = datasets.get_transect_data(id_)


def test_get_nourishment_grid_df():
    for id_ in TRANSECTS:
        data = datasets.get_nourishment_grid_df()
