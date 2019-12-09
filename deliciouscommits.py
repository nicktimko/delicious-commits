import argparse
import hashlib
import itertools
import os
import pathlib
import subprocess
import sys
import zlib


def load_commit_object(repo):
    git_in_repo = ["git", "-C", repo]
    # get head commit hash
    head_hash = subprocess.check_output(
        [*git_in_repo, "rev-parse", "HEAD"], universal_newlines=True
    ).strip()

    # print(head_hash)
    # get commit object
    git_root = subprocess.check_output(
        [*git_in_repo, "rev-parse", "--show-toplevel"], universal_newlines=True
    ).strip()

    git_root = pathlib.Path(git_root)
    print(git_root)

    head_object = git_root / ".git" / "objects" / head_hash[:2] / head_hash[2:]
    assert head_object.exists()

    with open(head_object, "rb") as f:
    # with zipfile.ZipFile.open(head_object, "r") as f:
    # with gzip.open(head_object, "rb") as f:
        data = f.read()

    # print(repr(data))

    commit_object = zlib.decompress(data)
    print(repr(commit_object))
    assert hashlib.sha1(commit_object).hexdigest() == head_hash

    commit_header, commit_data = commit_object.split(b"\x00", 1)

    _commit, commit_data_len = commit_header.decode("ascii").split(" ", 1)
    assert _commit == "commit"
    assert int(commit_data_len) == len(commit_data)

    commit_data_str = commit_data.decode("utf-8")
    print(commit_data_str)

    if "gpgsig" in commit_data_str:
        raise RuntimeError(
            "mutating commit message with signature will result in invalid "
            "signature or unpredictable (if resigned) hash"
        )
    return commit_data_str


_NOTIFY_PERIOD = 100000

def find_prefix(commit, prefix="beef", give_up_after=1_000_000):
    notify_at = 10
    for n in itertools.count():
        if n == notify_at:
            if n < _NOTIFY_PERIOD:
                notify_at *= 10
            else:
                notify_at += _NOTIFY_PERIOD
            print(f'attempt {n}')
        elif n > give_up_after:
            raise RuntimeError("gave up")

        new_commit = commit + f"\nDelicious: {n}\n"
        new_commit_b = new_commit.encode("utf-8")

        new_commit_obj = f"commit {len(new_commit_b)}\x00".encode("ascii") + new_commit_b

        if hashlib.sha1(new_commit_obj).hexdigest().startswith(prefix):
            return new_commit


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_repo")
    args = parser.parse_args(argv)

    commit_data = load_commit_object(args.target_repo)

    new_commit = find_prefix(commit_data)

    print("==============")
    print(new_commit)
    print("==============")
    print(repr(new_commit))
    print("==============")


if __name__ == "__main__":
    sys.exit(main())
