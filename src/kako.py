#!/usr/bin/env python
''' Kako - Manifest driven IoT honeypots. '''

import os
import sys
import glob
import time
import logging
import logging.config
import multiprocessing
import yaml
import click

import kako


def run_processor(destination=None, configuration=None, results=None):
    ''' Attempts to run the given results processor, returning the process. '''
    executor = getattr(kako.processor, destination).Processor(
        configuration=configuration,
        results=results
    )
    executor.start()
    return executor

def run_simulation(manifest=None, configuration=None, results=None):
    ''' Attempts to run the given simulation, returning the process. '''
    executor = getattr(kako.simulation, manifest['protocol']).Simulation(
        manifest=manifest,
        configuration=configuration,
        results=results
    )
    executor.start()
    return executor


@click.command()
@click.option(
    '--configuration-file',
    help='Path to configuration file (YAML)',
    default='/etc/kako.yaml'
)
@click.option(
    '--simulation-path',
    help='Path to the directory containing simulations (YAML)',
    default=None
)
def main(configuration_file, simulation_path):
    ''' Kako - Manifest driven IoT honeypots. '''
    try:
        with open(configuration_file, 'r') as hndl:
            configuration = yaml.safe_load(hndl.read())
            kako.config.validate(configuration)
    except FileNotFoundError:
        print('[CRITICAL] No configuration could be loaded, cannot continue')
        sys.exit(-1)

    # Configure the logger.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s',
        filename=os.path.join(configuration['logging']['path'], 'kako.log')
    )
    log = logging.getLogger(__name__)

    # Build a results queue for simulation interactions to be spooled into
    # before pushing to the relevant results processor.
    log.info('Setting up a queue for results processing')
    results = multiprocessing.Queue()

    # Start and track results processors.
    log.info('Setting up results processor')
    try:
        processor = run_processor(
            destination=configuration['results']['processor'],
            configuration=configuration,
            results=results
        )
    except AttributeError as err:
        log.fatal('Unable to load results processor, cannot continue!')
        sys.exit(-2)

    # Hot patch the configuration to have the new simulation path if overridden.
    if simulation_path:
        configuration['simulations']['path'] = simulation_path

    # Locate and load all simulation manifests.
    manifests = []
    candidates = glob.glob(
        os.path.join(configuration['simulations']['path'], '*.yaml')
    )
    log.info(
        'Attempting to load simulations from %s',
        configuration['simulations']['path']
    )
    if len(candidates) == 0:
        log.fatal('No simulations could be loaded, cannot continue')
        sys.exit(-1)

    # Load and validate.
    for idx, candidate in enumerate(candidates):
        log.info(
            'Loading simulation %d of %d from manifest: %s',
            idx + 1,
            len(candidates),
            candidate
        )
        with open(candidate, 'r') as hndl:
            manifest = yaml.safe_load(hndl.read())
            kako.simulation.manifest.validate(manifest)
            manifests.append(manifest)

    # Start and track all simulations.
    simulations = dict()
    for idx, manifest in enumerate(manifests):
        log.info('Starting simulation: %s', manifest['name'])
        try:
            simulations[idx] = run_simulation(
                manifest=manifest,
                configuration=configuration,
                results=results
            )
        except AttributeError as err:
            log.error('Unable to load %s: %s', manifest['name'], err)
            continue

    # Start monitoring loop.
    if configuration['monitoring']['enabled']:
        log.info(
            'Monitoring enabled every %s seconds',
            configuration['monitoring']['interval']
        )
        while True:
            # Ensure simulations are alive.
            for idx, process in simulations.items():
                if not process.is_alive():
                    try:
                        log.error(
                            'simulation %s has died, respawning',
                            manifests[idx]['name']
                        )
                        simulations[idx] = run_simulation(
                            manifests[idx], configuration
                        )
                    except AttributeError as err:
                        log.error(
                            'Unable to load %s: %s', manifests[idx]['name'],
                            err
                        )
                        continue

            # Ensure results processor is alive.
            if not processor.is_alive():
                try:
                    log.error('Results processor has died, respawning')
                    processor = run_processor(
                        destination=configuration['results']['processor'],
                        configuration=configuration,
                        results=results
                    )
                except AttributeError as err:
                    log.fatal(
                        'Unable to load results processor, cannot continue!'
                    )
                    sys.exit(-2)

            # ...and wait.
            log.debug('Monitor run complete, sleeping before next run.')
            time.sleep(configuration['monitoring']['interval'])

if __name__ == '__main__':
    main()
