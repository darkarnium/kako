![](https://github.com/darkarnium/kako/raw/master/docs/images/kako.png?raw=true)

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

The configuration for Kako is performed via a YAML document - named `kako.yaml` by default.

## Output

Two output formats are supported by Kako at this time: AWS SNS, and flat-file JSON. The former is intended for environments which may be part of a wider distributed deployment, whereas the latter allows for easy integration into existing environments which may also collect other honeypot logs from disk via something like Logstash.

### File (JSON)

Generates a new JSON document for each captured interaction with the honeypot, this is then appended to a file in the provided destination directory. Each line of this file should be processed as a new JSON document, as writing a new file per interaction can quickly yield a massive number of small documents on disk.

### AWS SNS

For use with SNS output, Kako assumes that `boto3` is able to enumerate credentials to access the configured SNS and S3 resources without intervention. This may be via `~/.aws/credentials` file, IAM Instance Profiles (when deployed in AWS), environment variables, or otherwise.

There is currently no ability to provide AWS access keys directly.

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

A number of example simulations can be found in the following repository:

* https://www.github.com/darkarnium/kako-simulations/

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

The above servers can also be extended without too much effort to implement required functionality for the given vulnerable service.

### Installation

Installation and configuration of a new simulation can be performed in the following manner:

1. Add a new simulation into the configured simulation directory - with a file suffix of `.yaml`.
2. Start / Restart Kako.
3. Done! :)

### SSL

For services that require SSL an SSL certificate and private key are required. These can easily be generated with the following command:

```
openssl req -new -subj '/C=US/ST=California/L=San Jose/O=NETGEAR/OU=Home Consumer Products/CN=www.routerlogin.net' \
  -x509 -keyout conf/routerlogin.pem -out conf/routerlogin.pem -days 3650 -nodes
```

## FAQ

### Why not X, Y, Z already existing Honeypot project(s)?

This project was primarily developed as a learning exercise :)

It was developed in response to receiving a number of packet captures from production networks being probed by machines attempting to exploit a number of IoT vulnerabilities en masse. Although the captures contained information about the method(s) of infection - such as HTTP requests - the payloads themselves were missing. As a result a number of simulations were built and deployed in a number of regions in order to catalog and retrieve these payloads as well as document the associated origins and droppers for later analysis.

The use of AWS SQS / SNS on the back-end allows for easy deployment and aggregation of captures back into a central location (ElasticSearch) via HTTPS.

## Additional Reading

* Example and common Kako simulations
    * https://www.github.com/darkarnium/kako-simulations/
* Ogawa project for consuming data from AWS SQS into ElasticSearch.
    * https://www.github.com/darkarnium/ogawa/
