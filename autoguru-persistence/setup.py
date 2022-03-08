#!/usr/bin/env python
from pathlib import Path

from setuptools import find_namespace_packages, setup

install_requires = ["tortoise-orm"]

extras_require = {
    "sqlite": ["tortoise-orm[aiosqlite]"],
    "postgres": ["tortoise-orm[asyncpg]"],
    "mysql": ["tortoise-orm[aiomysql]"],
}

version_file = Path(__file__).parent.joinpath("autoguru", "persistence", "VERSION.txt")
version = version_file.read_text(encoding="UTF-8").strip()

with open("README.md", "r", encoding="UTF-8") as in_file:
    long_description = in_file.read()

setup(
    name="autoguru-persistence",
    version=version,
    author="Rob Rua",
    author_email="robertrua@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"autoguru": "autoguru"},
    packages=find_namespace_packages(include=["autoguru.*"]),
    zip_safe=True,
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
)
