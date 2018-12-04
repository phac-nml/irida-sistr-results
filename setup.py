from distutils.core import setup

from setuptools import find_packages

from irida_sistr_results.version import __version__

classifiers = """
Development Status :: 4 - Beta
Environment :: Console
License :: OSI Approved :: Apache Software License
Intended Audience :: Science/Research
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Bio-Informatics
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Operating System :: POSIX :: Linux
""".strip().split('\n')

setup(name='irida-sistr-results',
      version=__version__,
      description='Exports SISTR results available through IRIDA into a single report.',
      author='Aaron Petkau',
      author_email='aaron.petkau@gmail.com',
      url='https://github.com/phac-nml/irida-sistr-results',
      license='Apache v2.0',
      classifiers=classifiers,
      install_requires=[
          'rauth>=0.7.3',
          'urllib3>=1.21.1',
          'XlsxWriter>=0.9.8',
          'appdirs>=1.4.3',
          'pandas>=0.23.0'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      packages=find_packages(),
      include_package_data=True,
      scripts=['bin/irida-sistr-results']
      )
