import requests
import os
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# --- Tool Input Schema ---
class DeeplinkCheckerInput(BaseModel):
    """Input model for the check_deeplink tool."""
    db_name: str = Field(..., description="The name of the database, e.g., 'NDTVProfit'.")
    user_id: str = Field(..., description="The unique identifier for the user.")
    campaign_id: str = Field(..., description="The unique identifier for the campaign.")
    date: str = Field(..., description="The date for the check in YYYY-MM-DD format, e.g., '2025-09-24'.")
    region: str = Field(..., description="The server region, e.g., 'DC1'.")
    check_url: str = Field(
        "https://intercom-api-gateway.moengage.com/v2/iw/check-deeplink",
        description="The URL of the deeplink checker service to hit."
    )

# --- MCP Server Setup ---
mcp_app = FastMCP(
    "Deeplink Verification Server"
)

# --- Tool Definition ---
@mcp_app.tool(
    name="check_deeplink",
    description="Fetches and compares the deeplink sent to a user against the one configured during campaign creation. It returns the result, highlighting any discrepancies."
)
def check_deeplink(inputs: DeeplinkCheckerInput) -> dict:
    """
    Checks a deeplink by using an authentication token provided as an
    environment variable and hitting the specified deeplink check endpoint.
    """
    # 1. Fetch the authentication token from an environment variable
    print("Fetching token from environment variable...")
    auth_token = os.environ.get("REFRESH_TOKEN")

    if not auth_token:
        print("ERROR: REFRESH_TOKEN environment variable not set.")
        return {"error": "Authentication token is not configured on the server."}

    print("Successfully fetched token.")
    
    # 2. Use the token to call the deeplink check API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }

    payload = {
        "db_name": inputs.db_name,
        "user_id": inputs.user_id,
        "campaign_id": inputs.campaign_id,
        "date": inputs.date,
        "region": inputs.region
    }

    try:
        print(f"Sending POST request to {inputs.check_url}...")
        check_response = requests.post(inputs.check_url, headers=headers, json=payload, timeout=30)
        check_response.raise_for_status()

        print("Successfully received response from deeplink checker.")
        return check_response.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred while checking the deeplink: {e}"}

# --- Main Entry Point ---
# For local testing. This part is ignored by FastMCP Cloud.
if __name__ == "__main__":
    print("Starting MCP server...")
    mcp_app.run()
