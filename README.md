# Kako

This project provides honeypots for a number of well known and deployed embedded device vulnerabilities. This project is intended for use in cataloging attack sources, droppers and payloads.

The default configuration will run a given set of simulations and capture information relating to the origin of the requests, the body of the request, and attempt to process and collect the payload - if supported.

## Disclaimer

This code is so pre-alpha it hurts; expect problems! :fire:

## Dependencies

The following Python packages are required for Kako to function correctly:

* `click` - Command-line argument processing.
* `boto3` - Amazon AWS integration.
* `requests` - HTTP request library.
* `cerberus` - Validation of messages and other documents.

Once these modules are installed, a valid configuration file is required. See the **Configuration** section for more information.

## Configuration

The configuration for Kako is performed via a YAML document - named `kako.yaml` by default. An example configuration ships with Kako and is named `kako.dist.yaml`.

### AWS API

Currently, Kako assumes that `boto3` is able to enumerate credentials to access the configured SNS and S3 resources without intervention. This may be via `~/.aws/credentials` file, IAM Instance Profiles (recommended), environment variables, or otherwise. This is done to encourage the use of IAM Instance Profiles, rather than generating AWS access keys and placing them into unencrypted text files.

There is currently no ability to provide AWS access keys directly.

## Simulations

Simply put, simulations provide data light-weight 'emulation' of a given target. These simulations are loaded by Kako by instantiating a class from the given simulation file (always named `Simulation`), and run by calling the run method (always named `run`).

The following simulations are currently included:

* Mirai - CPEServer SOAP
  * Simulates a vulnerable CPEServer SOAP service (command injection).
* Mirai - Generic Telnet
  * Simulates a vulnerable telnet service (default credentials).
* Unknown - D-Link HTTP
  * Simulates a vulnerable D-Link router HTTP web interface.
* Unknown - NetGear HTTPS
  * Simulates a vulnerable NetGear router HTTPS web interface.

## Servers

In order to simplify implementation of a new simulation, a number of servers are included. These servers implement the minimum required functionality to bind sockets, accept connections and read / write to the client.

The following servers are currently included:

* Telnet
  * Accepts any username / password pair for login.
  * Simulates a `BusyBox` telnet service with basic shell commands.
  * Records full interaction on disconnect / exit - via `capture()`.
* HTTP
  * Simulates a `uhttpd` HTTP service with no routes.
  * Records request on server response - via `capture()`.
  * This can be turned into an SSL listener though use of `ssl.wrap_socket()`.

The above servers can be easily extended to implement required functionality for the given vulnerable service. The two example simulations, discussed above in the `Simulations`, provide examples of how to extend the base classes to implement the required functionality.

### Installation

Installation and configuration of a new simulation can be performed in the following manner:

1. Install required Python dependencies for the new module.
2. Install / create the file into the `kako/simulation/` directory (eg. `generic_http_sample.py`).
3. Add the module into `kako.simulation` as an import inside of `__init__` (eg. `from . import generic_http_sample`).
4. Add the new module into the Kako configuration - under the `simulation` section.

### SSL

For services that require SSL, such as NetGear remote management simulations, an SSL certificate is required. These can easily be generated with the following command:

```
# Windows.
openssl req -new -subj '//C=US\ST=California\L=San Jose\O=NETGEAR\OU=Home Consumer Products\CN=www.routerlogin.net' -x509 -keyout conf/routerlogin.pem -out conf/routerlogin.pem -days 3650 -nodes

# *Nix.
openssl req -new -subj '/C=US/ST=California/L=San Jose/O=NETGEAR/OU=Home Consumer Products/CN=www.routerlogin.net' -x509 -keyout conf/routerlogin.pem -out conf/routerlogin.pem -days 3650 -nodes
```

## FAQ

### ...But why?

This project was developed in response to receiving a number of packet captures from production networks being probed by machines attempting to exploit a number of IoT vulnerabilities en masse. Although the captures contained information about the method(s) of infection - such as HTTP requests - the payloads themselves were missing.

As a result a number of simulations were built and deployed into Amazon Web Services (AWS) in order to catalog and retrieve these payloads as well as document the associated origins and droppers for later analysis.

## Additional Reading

A basic Chef environment cookbook for deploying and configuring Kako can be found at the following URL:

* https://www.github.com/darkarnium/kako-env/
