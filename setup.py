#!/usr/bin/env python
from pathlib import Path

from setuptools import setup, find_packages


install_requires = [
    "click",
    "numpy",
    "tensorflow",
    "tensorflow-hub",
    "hnswlib",
    "starlette",
    "uvicorn",
    "requests",
    "tabulate",
    "discord.py",
]

version_file = Path(__file__).parent.joinpath("autoguru", "VERSION.txt")
version = version_file.read_text(encoding="UTF-8").strip()

with open("README.md", "r", encoding="UTF-8") as in_file:
    long_description = in_file.read()

setup(
    name="autoguru",
    version=version,
    author="Rob Rua",
    author_email="robertrua@gmail.com",
    url="https://github.com/robrua/autoguru",
    description="Question Answering for FAQs with Natural Language Processing",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url="https://github.com/robrua/autoguru/archive/v{}.tar.gz".format(
        version
    ),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Customer Service",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Communications :: Chat",
        "Topic :: Documentation",
        "Typing :: Typed",
    ],
    keywords=[],  # TODO
    packages=find_packages(),
    entry_points={"console_scripts": ["autoguru=autoguru.__main__:autoguru"]},
    zip_safe=True,
    python_requires=">=3.5",
    install_requires=install_requires,
    include_package_data=True,
)
