# -*- coding: utf-8 -*-

"""
Requirements::

    pip install "boto3>=1.38.0,<2.0.0"
    pip install "boto_session_manager>=1.7.2,<2.0.0"
    pip install "PyGithub>=2.1.1,<3.0.0"
"""
import typing as T
import json
import dataclasses
from pathlib import Path
from functools import cached_property

import botocore.exceptions
from boto_session_manager import BotoSesManager
from github import Github, Repository

printer = print


@dataclasses.dataclass
class SetupIamUser:
    bsm: BotoSesManager
    aws_region: str
    iam_user_name: str
    tags: dict[str, str]
    policy_document: dict[str, T.Any]
    path_access_key_json: Path
    github_user_name: str
    github_repo_name: str
    github_token: str
    github_secret_name_aws_default_region: str = "AWS_DEFAULT_REGION"
    github_secret_name_aws_access_key_id: str = "AWS_ACCESS_KEY_ID"
    github_secret_name_aws_secret_access_key: str = "AWS_SECRET_ACCESS_KEY"

    @property
    def policy_document_name(self) -> str:
        return f"iam-user-{self.iam_user_name}-inline-policy"

    @property
    def github_secrets_url(self) -> str:
        return f"https://github.com/{self.github_user_name}/{self.github_repo_name}/settings/secrets/actions"

    # printer(f"Preview at {url}")
    @cached_property
    def gh(self) -> Github:
        return Github(self.github_token)

    @cached_property
    def repo(self) -> Repository:
        return self.gh.get_repo(f"{self.github_user_name}/{self.github_repo_name}")

    def s11_create_iam_user(self):
        printer(f"🆕Step 1.1: Create IAM User {self.iam_user_name!r}")
        try:
            self.bsm.iam_client.create_user(
                UserName=self.iam_user_name,
                Tags=[{"Key": key, "Value": value} for key, value in self.tags.items()],
            )
            printer("  ✅Successfully created IAM User.")
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "EntityAlreadyExists":
                printer("  ✅IAM User already exists, do nothing.")
            else:
                raise e

    def s12_put_iam_policy(self):
        printer(f"🆕Step 1.2: Put IAM Policy {self.policy_document_name!r}")
        self.bsm.iam_client.put_user_policy(
            UserName=self.iam_user_name,
            PolicyName=self.policy_document_name,
            PolicyDocument=json.dumps(self.policy_document),
        )
        printer("  ✅Successfully put IAM Policy.")

    def s13_create_or_get_access_key(
        self,
        verbose: bool = True,
    ) -> tuple[str, str]:
        if verbose:
            printer("🆕Step 1.3: Create or get access key")
        res = self.bsm.iam_client.list_access_keys(UserName=self.iam_user_name)
        access_key_list = res.get("AccessKeyMetadata", [])
        if len(access_key_list):
            data = json.loads(self.path_access_key_json.read_text())
            access_key = data["access_key"]
            secret_key = data["secret_key"]
            if verbose:
                printer(f"  ✅Found existing access key {access_key!r}, using it.")
        else:
            response = self.bsm.iam_client.create_access_key(
                UserName=self.iam_user_name
            )
            access_key = response["AccessKey"]["AccessKeyId"]
            secret_key = response["AccessKey"]["SecretAccessKey"]
            data = {"access_key": access_key, "secret_key": secret_key}
            self.path_access_key_json.write_text(json.dumps(data, indent=4))
            if verbose:
                printer(f"  ✅Successfully created new access key {access_key!r}")
        return access_key, secret_key

    def s14_setup_github_secrets(self):
        printer("🆕Step 1.4: Setup GitHub Secrets")
        printer(f"  👀Preview at {self.github_secrets_url}")
        access_key, secret_key = self.s13_create_or_get_access_key(verbose=False)
        key_value_pairs = [
            (self.github_secret_name_aws_default_region, self.aws_region),
            (self.github_secret_name_aws_access_key_id, access_key),
            (self.github_secret_name_aws_secret_access_key, secret_key),
        ]
        for secret_name, value in key_value_pairs:
            try:
                self.repo.create_secret(
                    secret_name=secret_name,
                    unencrypted_value=value,
                    secret_type="actions",
                )
                printer(f"  ✅Successfully created GitHub Secret {secret_name!r}")
            except Exception as e:
                printer(f"  ❌Failed to create GitHub Secret {secret_name!r}: {e}")
                return

    def s21_delete_github_secrets(self):
        printer("🗑Step 2.1: Delete GitHub Secrets")
        printer(f"  👀Preview at {self.github_secrets_url}")
        key_list = [
            self.github_secret_name_aws_default_region,
            self.github_secret_name_aws_access_key_id,
            self.github_secret_name_aws_secret_access_key,
        ]
        for secret_name in key_list:
            try:
                self.repo.delete_secret(secret_name)
                printer(f"  ✅Successfully deleted GitHub Secret {secret_name!r}")
            except Exception as e:
                printer(f"  ❌Failed to delete GitHub Secret {secret_name!r}: {e}")

    def s22_delete_access_key(self):
        data = json.loads(self.path_access_key_json.read_text())
        access_key = data["access_key"]
        printer(f"🗑Step 2.2: Delete access key {access_key!r}")
        try:
            self.bsm.iam_client.delete_access_key(
                UserName=self.iam_user_name,
                AccessKeyId=access_key,
            )
            printer("  ✅Successfully deleted access key.")
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                printer("  ✅Access key does not exist, nothing to delete.")
            else:
                raise e

    def s23_delete_iam_policy(self):
        printer(f"🗑Step 2.3: Delete IAM Policy {self.policy_document_name!r}")
        try:
            self.bsm.iam_client.delete_user_policy(
                UserName=self.iam_user_name,
                PolicyName=self.policy_document_name,
            )
            printer("  ✅Successfully deleted IAM Policy.")
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                printer("  ✅IAM Policy does not exist, nothing to delete.")
            else:
                raise e

    def s24_delete_iam_user(self):
        printer(f"🗑Step 2.4: Delete IAM User {self.iam_user_name!r}")
        try:
            self.bsm.iam_client.delete_user(UserName=self.iam_user_name)
            printer("  ✅Successfully deleted IAM User.")
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                printer("  ✅IAM User does not exist, nothing to delete.")
            else:
                raise e
