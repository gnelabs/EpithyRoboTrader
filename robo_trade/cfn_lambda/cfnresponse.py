"""
Python3 modified version of https://github.com/jorgebastida/cfn-response.
This module is normally only available for lambda ZipFile. Copying to use for general consumption for use in custom lambda build wrappers.
CFN-response provides success/fail responses for AWS CloudFormation custom resource triggers.
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-lambda-function-code.html#cfn-lambda-function-code-cfnresponsemodule
"""

__author__ = "Nathan Ward"

import json
import requests
from typing import Dict, Any, Optional

SUCCESS = "SUCCESS"
FAILED = "FAILED"

def send(event: Dict,
         context: Any,
         response_status: str,
         reason: Optional[None] = None,
         response_data: Optional[None] = None,
         physical_resource_id: Optional[None] = None) -> bool:
    response_data = response_data or {}
    response_body = json.dumps(
        {
            'Status': response_status,
            'Reason': reason or "See the details in CloudWatch Log Stream: " + context.log_stream_name,
            'PhysicalResourceId': physical_resource_id or context.log_stream_name,
            'StackId': event['StackId'],
            'RequestId': event['RequestId'],
            'LogicalResourceId': event['LogicalResourceId'],
            'Data': response_data
        }
    )
    
    headers = {
        'content-type': '',
        'content-length': str(len(response_body))
    }
    
    try:
        req = requests.put(event['ResponseURL'], data=response_body, headers=headers)
        if req.status_code != 200:
            return False
        else:
            return True
    except requests.exceptions.RequestException as e:
        print(e)
        return False