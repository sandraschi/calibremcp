from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="calibre-mcp",
    version="0.1.0",
    author="Sandra Schi",
    author_email="sandra@example.com",
    description="MCP server for automating Calibre ebook management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sandraschi/calibremcp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "fastmcp>=2.10.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
        "calibre>=6.0.0",
        "calibre-web>=0.6.0",
    ],
    entry_points={
        "console_scripts": [
            "calibre-mcp=calibremcp.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
