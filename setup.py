from setuptools import setup, find_packages

installRequires = []
dependencyLinks = []

tmp = {}
execfile("influxhtm/version.py", {}, tmp)
version = tmp["version"]

with open("requirements.txt", "r") as reqfile:
  for line in reqfile:
    installRequires.append(line.strip())

setup(
  name = "influxhtm",
  version = version,
  description = "InfluxDB interface for use with HTM systems.",
  packages = find_packages(),
  include_package_data=True,
  install_requires = installRequires,
)
