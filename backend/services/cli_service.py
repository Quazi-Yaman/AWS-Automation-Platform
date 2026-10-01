import subprocess
import json


class CLIService:

    def execute(self, service, command, timeout=30):
        try:
            full_command = ["aws", service] + command

            process = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if process.returncode == 0:
                output = process.stdout.strip()

                try:
                    output = json.loads(output)
                except json.JSONDecodeError:
                    pass

                return {
                    "success": True,
                    "method": "aws_cli",
                    "service": service,
                    "command": full_command,
                    "result": output
                }

            return {
                "success": False,
                "method": "aws_cli",
                "service": service,
                "command": full_command,
                "error": process.stderr.strip()
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "method": "aws_cli",
                "service": service,
                "error": "AWS CLI command timed out"
            }

        except Exception as e:
            return {
                "success": False,
                "method": "aws_cli",
                "service": service,
                "error": str(e)
            }