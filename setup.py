# setup.py
import configparser
# Monkey-patch for Python 3: define SafeConfigParser for stdeb compatibility
configparser.SafeConfigParser = configparser.RawConfigParser

from setuptools import setup, find_packages

# Load long description from README
with open("README.md", encoding="utf-8") as f:
    long_desc = f.read()

setup(
    name="distributed-task-system",
    version="1.0",
    description="A simple distributed task offload system",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Osama Awartany",
    author_email="osama@example.com",
    url="https://github.com/yourusername/distributed-task-system",
    packages=find_packages(include=["offload_core", "offload_core.*"]),
    py_modules=["dts_cli"],  # Include the CLI helper module
    install_requires=[
        "flask",
        "requests",
        "psutil",
        "zeroconf",
        "flask_cors",
        "numpy",
        "uvicorn"
    ],
    entry_points={
        "console_scripts": [
            "dts-start=dts_cli:main",
        ],
    },
    data_files=[
        ("/etc/systemd/system", ["dts.service"])
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
)


# dts_cli.py
# CLI entry-point module for the Distributed Task System
# Place this next to setup.py

def main():
    """
    Main entry for dts-start console script.
    Launches the FastAPI/Flask app via Uvicorn.
    """
    # Import your application instance here:
    try:
        from offload_core.main import app
    except ImportError:
        # If you have a factory, adjust accordingly:
        from offload_core.main import create_app
        app = create_app()

    # Run with Uvicorn
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7520)

