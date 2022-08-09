from git import Repo

repo = Repo(".")
latestCommit = list(repo.iter_commits("main", max_count=1))[0]
print(int(latestCommit.committed_datetime.timestamp()))
