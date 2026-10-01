# AWS Automation Platform

A Python-based AWS Automation Platform that provides a simple web dashboard for performing common AWS resource operations using **Boto3**, with **AWS CLI fallback**, validation, retry handling, and a persistent activity log.

The project is designed to simplify AWS resource management through a single user-friendly interface instead of requiring users to perform every operation manually through the AWS Console.

---

## Overview

The AWS Automation Platform provides a centralized dashboard where users can select an AWS service, choose an operation, provide the required parameters, and execute the operation.

The backend uses:

- **Python**
- **Flask**
- **Boto3**
- **AWS CLI**
- **Amazon S3**
- **Amazon DynamoDB**
- **AWS Lambda**

The application also maintains an activity log in DynamoDB so users can view previously performed automation operations.

---

## Key Features

- Web-based AWS automation dashboard
- Boto3-based AWS operations
- AWS CLI fallback when Boto3 fails
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
- Cost-conscious serverless AWS services

---

## Architecture

![AWS Automation Platform Architecture](architecture.png)

### Architecture Flow

```text
                    ┌──────────────────────┐
                    │        USER          │
                    │   Web Dashboard      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Flask Backend     │
                    │      Python          │
                    └──────────┬───────────┘
                               │
                     ┌─────────┴─────────┐
                     │                   │
                     ▼                   ▼
              ┌─────────────┐     ┌─────────────┐
              │   Boto3     │     │  AWS CLI    │
              │  Primary    │     │  Fallback   │
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