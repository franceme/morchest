#!/usr/bin/env python3
"""
Copyright (c) 2022, Miles Frantz
All rights reserved.
This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree.
"""
# region Imports
import pathlib
from fileinput import FileInput as finput
import os
import sys
from setuptools import find_packages, setup
from pathlib import Path
import glob
from glob import glob as re
try:
	from pylint.reporters.json_reporter import JSONReporter
except:
	pass

# endregion
# region Basic Information
here = os.path.abspath(os.path.dirname(__file__))
py_version = sys.version_info[:2]
NAME = "morchest"
AUTHOR = 'Miles Frantz'
EMAIL = 'frantzme@vt.edu'
DESCRIPTION = 'My short description for my project.'
GH_NAME = "franceme"
URL = f"https://github.com/{GH_NAME}/{NAME}"
long_description = pathlib.Path(f"{here}/README.md").read_text(encoding='utf-8')
REQUIRES_PYTHON = '>=3.8.0'
RELEASE = "?"
entry_point = f"src.{NAME}"
VERSION = "0.0.20"

def grab_version(update_patch:bool=False,update_minor:bool=False,update_major:bool=False):
	update = any([update_patch,update_minor,update_major])
	with finput(__file__,inplace=True) as foil:
		for line in foil:
			if line.startswith("VERSION = "):
				output = line.strip().replace('VERSION = ','').replace('"','').split('.')
				major,minor,patch = int(output[0]),int(output[1]),int(output[2])

				if update_patch:
					patch += 1
				if update_minor:
					minor += 1
				if update_major:
					major += 1

				if update:
					print(f"VERSION = \"{major}.{minor}.{patch}\"")
				else:
					print(line,end='')

			else:
				print(line, end='')
	return

# endregion
# region CMD Line Usage
def selfArg(string):
	return __name__ == "__main__" and len(
		sys.argv) > 1 and sys.argv[0].endswith('/setup.py') and str(
			sys.argv[1]).upper() == str(string).upper()

if selfArg('install'):
	sys.exit(os.system('python3 -m pip install -e .'))
elif selfArg('upload'):
	grab_version(True)
	cmd = f"{sys.executable} setup.py sdist && {sys.executable} -m twine upload --skip-existing dist/* --verbose"
	print(cmd)
	sys.exit(os.system(cmd))
# endregion
# region Setup

setup(
	name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	long_description=long_description,
	long_description_content_type='text/markdown',
	author=AUTHOR,
	author_email=EMAIL,
	command_options={
	},
	python_requires=REQUIRES_PYTHON,
	url=URL,
	packages=find_packages(
		exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
	entry_points={
	},
	install_requires=[
		"funbelts>=0.0.170",
		"orchest",
		"python-telegram-bot"
	],
	include_package_data=True,
	classifiers=[
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.8',
	],
)
# endregion
