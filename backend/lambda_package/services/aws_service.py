from services.boto_service import BotoService
from services.cli_service import CLIService


class AWSService:

    ALLOWED_SERVICES = {
        "s3",
        "dynamodb",
        "lambda"
    }

    ALLOWED_OPERATIONS = {

        "s3": {
            "create_bucket",
            "head_bucket",
            "list_buckets",
            "delete_bucket"
        },

        "dynamodb": {
            "create_table",
            "describe_table",
            "list_tables",
            "delete_table",
            "put_item",
            "get_item",
            "update_item",
            "delete_item",
            "scan",
            "query"
        },

        "lambda": {
            "create_function",
            "get_function",
            "list_functions",
            "delete_function",
            "update_function_code",
            "update_function_configuration",
            "invoke"
        }
    }


    def __init__(self):

        self.boto = BotoService()
        self.cli = CLIService()


    def validate_request(
        self,
        service_name,
        operation
    ):

        if service_name not in self.ALLOWED_SERVICES:

            return {
                "success": False,
                "error": (
                    f"Unsupported AWS service: "
                    f"{service_name}"
                )
            }


        if operation not in self.ALLOWED_OPERATIONS.get(
            service_name,
            set()
        ):

            return {
                "success": False,
                "error": (
                    f"Unsupported operation "
                    f"'{operation}' for "
                    f"{service_name}"
                )
            }


        return {
            "success": True
        }


    def execute(
        self,
        service_name,
        boto_operation,
        boto_kwargs=None,
        cli_service=None,
        cli_command=None
    ):

        boto_kwargs = boto_kwargs or {}


        # -----------------------------
        # 1. Validate request
        # -----------------------------

        validation = self.validate_request(
            service_name,
            boto_operation
        )

        if not validation.get("success"):

            return validation


        # -----------------------------
        # 2. Try Boto3 first
        # -----------------------------

        boto_result = self.boto.execute(
            service_name,
            boto_operation,
            **boto_kwargs
        )


        if boto_result.get("success"):

            return {
                "success": True,
                "method": "boto3",
                "fallback_used": False,
                "service": service_name,
                "operation": boto_operation,
                "boto3": boto_result,
                "result": boto_result.get("result")
            }


        # -----------------------------
        # 3. Boto3 failed
        # -----------------------------

        if not cli_service or not cli_command:

            return {
                "success": False,
                "method": "boto3",
                "fallback_used": False,
                "service": service_name,
                "operation": boto_operation,
                "boto3": boto_result,
                "error": boto_result.get(
                    "error",
                    "Boto3 operation failed"
                )
            }


        # -----------------------------
        # 4. Try AWS CLI fallback
        # -----------------------------

        cli_result = self.cli.execute(
            service=cli_service,
            command=cli_command
        )


        if cli_result.get("success"):

            return {
                "success": True,
                "method": "aws_cli",
                "fallback_used": True,
                "service": service_name,
                "operation": boto_operation,
                "boto3": boto_result,
                "cli": cli_result,
                "result": cli_result.get("result")
            }


        # -----------------------------
        # 5. Both failed
        # -----------------------------

        return {
            "success": False,
            "method": "aws_cli",
            "fallback_used": True,
            "service": service_name,
            "operation": boto_operation,
            "boto3": boto_result,
            "cli": cli_result,
            "error": (
                "Boto3 operation failed and "
                "AWS CLI fallback also failed"
            )
        }