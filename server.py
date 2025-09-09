from fastapi import FastAPI, Header, Request, Response
import uvicorn
import httpx # Used for making asynchronous HTTP requests

app = FastAPI()

# Define the external API URL
EXTERNAL_API_URL = "https://intercom-api-gateway.moengage.com/v2/iw/check-deeplink"

# --- 2. Define the API Endpoint ---
@app.post("/check-deeplink", tags=["Deeplink Proxy"])
async def forward_deeplink_check(
    request: Request,
    response: Response,
    authorization: str = Header(...) 
):
    json_payload = await request.json()
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json"
        }

        external_response = await client.post(EXTERNAL_API_URL, json=json_payload, headers=headers)
        response.status_code = external_response.status_code
        return external_response.json()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

