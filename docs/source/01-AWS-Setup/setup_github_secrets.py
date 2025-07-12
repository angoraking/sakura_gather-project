# -*- coding: utf-8 -*-

from github import Github
from home_secret.api import hs

from settings import (
    github_user_name,
    github_repo_name,
)

github_token = hs.v("providers.github.accounts.ak.users.ak.secrets.dev.value")
path = "providers.cloudflare.accounts.bmt.secrets.read_and_write_all_r2_bucket.creds.endpoint"
cloudflare_r2_endpoint = hs.v(path)
path = "providers.cloudflare.accounts.bmt.secrets.read_and_write_all_r2_bucket.creds.access_key"
cloudflare_r2_access_key = hs.v(path)
path = "providers.cloudflare.accounts.bmt.secrets.read_and_write_all_r2_bucket.creds.secret_key"
cloudflare_r2_secret_key = hs.v(path)
printer = print

gh = Github(github_token)
repo = gh.get_repo(f"{github_user_name}/{github_repo_name}")
key_value_pairs = [
    ("CLOUDFLARE_R2_ENDPOINT", cloudflare_r2_endpoint),
    ("CLOUDFLARE_R2_ACCESS_KEY", cloudflare_r2_access_key),
    ("CLOUDFLARE_R2_SECRET_KEY", cloudflare_r2_secret_key),
]


def setup():
    for secret_name, value in key_value_pairs:
        try:
            repo.create_secret(
                secret_name=secret_name,
                unencrypted_value=value,
                secret_type="actions",
            )
            printer(f"  ✅Successfully created GitHub Secret {secret_name!r}")
        except Exception as e:
            printer(f"  ❌Failed to create GitHub Secret {secret_name!r}: {e}")
            return


def teardown():
    for secret_name, _ in key_value_pairs:
        try:
            repo.delete_secret(secret_name)
            printer(f"  ✅Successfully deleted GitHub Secret {secret_name!r}")
        except Exception as e:
            printer(f"  ❌Failed to delete GitHub Secret {secret_name!r}: {e}")


if __name__ == "__main__":
    setup()
    # teardown()
