# -*- coding: utf-8 -*-

"""Console script for ztm."""

# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging
import os
import pathlib
import time
from datetime import datetime
from pprint import pprint

import click
import requests
from backoff import expo, on_exception
from ratelimit import RateLimitException, limits

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)

log = logging.getLogger(__name__)


@click.group()
@click.option('--apikey', default=None)
@click.option('--sleep', default=10, help='Number of seconds to sleep between fetches')
@click.option('--continuous/--once', default=False, help='Fetch data in a loop')
@click.pass_context
def main(ctx, apikey, continuous, sleep):
    ctx.ensure_object(dict)
    ctx.obj['APIKEY'] = apikey or os.environ.get('APIKEY', default=None)
    ctx.obj['continuous'] = continuous
    ctx.obj['sleep'] = sleep


@main.command()
@click.option('--line', '-l', multiple=True)
@click.pass_context
def fetch(ctx, line):
    """Pobierz dane o pozycji wskazanej linii"""
    while True:
        _fetch_data(ctx, line)
        if not ctx.obj['continuous']:
            break
        time.sleep(ctx.obj['sleep'])


@on_exception(expo, RateLimitException, max_tries=8)
@limits(calls=3, period=30)
def _fetch_data(ctx, lines):
    for item in lines:
        # TODO: Merge logging with click.echo
        click.echo('{}: Fetching position for {}!'.format(datetime.now(), item))
        data = {
            'resource_id': 'f2e5503e927d-4ad3-9500-4ab9e55deb59',
            'apikey': ctx.obj['APIKEY'],
            'type': 1,
            'line': item,
        }
        url = "https://api.um.warszawa.pl/api/action/busestrams_get/"
        response = requests.get(url, params=data)
        data = response.json()
        click.echo(pprint(data))
        result = data['result']
        if isinstance(result, str):
            log.warning(result)
            continue
        append_data(result)


def append_data(data):
    import csv

    path = pathlib.Path('ztm.csv')
    data_file_exists = path.exists()
    fieldnames = ['Time', 'Lines', 'Brigade', 'Lat', 'Lon']
    with path.open('a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        if not data_file_exists:
            writer.writeheader()
        for item in data:
            writer.writerow(item)


if __name__ == '__main__':
    main(obj={})
