import setuptools
import subprocess

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = subprocess.check_output('bin/get_version', shell=True).decode()

setuptools.setup(
    name="resource_resolver",
    version=version,
    author="Moye Odiase",
    author_email="moyeodiase@hotmail.co.uk",
    description="Resource Resolver",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Moyoka22/resource-resolver.git",
    project_urls={
        "Bug Tracker": "https://github.com/Moyoka22/resource-resolver/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[

        "attrs>=21.2.0",
        "autopep8>=1.5.7",
        "boto3>=1.18.1",
        "botocore>=1.21.1",
        "build>=0.6.1",
        "iniconfig>=1.1.1",
        "jmespath>=0.10.0",
        "numpy>=1.21.0",
        "packaging>=20.9",
        "pandas>=1.3.0",
        "pep517>=0.11.0",
        "pip>=21.2.2",
        "pluggy>=0.13.1",
        "py>=1.10.0",
        "pyarrow>=5.0.0",
        "pycodestyle>=2.7.0",
        "pyparsing>=2.4.7",
        "pytest>=6.2.4",
        "python-dateutil>=2.8.1",
        "pytz>=2021.1",
        "s3transfer>=0.5.0",
        "setuptools>=57.4.0",
        "six>=1.16.0",
        "toml>=0.10.2",
        "tomli>=1.2.1",
        "urllib3>=1.26.6",
        "wheel>=0.36.2",
    ]
)
