# Kako

![Kako](docs/images/kako.png?raw=true)

This project provides honeypots for a number of well known and deployed embedded device vulnerabilities.

This project is intended for use in cataloging attack sources, droppers and payloads. The default configuration will run a given set of simulations and capture information relating to the origin of the requests, the body of the request, and attempt to process and collect the payload - if supported.

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

Currently, Kako assumes that `boto3` is able to enumerate credentials to access the configured SNS and S3 resources without intervention. This may be via `~/.aws/credentials` file, IAM Instance Profiles (recommended), environment variables, or otherwise. There is currently no ability to provide AWS access keys directly.

### AWS Configuration

In order for Kako to operate properly, an SNS topic should be configured inside of AWS. The ARN for this topic will need to be provided as part of the Kako configuration, and a set of access-keys with permission to Publish to this SNS Topic ARN will be required to be present per the above section ('AWS API'). Further to this, the 'results->topic' attribute in the Kako configuration should be set to the ARN for this AWS SNS topic.

The output from the SNS Topic can be configured as desired. However, this has been successfully deployed using SNS to push messages into an SQS queue from which an external process consumes messages.

#### Policies

The following provides an example IAM policy which can be used to create and grant a user access to publish to the SNS topic - for use with Kako:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": [
                "arn:aws:sns:us-west-2:<ACCOUNT_NUMBER>:<SNS_TOPIC>"
            ]
        }
    ]
}
```

## Simulations

Simply put, simulations provide data light-weight 'emulation' of a given target. These are defined in YAML inside of the `simulations/` directory and will be linted, loaded and provisioned during Kako startup.

The following simulations are currently included:

* `000-LinuxTelnet.yaml` - Generic Telnet
  * Simulates a vulnerable telnet service (default credentials).
* `001-CPEServer.yaml` - CPEServer SOAP
  * Simulates a vulnerable CPEServer SOAP service (command injection).
* `002-NetGear.yaml` - NetGear HTTPS
  * Simulates a vulnerable NetGear router HTTPS web interface.
* `003-D-Link.yaml` - D-Link HTTP
  * Simulates a vulnerable D-Link router HTTP web interface.
* `004-Rompager.yaml` - Unknown RomPager
  * Simulates a vulnerable router RomPager HTTP interface.

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
* HTTPS
  * The same as HTTP but has an SSL listener though use of `ssl.wrap_socket()`.

The above servers can be easily extended to implement required functionality for the given vulnerable service. The two example simulations, discussed above in the `Simulations`, provide examples of how to extend the base classes to implement the required functionality.

### Installation

Installation and configuration of a new simulation can be performed in the following manner:

1. Create a new simulation YAML definition in `simulations/`.
2. Start / Restart Kako.
3. Done! :)

### SSL

For services that require SSL, such as NetGear remote management simulations, an SSL certificate is required. These can easily be generated with the following command:

```
# Windows.
openssl req -new -subj '//C=US\ST=California\L=San Jose\O=NETGEAR\OU=Home Consumer Products\CN=www.routerlogin.net' -x509 -keyout conf/routerlogin.pem -out conf/routerlogin.pem -days 3650 -nodes

# *Nix.
openssl req -new -subj '/C=US/ST=California/L=San Jose/O=NETGEAR/OU=Home Consumer Products/CN=www.routerlogin.net' -x509 -keyout conf/routerlogin.pem -out conf/routerlogin.pem -days 3650 -nodes
```

## FAQ

### Why not X, Y, Z already existing Honeypot project(s)?

This project was primarily developed as a learning exercise :)

It was developed in response to receiving a number of packet captures from production networks being probed by machines attempting to exploit a number of IoT vulnerabilities en masse. Although the captures contained information about the method(s) of infection - such as HTTP requests - the payloads themselves were missing. As a result a number of simulations were built and deployed in a number of regions in order to catalog and retrieve these payloads as well as document the associated origins and droppers for later analysis.

The use of AWS SQS / SNS on the back-end allows for easy deployment and aggregation of captures back into a central location (ElasticSearch) via HTTPS.

## Additional Reading

A basic Chef environment cookbook for deploying and configuring Kako can be found at the following URL:

* https://www.github.com/darkarnium/om-kako-env/
