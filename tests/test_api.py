# -*- coding: utf-8 -*-

from sakura_gather import api


def test():
    _ = api


if __name__ == "__main__":
    from sakura_gather.tests import run_cov_test

    run_cov_test(
        __file__,
        "sakura_gather.api",
        preview=False,
    )
