import os
import sys
from dotenv import load_dotenv
from google import genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Load environment variables from .env
load_dotenv()

# The scope required to interact with the Gemini API (Google Generative Language API)
SCOPES = ['https://www.googleapis.com/auth/generative-language']

def get_oauth_credentials(client_secret_path, token_path):
    """Retrieve cached OAuth credentials or perform the interactive login flow."""
    creds = None
    
    # 1. Attempt to load cached user credentials from token.json
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # 2. If credentials do not exist or are expired, refresh or prompt user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token expired. Refreshing authorization silently...")
            creds.refresh(Request())
        else:
            print("No cached token found. Initiating interactive login flow...")
            if not os.path.exists(client_secret_path):
                raise FileNotFoundError(
                    f"Google Cloud client secret file not found at: {os.path.abspath(client_secret_path)}\n"
                    "Please download the client secret JSON file from your Google Cloud Console,\n"
                    "place it in the project root, and ensure the CLIENT_SECRET_PATH in .env is correct."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
            # Opens a temporary local server to complete the OAuth consent handshake
            creds = flow.run_local_server(port=0)
            
        # 3. Cache the refreshed or new credentials for future headless runs
        token_abs = os.path.abspath(token_path)
        token_dir = os.path.dirname(token_abs)
        if token_dir:
            os.makedirs(token_dir, exist_ok=True)
            
        with open(token_abs, 'w') as token_file:
            token_file.write(creds.to_json())
        print(f"Cached credentials successfully written to: {token_abs}")
        
    return creds

def fetch_articles(feed_urls):
    """Placeholder to fetch RSS feed articles."""
    return [
        {
            "title": "Mock Article 1",
            "link": "https://example.com/1",
            "summary": "This is mock article 1 summary."
        }
    ]

def generate_summary(credentials, articles, model="gemini-2.5-flash"):
    """Placeholder to generate Gemini summary."""
    # We pass credentials to the GenAI SDK Client
    client = genai.Client(credentials=credentials)
    
    # Simple validation using the client (e.g. check model list or output info)
    return f"Summary of {len(articles)} articles using {model} verified via Gemini Client."

def main():
    # 1. Retrieve config from environment variables
    feeds_env = os.getenv("RSS_FEEDS", "")
    feeds = [f.strip() for f in feeds_env.split(",") if f.strip()]
    model = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    output_path = os.getenv("OUTPUT_PATH", "./morning_summary.md")
    
    client_secret_path = os.getenv("CLIENT_SECRET_PATH", "./client_secret.json")
    token_path = os.getenv("TOKEN_PATH", "./token.json")
    
    # 2. Run credentials flow
    try:
        creds = get_oauth_credentials(client_secret_path, token_path)
    except FileNotFoundError as e:
        print(f"Authentication Error: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 3. Run mock pipeline
    articles = fetch_articles(feeds)
    summary_text = generate_summary(creds, articles, model=model)
    
    # 4. Write summary to output file
    output_abs = os.path.abspath(output_path)
    output_dir = os.path.dirname(output_abs)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    with open(output_abs, "w") as f:
        f.write(summary_text + "\n")
        
    print(f"Success! Daily summary written to: {output_abs}")

if __name__ == "__main__":
    main()
