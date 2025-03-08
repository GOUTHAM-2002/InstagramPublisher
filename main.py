from fastapi import FastAPI, File, UploadFile, Form, Query
from fastapi.responses import HTMLResponse
import os
import shutil
import requests
from dotenv import load_dotenv
from pyngrok import ngrok, conf
import time  # Add this at the top with other imports

load_dotenv()

# Set up ngrok authentication
ngrok.set_auth_token("2sRePffqb5ZMnaAaqRKx1IHv2bD_oY362VieueiYTQm996gR")  # Add this line before creating the tunnel

app = FastAPI()
INSTAGRAM_APP_ID = os.getenv('INSTAGRAM_APP_ID')
INSTAGRAM_APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET')


VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

# Set up ngrok tunnel
ngrok_tunnel = ngrok.connect(8001)
REDIRECT_URI = f"{ngrok_tunnel.public_url}/callback"
print(f"Ngrok URL: {ngrok_tunnel.public_url}")
print(f"Please update this Redirect URI in Meta Dashboard: {REDIRECT_URI}")

# Add this root endpoint
@app.get("/")
async def root(hub_mode: str = Query(None, alias="hub.mode"),
              hub_challenge: str = Query(None, alias="hub.challenge"),
              hub_verify_token: str = Query(None, alias="hub.verify_token")):
    # Handle webhook verification
    print(f"Received verification request: mode={hub_mode}, challenge={hub_challenge}, token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token:
        if hub_verify_token == VERIFY_TOKEN:
            try:
                return int(hub_challenge)
            except (TypeError, ValueError):
                return HTMLResponse("Invalid challenge value", status_code=400)
        return HTMLResponse("Verify token mismatch", status_code=403)
    
    # Regular homepage for non-webhook requests
    auth_url = (
        f"https://www.instagram.com/oauth/authorize"
        f"?client_id={INSTAGRAM_APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=instagram_business_basic,instagram_business_manage_messages,"
        f"instagram_business_manage_comments,instagram_business_content_publish,"
        f"instagram_business_manage_insights"
        f"&response_type=code"
        f"&enable_fb_login=0"
        f"&force_authentication=1"
    )
    return HTMLResponse(f"""
    <html>
        <body>
            <h1>Instagram Login</h1>
            <a href="{auth_url}"><button>Login with Instagram Business Account</button></a>
        </body>
    </html>
    """)
@app.get("/callback")
async def callback(code: str = None, hub_mode: str = None, hub_verify_token: str = None, hub_challenge: str = None):
    print(f"Callback received - code: {code}")
    
    if hub_mode == 'subscribe' and hub_verify_token:
        if hub_verify_token == VERIFY_TOKEN:
            return int(hub_challenge)
        return {"error": "Verify token mismatch"}, 403

    if code:
        # Step 1: Exchange code for short-lived access token
        token_url = "https://api.instagram.com/oauth/access_token"
        data = {
            'client_id': INSTAGRAM_APP_ID,
            'client_secret': INSTAGRAM_APP_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'code': code
        }
        
        response = requests.post(token_url, data=data)
        print(f"Token exchange response: {response.json()}")
        token_data = response.json()
        
        if 'access_token' in token_data:
            # Step 2: Exchange short-lived token for long-lived token
            long_lived_token_url = "https://graph.instagram.com/v18.0/access_token"
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': INSTAGRAM_APP_SECRET,
                'access_token': token_data['access_token']
            }
            long_lived_response = requests.get(long_lived_token_url, params=params)
            print(f"Long-lived token response: {long_lived_response.json()}")
            long_lived_data = long_lived_response.json()
            
            if 'access_token' in long_lived_data:
                # Step 3: Get Instagram Business Account ID using the long-lived token
                account_url = f"https://graph.instagram.com/v18.0/me"
                params = {
                    'fields': 'id,username,account_type',
                    'access_token': long_lived_data['access_token']
                }
                account_response = requests.get(account_url, params=params)
                print(f"Account info response: {account_response.json()}")
                account_data = account_response.json()
                
                if 'id' in account_data:
                    # In the callback endpoint, update the HTML form to:
                    return HTMLResponse(f"""
                    <html>
                        <body>
                            <h1>Upload Video</h1>
                            <form action="/upload" method="post" enctype="multipart/form-data">
                                <input type="text" name="video_url" placeholder="Enter video URL" required><br>
                                <input type="text" name="caption" placeholder="Caption"><br>
                                <input type="hidden" name="access_token" value="{long_lived_data['access_token']}"><br>
                                <input type="hidden" name="ig_account_id" value="{account_data['id']}"><br>
                                <input type="submit" value="Upload">
                            </form>
                        </body>
                    </html>
                    """)
    
    return HTMLResponse("Authentication failed. Please try again.", status_code=400)
@app.post("/upload")
async def upload_video(
    video_url: str = Form(...),
    caption: str = Form(...),
    access_token: str = Form(...),
    ig_account_id: str = Form(...)
):
    try:
        # Create container for the reel using Instagram Graph API
        container_url = f"https://graph.instagram.com/v18.0/{ig_account_id}/media"
        container_data = {
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption,
            'access_token': access_token
        }
        
        print("Creating container...")
        print(f"Using video URL: {video_url}")
        container_response = requests.post(container_url, data=container_data)
        container_data = container_response.json()
        print(f"Container creation response: {container_data}")
        
        if 'id' in container_data:
            creation_id = container_data['id']
            
            # Add delay and retry mechanism for publishing
            max_retries = 5
            retry_delay = 10  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Wait before attempting to publish
                    time.sleep(retry_delay)
                    
                    # Publish the reel
                    publish_url = f"https://graph.instagram.com/v18.0/{ig_account_id}/media_publish"
                    publish_data = {
                        'creation_id': creation_id,
                        'access_token': access_token
                    }
                    publish_response = requests.post(publish_url, data=publish_data)
                    publish_result = publish_response.json()
                    print(f"Publish attempt {attempt + 1} response: {publish_result}")
                    
                    if 'id' in publish_result:
                        return {
                            "message": f"Reel upload successful after {attempt + 1} attempts",
                            "creation_id": creation_id,
                            "media_id": publish_result['id']
                        }
                    elif 'error' in publish_result and 'code' in publish_result['error'] and publish_result['error']['code'] == 9007:
                        print(f"Media not ready yet, retrying in {retry_delay} seconds...")
                        continue
                    else:
                        return {"error": f"Publishing failed: {publish_result}"}
                        
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
            
            return {"error": "Max retries reached, video processing took too long"}
        else:
            return {"error": f"Failed to create media container: {container_data}"}
            
    except Exception as e:
        print(f"Exception details: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
