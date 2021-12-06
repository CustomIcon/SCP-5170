(import [git[Repo]])

(setv repo (Repo))

(defn getVersion []
    (setv versions
        (, repo.head.commit.hexsha
        (repo.git.rev_parse repo.head.commit.hexsha :short 7)))
    (return versions))
