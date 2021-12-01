from setuptools import setup
import setuptools

setuptools.setup(version_config=True, setup_requires=["setuptools-git-versioning"])


setup(name='rlxutils',
      description='rlx general purpose utils',
      url='http://github.com/rramosp/rlxutils',
      install_requires=['matplotlib','numpy', 'pandas','joblib',
                        'progressbar2', 'psutil'
                       ],
      scripts=[],
      author='raul ramos',
      author_email='rulix.rp@gmail.com',
      license='MIT',
      packages=['rlxutils'],
      include_package_data=True,
      zip_safe=False)
