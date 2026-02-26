import logging
import azure.functions as func
import requests
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Delete backup function processed a request.')
    
    try:
        req_body = req.get_json()
        environment = req_body.get('environment')
        backup_name = req_body.get('backup_name')
        
        if not environment or not backup_name:
            return func.HttpResponse(
                json.dumps({"error": "Missing environment or backup_name"}),
                mimetype="application/json",
                status_code=400
            )
        
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            logging.error('GITHUB_TOKEN not configured')
            return func.HttpResponse(
                json.dumps({"error": "GITHUB_TOKEN not configured"}),
                mimetype="application/json",
                status_code=500
            )
        
        # ✅ URL CORRIGIDA: sem espaços no final
        repo_owner = "laguirre06"
        repo_name = "velero-dashboard-ftd"
        workflow_id = "delete-backup.yml"
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches"
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        payload = {
            "ref": "main",
            "inputs": {
                "environment": environment,
                "backup_name": backup_name
            }
        }
        
        logging.info(f'Triggering workflow for {backup_name} in {environment}')
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 204:
            return func.HttpResponse(
                json.dumps({
                    "success": True,
                    "message": f"Delete workflow triggered for {backup_name} in {environment}"
                }),
                mimetype="application/json",
                status_code=200
            )
        else:
            logging.error(f'Failed to trigger workflow: {response.status_code} - {response.text}')
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}"
                }),
                mimetype="application/json",
                status_code=500
            )
            
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"success": False, "error": str(e)}),
            mimetype="application/json",
            status_code=500
        )