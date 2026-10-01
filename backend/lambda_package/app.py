from flask import Flask, jsonify
from flask_cors import CORS
from mangum import Mangum
from routes.activity import activity_bp
from routes.resources import resources_bp


app = Flask(__name__)
CORS(app)

app.register_blueprint(activity_bp)
app.register_blueprint(resources_bp)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "AWS Automation Platform backend is running"
    })

handler = Mangum(app)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
