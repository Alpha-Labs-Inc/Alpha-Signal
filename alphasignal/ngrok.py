# import ngrok python sdk
import ngrok
import time


listener = ngrok.forward(
    "127.0.0.1:8000",
    authtoken_from_env=True,
    # oauth_provider="google",
    # oauth_allow_emails="kate.libby@gmail.com",
    # oauth_allow_domains="acme.org",
)

# Output ngrok url to console
print(f"Ingress established at {listener.url()}")

if __name__ == "__main__":
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing listener")
