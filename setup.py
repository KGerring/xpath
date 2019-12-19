
import io
from setuptools import find_packages, setup

with open("xpath/__version__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split("=")[1].strip(" '\"")
            break
    else:
        version = "0.1.0"
with open("README.rst", "r", encoding="utf-8") as f:
    readme = f.read()

packages = find_packages()

setup(
    name="xpath",
    version=version,
    long_description=readme,
    license="MIT/Apache-2.0",
    test_suite='tests',
    packages=find_packages(),
)