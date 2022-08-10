# IMPORTS
import zipfile
from application import get_latest_commit_timestamp

# CONSTANTS
FILES_TO_ADD = [
    ".gitattributes",
    ".gitignore",
    "application.py",
    "Procfile",
    "requirements.txt",
    "wsgi.py",
]


# MAIN CODE
if __name__ == "__main__":
    # Get latest commit timestamp
    latestTimestamp = get_latest_commit_timestamp()

    # Create the ZIP file
    name = f"dist/API-Server-{latestTimestamp}.zip"
    with zipfile.ZipFile(name, "w") as f:
        # Add required files
        for file in FILES_TO_ADD:
            f.write(file)

    # Report completion
    print(f"Created '{name}' using commit with timestamp {latestTimestamp}.")
