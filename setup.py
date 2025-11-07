"""Setup configuration for ffmcp"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ffmcp",
    version="0.1.5",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI command-line tool inspired by ffmpeg",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brandonhenry/ffmcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "httpx>=0.24.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.18.0"],
        "all": ["openai>=1.0.0", "anthropic>=0.18.0"],
    },
    entry_points={
        "console_scripts": [
            "ffmcp=ffmcp.cli:cli",
        ],
    },
)

