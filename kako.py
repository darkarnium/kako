#!/usr/bin/env python2.7

import os
import time
import yaml
import click
import logging
import logging.config

import multiprocessing

from kako import config
from kako import constant
from kako import simulation


def run_simulation(name=None, configuration=None):
    ''' Attempts to run the given simulation, returning the process. '''
    executor = getattr(simulation, name).Simulation(configuration)
    process = multiprocessing.Process(target=executor.run)
    process.start()
    return process


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
    running = {}
    for name in configuration['simulation']:
        log.info('Loading simulation: {}'.format(name))
        try:
            running[name] = run_simulation(name, configuration)
        except AttributeError as x:
            log.error('Unable to load simulation {}: {}'.format(name, x))
            continue

    # Start monitoring loop.
    if configuration['monitoring']['enabled']:
        log.info(
            'Monitoring enabled every {} seconds'.format(
                configuration['monitoring']['interval']
            )
        )
        while True:
            for name, simulation in running:
                if not simulation.is_alive():
                    try:
                        log.error('{} died, respawning'.format(name))
                        running[name] = run_simulation(name, configuration)
                    except AttributeError as x:
                        log.error('Unable to load simulation {}: {}'.format(
                            name, x
                        ))
                        continue

            log.debug('Monitor run complete, sleeping before next run.')
            time.sleep(configuration['monitoring']['interval'])

if __name__ == '__main__':
    main()
