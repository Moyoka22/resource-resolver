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

)
