from setuptools import setup, find_packages

setup(
    name="botapi",
    version="2025.03.13",
    install_requires=[
        "httpx",
        "pydantic",
        "bs4",
        "orjson",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
)