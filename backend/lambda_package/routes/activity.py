from flask import Blueprint, jsonify, request

from services.activity_logger import ActivityLogger
from utils.json_serializer import sanitize_json


activity_bp = Blueprint("activity", __name__)

logger = ActivityLogger()


@activity_bp.route("/api/activity", methods=["GET"])
def get_activity():
    result = logger.get_logs()

    return (
        jsonify(sanitize_json(result)),
        200 if result.get("success") else 500
    )


@activity_bp.route("/api/activity", methods=["POST"])
def create_activity():
    data = request.get_json(silent=True) or {}

    status = data.get("status")
    action = data.get("action")
    message = data.get("message")

    if not status or not action or not message:
        return jsonify({
            "success": False,
            "error": "status, action and message are required"
        }), 400

    result = logger.create_log(
        status=status,
        action=action,
        message=message,
        resource=data.get("resource"),
        method=data.get("method"),
        details=data.get("details")
    )

    return (
        jsonify(sanitize_json(result)),
        200 if result.get("success") else 500
    )


@activity_bp.route("/api/activity", methods=["DELETE"])
def clear_activity():
    result = logger.clear_logs()

    return (
        jsonify(sanitize_json(result)),
        200 if result.get("success") else 500
    )