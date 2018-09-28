try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(name='pManager',
      py_modules=['pmanager'],
      version='0.6.4',
      license='MIT',
      description='Collection of scripts for image management',
      long_description=long_description,
      author='Stephan Weiss',
      author_email=' ',
      url='',
      download_url='',
      keywords=['photo management', 'feh','video management'],
      classifiers=["Topic :: Scientific/Engineering",
                   "License :: OSI Approved :: MIT License",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.5",
                   "Development Status :: 1 - Beta"],

      #install_requires=['PIL','glob'],

      entry_points={
          'console_scripts': [
              'pmanager = pmanager:main',
              ]
		}
      )
