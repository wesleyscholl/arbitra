"""Setup configuration for Arbitra."""

from setuptools import setup, find_packages

setup(
    name="arbitra",
    version="0.1.0",
    description="AI Crypto Trading Agent with Capital Preservation",
    packages=find_packages(where="."),
    package_dir={"": "."},
    python_requires=">=3.11",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
    ],
)
