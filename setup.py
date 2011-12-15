from setuptools import setup

version = '0.2'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('TODO.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'django-extensions',
    'django-nose',
    'lizard-ui',
    'pkginfo',
    'xlrd',
    ]

tests_require = [
    ]

setup(name='lizard-rijnmond',
      version=version,
      description="Deltaportaal lizard-map plugin for Rijnmond-Drechtsteden",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout.vanrees@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=['lizard_rijnmond'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require = {'test': tests_require},
      entry_points={
          'console_scripts': [
          ],
        'lizard_map.adapter_class': [
            'adapter_rijnmond_segments = lizard_rijnmond.layers:SegmentAdapter',
            'adapter_rijnmond_riverlines = lizard_rijnmond.layers:RiverlineAdapter',
            ],
          },
      )
