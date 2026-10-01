from flask import Blueprint, jsonify, request

from services.aws_service import AWSService
from services.activity_logger import ActivityLogger
from utils.json_serializer import sanitize_json


resources_bp = Blueprint("resources", __name__)

aws_service = AWSService()
activity_logger = ActivityLogger()


def get_resource_name(parameters):
    return (
        parameters.get("Bucket")
        or parameters.get("TableName")
        or parameters.get("FunctionName")
        or "AWS Resource"
    )


def build_cli_fallback(service, operation, parameters):

    # =========================
    # S3
    # =========================

    if service == "s3":

        if operation == "list_buckets":
            return "s3api", [
                "list-buckets"
            ]

        if operation == "head_bucket":
            return "s3api", [
                "head-bucket",
                "--bucket",
                parameters["Bucket"]
            ]

        if operation == "delete_bucket":
            return "s3api", [
                "delete-bucket",
                "--bucket",
                parameters["Bucket"]
            ]

        if operation == "create_bucket":

            bucket = parameters["Bucket"]

            region = parameters.get(
                "Region",
                "ap-south-1"
            )

            command = [
                "create-bucket",
                "--bucket",
                bucket
            ]

            if region != "us-east-1":
                command += [
                    "--create-bucket-configuration",
                    f"LocationConstraint={region}"
                ]

            command += [
                "--region",
                region
            ]

            return "s3api", command


    # =========================
    # DynamoDB
    # =========================

    if service == "dynamodb":

        if operation == "list_tables":
            return "dynamodb", [
                "list-tables"
            ]

        if operation == "describe_table":
            return "dynamodb", [
                "describe-table",
                "--table-name",
                parameters["TableName"]
            ]

        if operation == "delete_table":
            return "dynamodb", [
                "delete-table",
                "--table-name",
                parameters["TableName"]
            ]

        if operation == "create_table":
            return None, None


    # =========================
    # Lambda
    # =========================

    if service == "lambda":

        if operation == "list_functions":
            return "lambda", [
                "list-functions"
            ]

        if operation == "get_function":
            return "lambda", [
                "get-function",
                "--function-name",
                parameters["FunctionName"]
            ]

        if operation == "create_function":
            return None, None


    return None, None


@resources_bp.route(
    "/api/automation",
    methods=["POST"]
)
def automation():

    data = request.get_json(
        silent=True
    )

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body is missing or invalid JSON"
        }), 400


    service = data.get("service")
    operation = data.get("operation")
    parameters = data.get(
        "parameters"
    ) or {}


    if not service:
        return jsonify({
            "success": False,
            "error": "service is required"
        }), 400


    if not operation:
        return jsonify({
            "success": False,
            "error": "operation is required"
        }), 400


    if not isinstance(
        parameters,
        dict
    ):
        return jsonify({
            "success": False,
            "error": "parameters must be an object"
        }), 400


    # =========================
    # S3 CREATE BUCKET
    # =========================

    if (
        service == "s3"
        and operation == "create_bucket"
    ):

        bucket_name = parameters.get(
            "Bucket"
        )

        if not bucket_name:
            return jsonify({
                "success": False,
                "error": "Bucket name is required"
            }), 400


        region = parameters.get(
            "Region",
            aws_service.boto.region
        )


        if region != "us-east-1":

            parameters[
                "CreateBucketConfiguration"
            ] = {
                "LocationConstraint": region
            }


        parameters.pop(
            "Region",
            None
        )


    # =========================
    # REQUIRED FIELDS
    # =========================

    required_fields = {

        "s3": {

            "create_bucket": [
                "Bucket"
            ],

            "head_bucket": [
                "Bucket"
            ],

            "delete_bucket": [
                "Bucket"
            ]
        },

        "dynamodb": {

            "create_table": [
                "TableName"
            ],

            "describe_table": [
                "TableName"
            ],

            "delete_table": [
                "TableName"
            ]
        },

        "lambda": {

            "create_function": [
                "FunctionName"
            ],

            "get_function": [
                "FunctionName"
            ]
        }
    }


    for field in required_fields.get(
        service,
        {}
    ).get(
        operation,
        []
    ):

        if not parameters.get(field):

            return jsonify({
                "success": False,
                "error": f"{field} is required"
            }), 400


    # =========================
    # CLI FALLBACK
    # =========================

    cli_service, cli_command = (
        build_cli_fallback(
            service,
            operation,
            parameters
        )
    )


    # =========================
    # EXECUTE
    # =========================

    result = aws_service.execute(

        service_name=service,

        boto_operation=operation,

        boto_kwargs=parameters,

        cli_service=cli_service,

        cli_command=cli_command
    )


    resource_name = get_resource_name(
        parameters
    )


    # =========================
    # SUCCESS
    # =========================

    if result.get("success"):

        method = result.get(
            "method",
            "boto3"
        )


        message = (
            f"{service.upper()} "
            f"{operation} completed "
            f"for {resource_name}"
        )


        if result.get(
            "fallback_used"
        ):

            message += (
                " using AWS CLI fallback"
            )


        activity_logger.create_log(

            status="success",

            action=operation,

            message=message,

            resource=resource_name,

            method=method
        )


        return jsonify(
            sanitize_json(result)
        ), 200


    # =========================
    # ERROR
    # =========================

    activity_logger.create_log(

        status="error",

        action=operation,

        message=(
            f"{service.upper()} "
            f"{operation} failed "
            f"for {resource_name}"
        ),

        resource=resource_name,

        method=result.get(
            "method"
        ),

        details=result.get(
            "error"
        )
    )


    return jsonify(
        sanitize_json(result)
    ), 500


@resources_bp.route(
    "/api/status",
    methods=["GET"]
)
def resource_status():

    status = {}


    checks = {

        "s3": (
            "list_buckets",
            {},
            "s3api",
            ["list-buckets"]
        ),

        "dynamodb": (
            "list_tables",
            {},
            "dynamodb",
            ["list-tables"]
        ),

        "lambda": (
            "list_functions",
            {},
            "lambda",
            ["list-functions"]
        )
    }


    for service, (
        operation,
        parameters,
        cli_service,
        cli_command
    ) in checks.items():

        result = aws_service.execute(

            service_name=service,

            boto_operation=operation,

            boto_kwargs=parameters,

            cli_service=cli_service,

            cli_command=cli_command
        )


        status[service] = {

            "status":
                "available"
                if result.get("success")
                else "unavailable",

            "method":
                result.get("method")
        }


    return jsonify({

        "success": True,

        "resources": status
    })