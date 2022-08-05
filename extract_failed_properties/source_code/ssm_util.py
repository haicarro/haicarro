import boto3
import json 
import logging
logging.getLogger().setLevel(logging.INFO)


def get_secret_from_ssm(param_name) :
    logging.debug('Start get_secret_from_ssm')
    client = boto3.client('ssm')
    response = client.get_parameter(
        Name=param_name,
        WithDecryption = True,
    )
    response_body = response['Parameter']['Value']
    logging.info('Finished get_secret_from_ssm')
    return response_body

def get_secret_from_ssm_in_vpc(param_name) :
    logging.debug('Start get_secret_from_ssm')
    # Ref https://frankcorso.dev/passing-credentials-aws-lambda-parameter-store.html
    client = boto3.client('lambda')
    payload = {
        "name": param_name,
    }
    response = client.invoke(
        FunctionName='get_from_ssm',
        Payload = json.dumps(payload)
    )
    response_body = response['Payload'].read().decode('utf-8')[1:-1]
    logging.info('Finished get_secret_from_ssm')
    return response_body