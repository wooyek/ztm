# -*- coding: utf-8 -*-

"""Console script for ztm."""

# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging
import os
import pathlib

import click
import requests

log = logging.getLogger(__name__)


@click.group()
@click.option('--apikey', default=None)
@click.pass_context
def main(ctx, apikey):
    ctx.ensure_object(dict)
    ctx.obj['APIKEY'] = apikey or os.environ.get('APIKEY', default=None) or '58013e79-70ba-427d-be89-0bae95c53d40'


@main.command()
@click.option('--line', '-l', multiple=True)
@click.pass_context
def fetch(ctx, line):
    """Pobierz dane o pozycji wskazanej linii"""
    for item in line:
        click.echo('Fetching position for %s!' % item)
        data = {
            'resource_id': 'f2e5503e927d-4ad3-9500-4ab9e55deb59',
            'apikey': ctx.obj['APIKEY'],
            'type': 1,
            'line': item,
        }
        url = "https://api.um.warszawa.pl/api/action/busestrams_get/"
        response = requests.get(url, params=data)
        data = response.json()
        click.echo(data)
        append_data(data['result'])


def append_data(data):
    import csv

    path = pathlib.Path('ztm.csv')
    data_file_exists = path.exists()
    fieldnames = ['Time', 'Lines', 'Brigade', 'Lat', 'Lon']
    with path.open('a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not data_file_exists:
            writer.writeheader()
        for item in data:
            writer.writerow(item)


if __name__ == '__main__':
    main(obj={})
