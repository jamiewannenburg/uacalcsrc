from setuptools import setup, find_packages

setup(
    name="uacalc-python",
    version="0.2.0",
    description="Pure Python utilities for UACalc",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "typing-extensions>=3.7.4",
    ],
    python_requires=">=3.7",
)
