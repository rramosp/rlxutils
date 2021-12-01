from setuptools import setup
import setuptools

#setuptools.setup(version_config=True, setup_requires=["setuptools-git-versioning"])



setup(name='rlxutils',
      install_requires=['matplotlib','numpy', 'pandas','joblib',
                        'progressbar2', 'psutil'
                       ],
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      scripts=[],
      packages=['rlxutils'],
      include_package_data=True,
      zip_safe=False)
