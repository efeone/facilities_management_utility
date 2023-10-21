from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in facilities_management_utility/__init__.py
from facilities_management_utility import __version__ as version

setup(
	name="facilities_management_utility",
	version=version,
	description="Facilities Management Utility",
	author="efeone",
	author_email="info@efeone.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
