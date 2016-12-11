#!/usr/bin/env python

import os
import yaml
import click
import logging
import logging.config

import multiprocessing

from kako import config
from kako import constant
from kako import simulation


@click.command()
@click.option('--configuration-file', help='Path to YAML configuration file.')
def main(configuration_file):
    ''' Kako. '''

    # Determine the configuration file to use.
    if configuration_file is None:
        configuration_file = os.path.join(
            os.path.dirname(__file__), constant.DEFAULT_CONFIGURATION_FILE
        )
    else:
        configuration_file = os.path.join(
            os.path.abspath(configuration_file)
        )

    # Read in the application configuration.
    with open(configuration_file, 'r') as f:
        configuration = yaml.safe_load(f.read())
        config.validate(configuration)

    # Configure the logger.
    log_path = os.path.join(configuration['logging']['path'], 'kako.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s',
        filename=log_path
    )

    # Attempt to load the configured simulation, and run it.
    log = logging.getLogger()

    for name in configuration['simulation']:
        log.info('Loading simulation: {}'.format(name))
        try:
            executor = getattr(simulation, name).Simulation(configuration)
        except AttributeError as x:
            log.error('Unable to load simulation {}: {}'.format(name, x))
            continue

        process = multiprocessing.Process(target=executor.run)
        process.start()


if __name__ == '__main__':
    main()
