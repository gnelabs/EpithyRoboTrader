DEPRECATED

# EpithyRoboTrader

Serverless stock trader for Robinhood built on AWS. In development.

## Prerequisites

### SAM CLI

This package assumes you have the SAM CLI installed on your developer instance. See: https://github.com/awsdocs/aws-sam-developer-guide/blob/master/doc_source/serverless-sam-cli-install-linux.md

### Docker (For testing and development)

If you want to test and develop, you're going to want docker to be installed so you can run the local lambda docker container. This will allow you to run sam local commands. See: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install-linux.html#serverless-sam-cli-install-linux-docker

## Usage

Build.

``` bash
# Resolve dependencies and create a .aws-sam/build/ directory.
$ sam build
```

Deploy to cloudformation. Use --guided for the initial install to setup your S3 bucket and what not.

``` bash
# Deploy the application. Use the guided method so you can fill in information about your S3 bucket and region.
$ sam deploy --guided
```
## Testing

Build dependencies for local container testing. The --use-container command is needed to give the build directory proper permissions for docker lambda to read.

``` bash
# Build inside the local container.
$ sam build --use-container
```

Execute whatever function locally. Useful for verifying lambdas work and staying out of cloudformation purgatory.

``` bash
# Run the lambda function locally as an integration test.
$ sam local invoke CreateDefaultCognitoUserLambda
```

Example: start API gateway locally.

``` bash
# Run local api gateway endpoint.
$ sam local start-api
```
