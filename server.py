import requests
import os
from fastmcp import FastMCP
from pydantic import Field
from typing import Dict, Any

# --- MCP Server Setup ---
mcp_app = FastMCP(
    "Deeplink Verification Server",
    description="A server that provides tools for verifying marketing campaign deeplinks."
)

# --- Tool Definition ---
@mcp_app.tool(
    name="check_deeplink",
    description="Verifies a campaign deeplink by comparing the link sent to a user with the one configured in the campaign. Crucial for ensuring link integrity."
)
def check_deeplink(
    db_name: str = Field(..., description="The specific database name for the query.", examples=["NDTVProfit_123"]),
    user_id: str = Field(..., description="The unique identifier for the user.", examples=["user_a4b1c9x"]),
    campaign_id: str = Field(..., description="The unique identifier for the campaign.", examples=["campaign_z9y8w7v"]),
    date: str = Field(..., description="The date the campaign was sent, in YYYY-MM-DD format.", examples=["2025-09-24"]),
    region: str = Field(..., description="The server region where the data is hosted.", examples=["DC1", "EU1"])
) -> Dict[str, Any]:
    """
    Performs a server-side check to validate a campaign's deeplink for a specific user.

    Args:
        db_name: The specific database name for the query.
        user_id: The unique identifier for the user whose deeplink is being checked.
        campaign_id: The unique identifier for the campaign that sent the deeplink.
        date: The specific date the campaign was sent, in YYYY-MM-DD format.
        region: The server region where the campaign data is hosted.

    Returns:
        A dictionary with a 'status' and either a 'data' key on success or an 'error' key on failure.
    """
    CHECK_URL = "https://intercom-api-gateway.moengage.com/v2/iw/check-deeplink"
    AUTH_TOKEN_ENV_VAR = "DEEPLINK_CHECKER_REFRESH_TOKEN"
    auth_token = os.environ.get(AUTH_TOKEN_ENV_VAR)

    if not auth_token:
        print(f"ERROR: {AUTH_TOKEN_ENV_VAR} environment variable not set.")
        return {
            "status": "error",
            "error": "Authentication token is not configured on the server."
        }

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}"}
    payload = {
        "db_name": db_name,
        "user_id": user_id,
        "campaign_id": campaign_id,
        "date": date,
        "region": region,
    }

    try:
        print(f"Sending POST request to {CHECK_URL}...")
        response = requests.post(CHECK_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        print("Successfully received response from deeplink checker.")
        return {"status": "success", "data": response.json()}

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return {"status": "error", "error": f"An HTTP error occurred: {http_err}. Response: {response.text}"}
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return {"status": "error", "error": f"A network or request error occurred: {req_err}"}

# --- Main Entry Point ---
if __name__ == "__main__":
    os.environ["DEEPLINK_CHECKER_REFRESH_TOKEN"] = "your_test_token_here"
    print("Starting MCP server for local testing...")
    mcp_app.run()
