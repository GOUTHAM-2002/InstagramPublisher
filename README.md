# Instagram Reel Uploader

A simple web application to upload reels to Instagram using the Instagram Graph API.

## Prerequisites

Before setting up the project, ensure you have the following:

1. **Download and install [ngrok](https://ngrok.com/download)**
2. **Python 3.8 or higher**
3. **An Instagram Business Account**
4. **A Meta Developer Account with an app configured**

## Setup

### 1. Install Requirements

Run the following command to install the necessary dependencies:

```bash
pip install -r requirements.txt
```

### 2. Create a `.env` File

Create a `.env` file in the project root and add your credentials:

```ini
INSTAGRAM_APP_ID=your_app_id
INSTAGRAM_APP_SECRET=your_app_secret
VERIFY_TOKEN=any_random_string
NGROK_AUTH_TOKEN=your_ngrok_auth_token
```

### 3. Update Your Meta App Settings

Follow these steps to configure your Meta App:

1. **Go to the [Meta Developers Console](https://developers.facebook.com/)**
2. Navigate to your app settings.
3. Add `{ngrok_url}/callback` to the **Valid OAuth Redirect URIs**.
4. The `ngrok_url` will be displayed when you start the application.

## Running the Application

To start the application, run the following command:

```bash
python app.py
```

Once the application is running, use **ngrok** to expose your local server:

```bash
ngrok http 5000
```

Copy the generated ngrok URL and update your Meta App settings accordingly.

## Usage

- Authenticate using OAuth.
- Upload reels to your Instagram Business Account.

## License

This project is licensed under the MIT License.

