# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from sakura_gather.tests import run_cov_test

    run_cov_test(
        __file__,
        "sakura_gather",
        is_folder=True,
        preview=False,
    )
