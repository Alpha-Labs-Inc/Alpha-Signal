# import ngrok python sdk
from dotenv import load_dotenv
import ngrok
import time
import os

load_dotenv()

listener = ngrok.forward(
    "localhost:8000",  # Updated upstream address to localhost
    authtoken_from_env=True,
    domain=os.getenv("NGROK_DOMAIN"),
    # oauth_provider="google",
    # oauth_allow_emails="kate.libby@gmail.com",
    # oauth_allow_domains="acme.org",
    # ip_restriction_allow_cidrs=[os.getenv("TWEET_CATCHER_SERVICE_IP")],
    # ip_restriction_deny_cidrs="110.2.3.4/32"
)

# Output ngrok url to console with immediate flush
print(f"Ingress established at {listener.url()}", flush=True)

if __name__ == "__main__":
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing listener")
