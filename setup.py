from setuptools import setup, find_packages

setup(
    name="botapi",
    version="2024.11.21",
    install_requires=[
        "httpx",
        "pydantic",
        "bs4",
        "orjson",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
)