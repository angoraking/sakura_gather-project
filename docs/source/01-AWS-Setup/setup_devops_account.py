# -*- coding: utf-8 -*-

from pathlib import Path
from boto_session_manager import BotoSesManager
from home_secret.api import hs
from aws_iam_user_setup_library import SetupIamUser

aws_region = "us-east-1"
bsm = BotoSesManager(profile_name="bmt_app_devops_us_east_1", region_name=aws_region)
aws_codeartifact_domain = "bmt"
aws_codeartifact_repository = "bmt-python"
setup = SetupIamUser(
    bsm=bsm,
    aws_region=aws_region,
    iam_user_name="gh-ci-sakura_gather",
    tags={
        "tech:use_case": "for GitHub Action to access AWS CodeArtifact",
        "github_username": "angoraking",
        "github_repo": "sakura_gather-project",
        "automation_script": "https://github.com/angoraking/sakura_gather-project/blob/main/docs/source/01-AWS-Setup/setup_dev_account.py",
    },
    policy_document={
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "codeartifact:DescribeDomain",
                    "codeartifact:DescribePackage",
                    "codeartifact:DescribePackageGroup",
                    "codeartifact:DescribePackageVersion",
                    "codeartifact:DescribeRepository",
                    "codeartifact:GetAssociatedPackageGroup",
                    "codeartifact:GetAuthorizationToken",
                    "codeartifact:GetDomainPermissionsPolicy",
                    "codeartifact:GetPackageVersionAsset",
                    "codeartifact:GetPackageVersionReadme",
                    "codeartifact:GetRepositoryEndpoint",
                    "codeartifact:GetRepositoryPermissionsPolicy",
                    "codeartifact:ListAllowedRepositoriesForGroup",
                    "codeartifact:ListAssociatedPackages",
                    "codeartifact:ListPackageGroups",
                    "codeartifact:ListPackages",
                    "codeartifact:ListPackageVersionAssets",
                    "codeartifact:ListPackageVersionDependencies",
                    "codeartifact:ListPackageVersions",
                    "codeartifact:ListRepositoriesInDomain",
                    "codeartifact:ListSubPackageGroups",
                    "codeartifact:ListTagsForResource",
                    "codeartifact:ReadFromRepository",
                ],
                "Resource": [
                    f"arn:aws:codeartifact:{bsm.aws_region}:{bsm.aws_account_id}:domain/{aws_codeartifact_domain}",
                    f"arn:aws:codeartifact:{bsm.aws_region}:{bsm.aws_account_id}:repository/{aws_codeartifact_domain}/{aws_codeartifact_repository}",
                    f"arn:aws:codeartifact:{bsm.aws_region}:{bsm.aws_account_id}:package/{aws_codeartifact_domain}/*/*/*/*",
                    f"arn:aws:codeartifact:{bsm.aws_region}:{bsm.aws_account_id}:package-group/{aws_codeartifact_domain}*",
                ],
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": ["codeartifact:ListRepositories", "codeartifact:ListDomains"],
                "Resource": "*",
            },
            {
                "Sid": "VisualEditor2",
                "Effect": "Allow",
                "Action": "sts:GetServiceBearerToken",
                "Resource": "*",
            },
        ],
    },
    path_access_key_json=Path(__file__)
    .absolute()
    .parent.joinpath("devops_access_key.json"),
    github_user_name="angoraking",
    github_repo_name="sakura_gather-project",
    github_token=hs.v("providers.github.accounts.ak.users.ak.secrets.dev.value"),
)

if __name__ == "__main__":

    def setup_all():
        setup.s11_create_iam_user()
        setup.s12_put_iam_policy()
        setup.s13_create_or_get_access_key()
        setup.s14_setup_github_secrets()

    def teardown_all():
        setup.s21_delete_github_secrets()
        setup.s22_delete_access_key()
        setup.s23_delete_iam_policy()
        setup.s24_delete_iam_user()

    # setup_all()
    # teardown_all()
