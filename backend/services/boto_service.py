import time

import boto3
from botocore.config import Config
from botocore.exceptions import (
    BotoCoreError,
    ClientError,
    ConnectTimeoutError,
    EndpointConnectionError,
    ReadTimeoutError
)


class BotoService:

    def __init__(self):
        config = Config(
            connect_timeout=10,
            read_timeout=20,
            retries={
                "max_attempts": 2,
                "mode": "standard"
            }
        )

        self.session = boto3.Session()
        self.region = self.session.region_name or "ap-south-1"
        self.config = config

    def get_client(self, service_name):
        return self.session.client(
            service_name,
            region_name=self.region,
            config=self.config
        )

    def execute(
        self,
        service_name,
        operation,
        retries=2,
        retry_delay=1,
        **kwargs
    ):
        last_error = None

        for attempt in range(1, retries + 1):

            try:
                client = self.get_client(service_name)

                method = getattr(client, operation)
                result = method(**kwargs)

                return {
                    "success": True,
                    "method": "boto3",
                    "service": service_name,
                    "operation": operation,
                    "region": self.region,
                    "attempt": attempt,
                    "result": result
                }

            except (
                ConnectTimeoutError,
                ReadTimeoutError,
                EndpointConnectionError
            ) as e:

                last_error = str(e)

                if attempt < retries:
                    time.sleep(retry_delay)
                    continue

                return {
                    "success": False,
                    "method": "boto3",
                    "service": service_name,
                    "operation": operation,
                    "region": self.region,
                    "error_type": "timeout_or_connection",
                    "error": last_error,
                    "attempts": attempt
                }

            except ClientError as e:

                return {
                    "success": False,
                    "method": "boto3",
                    "service": service_name,
                    "operation": operation,
                    "region": self.region,
                    "error_type": "aws_client_error",
                    "error": str(e),
                    "attempts": attempt
                }

            except BotoCoreError as e:

                last_error = str(e)

                if attempt < retries:
                    time.sleep(retry_delay)
                    continue

                return {
                    "success": False,
                    "method": "boto3",
                    "service": service_name,
                    "operation": operation,
                    "region": self.region,
                    "error_type": "boto_core_error",
                    "error": last_error,
                    "attempts": attempt
                }

            except Exception as e:

                return {
                    "success": False,
                    "method": "boto3",
                    "service": service_name,
                    "operation": operation,
                    "region": self.region,
                    "error_type": "unexpected_error",
                    "error": str(e),
                    "attempts": attempt
                }

        return {
            "success": False,
            "method": "boto3",
            "service": service_name,
            "operation": operation,
            "region": self.region,
            "error_type": "unknown",
            "error": last_error or "Unknown AWS error",
            "attempts": retries
        }


class S3Service:

    def __init__(self):
        self.boto = BotoService()
        self.region = self.boto.region

    def create_bucket(self, bucket_name):
        kwargs = {
            "Bucket": bucket_name
        }

        if self.region != "us-east-1":
            kwargs["CreateBucketConfiguration"] = {
                "LocationConstraint": self.region
            }

        return self.boto.execute(
            "s3",
            "create_bucket",
            **kwargs
        )

    def check_bucket(self, bucket_name):
        return self.boto.execute(
            "s3",
            "head_bucket",
            Bucket=bucket_name
        )

    def list_buckets(self):
        return self.boto.execute(
            "s3",
            "list_buckets"
        )


class DynamoDBService:

    def __init__(self):
        self.boto = BotoService()
        self.region = self.boto.region

    def list_tables(self):
        return self.boto.execute(
            "dynamodb",
            "list_tables"
        )

    def describe_table(self, table_name):
        return self.boto.execute(
            "dynamodb",
            "describe_table",
            TableName=table_name
        )

    def create_table(
        self,
        table_name,
        key_name="id",
        key_type="S",
        billing_mode="PAY_PER_REQUEST"
    ):
        return self.boto.execute(
            "dynamodb",
            "create_table",
            TableName=table_name,
            KeySchema=[
                {
                    "AttributeName": key_name,
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": key_name,
                    "AttributeType": key_type
                }
            ],
            BillingMode=billing_mode
        )

    def delete_table(self, table_name):
        return self.boto.execute(
            "dynamodb",
            "delete_table",
            TableName=table_name
        )

    def put_item(self, table_name, item):
        return self.boto.execute(
            "dynamodb",
            "put_item",
            TableName=table_name,
            Item=item
        )

    def get_item(self, table_name, key):
        return self.boto.execute(
            "dynamodb",
            "get_item",
            TableName=table_name,
            Key=key
        )

    def update_item(
        self,
        table_name,
        key,
        update_expression,
        expression_attribute_values,
        expression_attribute_names=None
    ):
        kwargs = {
            "TableName": table_name,
            "Key": key,
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
            "ReturnValues": "ALL_NEW"
        }

        if expression_attribute_names:
            kwargs["ExpressionAttributeNames"] = (
                expression_attribute_names
            )

        return self.boto.execute(
            "dynamodb",
            "update_item",
            **kwargs
        )

    def delete_item(self, table_name, key):
        return self.boto.execute(
            "dynamodb",
            "delete_item",
            TableName=table_name,
            Key=key
        )

    def scan(self, table_name):
        return self.boto.execute(
            "dynamodb",
            "scan",
            TableName=table_name
        )

    def query(
        self,
        table_name,
        key_condition_expression,
        expression_attribute_values
    ):
        return self.boto.execute(
            "dynamodb",
            "query",
            TableName=table_name,
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values
        )


class LambdaService:

    def __init__(self):
        self.boto = BotoService()
        self.region = self.boto.region

    def list_functions(self):
        return self.boto.execute(
            "lambda",
            "list_functions"
        )

    def get_function(self, function_name):
        return self.boto.execute(
            "lambda",
            "get_function",
            FunctionName=function_name
        )

    def create_function(
        self,
        function_name,
        runtime,
        role,
        handler,
        code
    ):
        return self.boto.execute(
            "lambda",
            "create_function",
            FunctionName=function_name,
            Runtime=runtime,
            Role=role,
            Handler=handler,
            Code=code
        )