from datetime import date, datetime
from decimal import Decimal


def sanitize_json(value):
    """
    Convert AWS/Boto3 response data into JSON-safe values.
    """

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    if isinstance(value, dict):
        return {
            str(key): sanitize_json(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            sanitize_json(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            sanitize_json(item)
            for item in value
        ]

    return value