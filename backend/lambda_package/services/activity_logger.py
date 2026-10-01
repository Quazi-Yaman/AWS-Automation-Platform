from datetime import datetime, timezone
import uuid

from services.boto_service import BotoService


class ActivityLogger:

    TABLE_NAME = "AWSAutomationActivityLog"

    def __init__(self):
        self.boto = BotoService()

    def create_table(self):
        return self.boto.execute(
            "dynamodb",
            "create_table",
            TableName=self.TABLE_NAME,
            KeySchema=[
                {
                    "AttributeName": "log_id",
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "log_id",
                    "AttributeType": "S"
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )

    def create_log(
        self,
        status,
        action,
        message,
        resource=None,
        method=None,
        details=None
    ):
        timestamp = datetime.now(timezone.utc).isoformat()
        log_id = str(uuid.uuid4())

        item = {
            "log_id": {"S": log_id},
            "timestamp": {"S": timestamp},
            "status": {"S": str(status)},
            "action": {"S": str(action)},
            "message": {"S": str(message)}
        }

        if resource:
            item["resource"] = {"S": str(resource)}

        if method:
            item["method"] = {"S": str(method)}

        if details:
            item["details"] = {"S": str(details)}

        return self.boto.execute(
            "dynamodb",
            "put_item",
            TableName=self.TABLE_NAME,
            Item=item
        )

    def get_logs(self):
        return self.boto.execute(
            "dynamodb",
            "scan",
            TableName=self.TABLE_NAME
        )

    def clear_logs(self):
        scan_result = self.get_logs()

        if not scan_result.get("success"):
            return scan_result

        items = scan_result.get("result", {}).get("Items", [])

        deleted = 0

        for item in items:
            log_id = item.get("log_id")

            if not log_id:
                continue

            result = self.boto.execute(
                "dynamodb",
                "delete_item",
                TableName=self.TABLE_NAME,
                Key={
                    "log_id": log_id
                }
            )

            if result.get("success"):
                deleted += 1

        return {
            "success": True,
            "deleted": deleted
        }