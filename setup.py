from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eww-notifier",
    version="1.0.0",
    author="KhalidWKhedr",
    author_email="",  # Add your email if you want
    description="A custom DBus notification service for Linux desktops, designed to work with eww",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KhalidWKhedr/eww-notifier",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Desktop Environment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyGObject>=3.42.0",
        "pydbus>=0.6.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "eww-notifier=eww_notifier.__main__:main",
        ],
    },
) 