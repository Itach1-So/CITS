from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cits-lang",
    version="1.0.0",
    author="Your Name",
    description="CITS - A Simple BASIC-like Programming Language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cits",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Interpreters",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "cits=cits.main:main",
        ],
    },
)