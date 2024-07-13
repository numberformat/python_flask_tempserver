"""This script is used to setup the environment variables for the server.
This only needs to be run once to create the .env file.
"""
import os
from dotenv import load_dotenv, set_key

# Function to ask for input and save it to .env
def setup_environment():
    env_file = ".env"
    # Check if .env exists
    if os.path.exists(env_file):
        overwrite = input(".env file already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Setup aborted.")
            return

    # Save to .env file
    set_key(env_file, "SMTP_HOST", input("Enter SMTP host: "))
    set_key(env_file, "SMTP_PORT", input("Enter SMTP port for example 587: "))
    set_key(env_file, "TIMEOUT_MINUTES", input("Enter timeout in minutes for the server: "))
    set_key(env_file, "NOTIFY_EMAIL", input("Enter default email address to notify about the temporary server: "))
    set_key(env_file, "DB_URI", input("Enter database URI for example: sqlite:///db.sqlite3: "))

    print("Setup complete. Configuration saved to .env file.")

if __name__ == "__main__":
    setup_environment()