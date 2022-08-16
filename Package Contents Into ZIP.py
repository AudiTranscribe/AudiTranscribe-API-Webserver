# IMPORTS
import os
import zipfile

from git import Repo

# CONSTANTS
EXCLUDED_FILES_AND_FOLDERS = {
    "__pycache__",
    ".git",
    ".idea",
    ".run",
    "dist",
    "venv",
    "LICENSE",
    "README.md",
    ".DS_Store"
}


# HELPER FUNCTIONS
def get_latest_commit_timestamp():
    # Get the latest commit timestamp
    repo = Repo(".")
    latest_commit = list(repo.iter_commits("main", max_count=1))[0]
    latest_timestamp = int(latest_commit.committed_datetime.timestamp())

    # Update the API server version
    with open("API Server Version.txt", "w") as timestamp_file:
        timestamp_file.write(str(latest_timestamp))

    # Return the latest timestamp value
    return latest_timestamp


# MAIN CODE
if __name__ == "__main__":
    # Get latest commit timestamp
    latestTimestamp = get_latest_commit_timestamp()

    # Get all non-excluded files
    toInclude = []

    for dirName, dirs, files in os.walk("."):
        if dirName not in EXCLUDED_FILES_AND_FOLDERS:
            # Exclude files and folders
            dirs[:] = [d for d in dirs if d not in EXCLUDED_FILES_AND_FOLDERS]
            files[:] = [f for f in files if f not in EXCLUDED_FILES_AND_FOLDERS]

            # Add the specific directory if it is not the root directory
            if dirName != ".":
                # Skip the first two characters because it is always "./"
                toInclude.append(dirName[2:])

            # Add the rest to the master list
            for file in files:
                # Skip the first two characters because it is always "./"
                toInclude.append((dirName + "/" + file)[2:])

    # Create the ZIP file
    name = f"dist/API-Server-{latestTimestamp}.zip"
    with zipfile.ZipFile(name, "w") as f:
        # Add required files
        for file in toInclude:
            f.write(file)

    # Report completion
    print(f"Created '{name}' using commit with timestamp {latestTimestamp}.")
