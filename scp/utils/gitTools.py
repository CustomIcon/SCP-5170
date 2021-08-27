from git import Repo

repo = Repo()


def getVersion():
    return repo.head.commit.hexsha, repo.git.rev_parse(
        repo.head.commit.hexsha,
        short=7,
    )