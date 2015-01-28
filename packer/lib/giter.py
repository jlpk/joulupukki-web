#!/usr/bin/python

import git


def clone(git_url, git_local_folder, branch=None, commit=None):
    repo = git.Repo.clone_from(git_url, git_local_folder)
    if branch is not None:
        for ref in repo.refs:
            print ref.name
            if ref.name == branch:
                repo.head.reference = repo.commit(ref)
            if ref.name == "origin/" + branch:
                repo.head.reference = repo.commit(ref)

    if commit is not None:
        repo.head.reference = repo.commit(commit)

    repo.head.reset(index=True, working_tree=True)

