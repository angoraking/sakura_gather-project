# -*- coding: utf-8 -*-

import os
from pathlib_mate import Path
from boto_session_manager import BotoSesManager
from sakura_site_msav.project.define import Project
from sakura_site_msav.constants import LangCodeEnum

project = Project(
    dir_root_str=str(Path.home().joinpath(".projects", "sakura_site_msav")),
    snapshot_md5=None,
    lang_code_list=[
        LangCodeEnum.cn.value,
    ],
    aws_profile=None,
    aws_region="us-east-1",
    s3uri_root="s3://bmt-app-dev-us-east-1/projects/sakura_site_msav/",
    cloudflare_r2_endpoint=os.environ["CLOUDFLARE_R2_ENDPOINT"],
    cloudflare_r2_access_key=os.environ["CLOUDFLARE_R2_ACCESS_KEY"],
    cloudflare_r2_secret_key=os.environ["CLOUDFLARE_R2_SECRET_KEY"],
    dir_library_str=str(Path.home().joinpath("library")),
)
bsm_dev = BotoSesManager(
    aws_access_key_id=os.environ["DEV_ACC_AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["DEV_ACC_AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["DEV_ACC_AWS_REGION"],
)
with bsm_dev.awscli():
    project.bsm.print_who_am_i(masked=True)
# project.crawl_all_video_details_in_one_html_database(
#     lang_code=LangCodeEnum.cn.value,
#     node_id=0,
#     big_batch_size=10,
#     micro_batch_size=3,
# )

from sakura_site_msav.project.s04_2_crawl_website_mixin import RoundRobinManager
next_node_id = RoundRobinManager.get_next_node_id(bsm=project.bsm)
project.crawl_all_video_details_in_one_html_database(
    lang_code=LangCodeEnum.cn.value,
    node_id=next_node_id,
    reset_lock=True,
)
# project.step_04_01_crawl_all_video_details_in_all_html_database(
#     lang_code=LangCodeEnum.cn.value,
# )
