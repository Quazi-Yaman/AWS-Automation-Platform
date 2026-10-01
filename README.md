# AWS Automation Platform

A practical Python-based AWS Automation Platform that provides a user-friendly web dashboard for performing common AWS resource operations using **Flask, Boto3, AWS CLI, and DynamoDB**.

The platform simplifies AWS resource management by allowing users to select an AWS service, choose an operation, provide the required parameters, and execute the operation from a single dashboard.

---

## 📌 Project Overview

The AWS Automation Platform is designed to demonstrate practical AWS automation using Python.

The application uses **Boto3 as the primary AWS SDK** and provides an **AWS CLI fallback** when a supported Boto3 operation fails.

The platform also provides:

- AWS resource validation
- Retry and timeout handling
- Structured API responses
- AWS service status monitoring
- Persistent activity logging using DynamoDB
- User-friendly web dashboard

---

## ✨ Key Features

- Web-based AWS automation dashboard
- Boto3-based AWS operations
- AWS CLI fallback mechanism
- AWS resource validation
- Connection timeout handling
- Retry mechanism
- Structured JSON API responses
- S3 automation
- DynamoDB automation
- Lambda automation
- Persistent activity logging
- AWS service availability status
- User-friendly frontend
- CORS support
- Error handling
- Cost-conscious AWS architecture

---

## 🏗️ Architecture

![AWS Automation Platform Architecture](architecture.png)

### Architecture Flow

```text
                    ┌──────────────────────┐
                    │        USER          │
                    │    Web Dashboard     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Flask Backend     │
                    │       Python         │
                    └──────────┬───────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                     ▼                   ▼
              ┌─────────────┐     ┌─────────────┐
              │    Boto3    │     │   AWS CLI   │
              │   Primary   │     │   Fallback  │
              └──────┬──────┘     └──────┬──────┘
                     │                   │
                     └─────────┬─────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
        ┌─────────┐       ┌───────────┐      ┌─────────┐
        │   S3    │       │ DynamoDB  │      │ Lambda  │
        └─────────┘       └─────┬─────┘      └─────────┘
                                │
                                ▼
                       ┌────────────────┐
                       │ Activity Log   │
                       │ DynamoDB Table │
                       └────────────────┘


🌐 How to Run the Website

Follow these steps to run the AWS Automation Platform locally on Windows.

Step 1 — Clone the Repository

Open Command Prompt and run:

git clone https://github.com/Quazi-Yaman/AWS-Automation-Platform.git
cd AWS-Automation-Platform
Step 2 — Open the Backend Folder
cd backend
Step 3 — Create the Python Virtual Environment
python -m venv venv
Step 4 — Activate the Virtual Environment
venv\Scripts\activate

After activation, the terminal should show:

(venv)
Step 5 — Install Dependencies
pip install -r requirements.txt
Step 6 — Configure AWS CLI

Configure your AWS credentials:

aws configure

Enter your AWS credentials and use:

Default region: ap-south-1
Output format: json

Verify the AWS connection:

aws sts get-caller-identity

A successful response confirms that AWS CLI is configured correctly.

Security: Never upload AWS Access Keys, Secret Keys, or other credentials to GitHub.

Step 7 — Start the Flask Backend

Make sure you are inside the backend folder and run:

python app.py

The Flask backend will start at:

http://127.0.0.1:5000

Keep this Command Prompt window running.

Step 8 — Check the Backend

Open this URL in your browser:

http://127.0.0.1:5000/api/health

Expected response:

{
    "status": "success",
    "message": "AWS Automation Platform backend is running"
}

If this response appears, the backend is running successfully.

Step 9 — Open the Website

Open the project folder:

AWS-Automation-Platform/
│
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js

Open:

frontend/index.html

by double-clicking index.html.

The AWS Automation Platform dashboard will open in your browser.

The frontend communicates with the Flask backend through:

http://127.0.0.1:5000/api

Important: The Flask backend must remain running while using the website.

Step 10 — Stop the Website

When you finish using the application, return to the Command Prompt running Flask and press:

CTRL + C

This stops the Flask backend.
