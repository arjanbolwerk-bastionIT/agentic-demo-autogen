def ensure_repo_sync():
    return True
def commit_and_push(message: str):
    print("[github] commit noop:", message)
    return True
def create_or_update_pr(title: str, body: str):
    print("[github] pr noop:", title)
    return "(noop-pr-url)"
