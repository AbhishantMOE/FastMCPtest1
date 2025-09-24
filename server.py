import requests
import os
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# --- Tool Input Schema ---
# This model defines the inputs for the tool, which FastMCP uses to generate the UI and API schema.
class DeeplinkCheckerInput(BaseModel):
    """Input model for the check_deeplink tool."""
    db_name: str = Field(..., description="The name of the database, e.g., 'NDTVProfit'.")
    user_id: str = Field(..., description="The unique identifier for the user.")
    campaign_id: str = Field(..., description="The unique identifier for the campaign.")
    date: str = Field(..., description="The date for the check in YYYY-MM-DD format, e.g., '2025-09-24'.")
    region: str = Field(..., description="The server region, e.g., 'DC1'.")

# --- MCP Server Setup ---
mcp_app = FastMCP(
    "Deeplink Verification Server"
)

# --- Tool Definition ---
@mcp_app.tool
def check_deeplink(db_name: str, user_id: str, campaign_id: str, date: str, region: str) -> str:
    """
    Checks a deeplink by using an authentication token provided as an
    environment variable and hitting the specified deeplink check endpoint.

    Args:
        db_name: The specific database name for the query.
        user_id: The unique identifier for the user whose deeplink is being checked.
        campaign_id: The unique identifier for the campaign that sent the deeplink.
        date: The specific date the campaign was sent, in YYYY-MM-DD format.
        region: The server region where the campaign data is hosted.

    Returns:
        A string indicating success or the specific error message.
    """
    # The check URL is a fixed constant.
    CHECK_URL = "https://intercom-api-gateway.moengage.com/v2/iw/check-deeplink"
    
    # 1. Fetch the authentication token from an environment variable
    print("Fetching token from environment variable...")
    auth_token = os.environ.get("REFRESH_TOKEN")

    if not auth_token:
        print("ERROR: REFRESH_TOKEN environment variable not set.")
        return "Authentication token is not configured on the server."

    print("Successfully fetched token.")
    
    # 2. Use the token to call the deeplink check API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}"
    }

    payload = {
        "db_name": db_name,
        "user_id": user_id,
        "campaign_id": campaign_id,
        "date": date,
        "region": region
    }

    try:
        print(f"Sending POST request to {CHECK_URL}...")
        check_response = requests.post(CHECK_URL, headers=headers, json=payload, timeout=30)
        check_response.raise_for_status()

        response_data = check_response.json()
        print("Successfully received response from deeplink checker.")

        # 3. Process the response and return the appropriate message
        if response_data.get("status") == "success":
            return "Urls are matching, your deeplink is working correctly at clients end"
        else:
            return response_data.get("error_message", "An unknown error occurred, and no error message was provided.")

    except requests.exceptions.HTTPError as e:
        # Handle cases where the API returns a non-2xx status code
        return f"HTTP Error: {e.response.status_code} - {e.response.text}"
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        return f"An error occurred while checking the deeplink: {e}"
    except ValueError:
        # Handle cases where the response is not valid JSON
        return "Failed to decode the JSON response from the server."


# --- Main Entry Point ---
# For local testing. This part is ignored by FastMCP Cloud.
if __name__ == "__main__":
    print("Starting MCP server...")
    mcp_app.run()
