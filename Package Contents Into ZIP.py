# IMPORTS
import zipfile

from git import Repo

# CONSTANTS
FILES_TO_ADD = [
    ".gitattributes",
    ".gitignore",
    "application.py",
    "Procfile",
    "requirements.txt",
    "wsgi.py",
]


# HELPER FUNCTIONS
def get_latest_commit_timestamp():
    repo = Repo(".")
    latest_commit = list(repo.iter_commits("main", max_count=1))[0]
    return int(latest_commit.committed_datetime.timestamp())


# MAIN CODE
if __name__ == "__main__":
    # Get latest commit timestamp
    latestTimestamp = get_latest_commit_timestamp()

    # Create the ZIP file
    name = f"API-Server-{latestTimestamp}.zip"
    with zipfile.ZipFile(name, "w") as f:
        # Add required files
        for file in FILES_TO_ADD:
            f.write(file)

    # Report completion
    print(f"Created '{name}' using commit with timestamp {latestTimestamp}.")
