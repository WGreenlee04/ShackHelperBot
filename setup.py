import sys

from setuptools import setup, find_packages

base = None
if sys.platform == 'win64':
    base = 'WIN64GUI'

setup(name='ShackHelperBot',
      version='1.0.3rc3',
      description='A bot for discord to assist Taco Shack',
      author='William Greenlee',
      author_email='williamgreenlee04@gmail.com',
      url='https://github.com/WGreenlee04/ShackHelperBot',
      scripts=['main.py', 'objects.py'],
      packages=find_packages(),
      install_requires=['discord.py~=1.4.1']
      )
