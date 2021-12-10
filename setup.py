import os
import sys
import ensurepip
ensurepip.bootstrap(upgrade=True)
import pip
from setuptools import setup

majorver = int(pip.__version__.split('.')[0])
if majorver < 21:
    print('pip version too low! pip will now be upgraded')
    os.system(f'{sys.executable} -m pip install --upgrade pip')
    from importlib import reload
    reload(pip)


setup(name='aisdb',
      version='0.1',
      description='AIS Database and Processing Utils',
      author='Matt Smith',
      author_email='matthew.smith@dal.ca',
      url='https://gitlab.meridian.cs.dal.ca/matt_s/ais_public',
      license='GNU General Public License v3.0',
      python_requires='>=3.8',
      packages=[
          'aisdb', 'aisdb.database', 'aisdb.webdata', 
        ],
      setup_requires=[
          'cython',
          #'setuptools',
          'pip>=21.1.0',
          'wheel',
        ],
      install_requires=[
          'numpy',
          'packaging', 
          'pip>=21.1.0',
          'pyais', 
          'pysqlite3-binary', 
          'rasterio', 
          'requests', 
          'scikit-learn',
          'selenium', 
          'shapely', 
          'tqdm',
        ],
      tests_requires=[
          'pytest',
          #'pytest-monitor',
          'sphinx', # required for building docs
        ],
     )

