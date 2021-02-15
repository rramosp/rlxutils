from setuptools import setup
exec(open('rlxutils/version.py').read())

setup(name='rlxutils',
      version=__version__,
      description='rlx general purpose utils',
      url='http://github.com/rramosp/rlxutils',
      install_requires=['matplotlib','numpy', 'pandas','joblib',
                        'progressbar2', 'psutil', 'bokeh', 'pyshp',
                        'statsmodels'],
      scripts=[],
      author='rlx',
      author_email='rulix.rp@gmail.com',
      license='MIT',
      packages=['rlxutils'],
      include_package_data=True,
      zip_safe=False)
