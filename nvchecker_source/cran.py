# MIT licensed
# Copyright (c) 2021- hubutui <hot123tea123@gmail.com>
import configparser

from nvchecker.api import session

CRAN_URL = 'https://cran.r-project.org/src/contrib/PACKAGES'

async def get_versions(url: str):
    result = {}
    res = await session.get(url)
    config = configparser.ConfigParser()
    for item in res.body.decode("UTF-8").split("\n\n"):
        if item.startswith("Package: "):
            rpkgname = item.split('\n')[0].replace(' ', '').split(':')[1]
            config.read_string(f"[{rpkgname}]\n" + item)
            result[rpkgname] = config[rpkgname]["version"]

    return result

async def get_version(name, conf, *, cache, **kwargs):
    rpkgname = conf.get('cran', name)
    versions = await cache.get(CRAN_URL, get_versions)

    return versions[rpkgname]
