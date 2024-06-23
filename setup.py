from setuptools import setup

setup(name='pyblog',
      version='0.6.3',
      description='Lightweight python static blog generator',
      long_description=open('README.rst').read(),
      url='http://github.com/addu390/pyblog',
      author='Cesar Parent',
      author_email='yo@pyblog.xyz',
      license='MIT',
      packages=['pyblog'],
      install_requires=[
          'python-dateutil',
          'markdown',
          'jinja2',
          'pygments',
          'watchdog'
      ],
      entry_points={
          'console_scripts': [
              'pyblog = pyblog.entry:main'
          ],
      },
      zip_safe=False)
