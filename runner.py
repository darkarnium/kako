''' Kako - Manifest driven IoT honeypots. '''

import os
import glob
import time
import logging
import logging.config
import multiprocessing
import yaml
import click

import kako


def run_simulation(manifest=None, configuration=None):
    ''' Attempts to run the given simulation, returning the process. '''
    executor = getattr(kako.simulation, manifest['protocol']).Simulation(
        manifest=manifest,
        configuration=configuration
    )
    process = multiprocessing.Process(target=executor.run)
    process.start()
    return process


@click.command()
@click.option('--configuration-file', help='Path to YAML configuration file.')
def main(configuration_file):
    ''' Kako - Manifest driven IoT honeypots. '''

    # Determine the configuration file to use.
    if configuration_file is None:
        configuration_file = os.path.join(
            os.path.dirname(__file__), kako.constant.DEFAULT_CONFIGURATION_FILE
        )
    else:
        configuration_file = os.path.join(
            os.path.abspath(configuration_file)
        )

    # Read in the application configuration.
    with open(configuration_file, 'r') as hndl:
        configuration = yaml.safe_load(hndl.read())
        kako.config.validate(configuration)

    # Configure the logger.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s',
        filename=os.path.join(configuration['logging']['path'], 'kako.log')
    )
    log = logging.getLogger(__name__)

    # Bring down the logger level(s) for boto to prevent log spam during AWS
    # operations - such as pushing messages to SNS.
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)

    # Locate and load all simulation manifests.
    manifests = []
    candidates = glob.glob(
        os.path.join(configuration['simulations']['path'], '*.yaml')
    )

    for candidate in candidates:
        log.info('Loading simulation from manifest: %s', candidate)

        with open(candidate, 'r') as hndl:
            manifest = yaml.safe_load(hndl.read())
            kako.simulation.manifest.validate(manifest)
            manifests.append(manifest)

    # Start and track all simulations.
    simulations = dict()
    for idx, manifest in enumerate(manifests):
        log.info('Starting simulation: %s', manifest['name'])
        try:
            simulations[idx] = run_simulation(manifest, configuration)
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
            for idx, process in simulations.iteritems():
                if not process.is_alive():
                    try:
                        log.error(
                            'simulation %s has died, respawning',
                            simulations[idx]['name']
                        )
                        simulations[idx] = run_simulation(
                            simulations[idx], configuration
                        )
                    except AttributeError as err:
                        log.error(
                            'Unable to load %s: %s', simulations[idx]['name'],
                            err
                        )
                        continue

            # ...and wait.
            log.debug('Monitor run complete, sleeping before next run.')
            time.sleep(configuration['monitoring']['interval'])

if __name__ == '__main__':
    main()
