from setuptools import setup, find_packages

module_name = "pvi"

setup(
    name=module_name,
    version='',
    description='PV Interface described in YAML',
    url='https://github.com/dls-controls/pvi',
    author='Yousef Moazzam',
    author_email='yousef.moazzam@diamond.ac.uk',
    keywords='',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
    license='APACHE',
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=[
        'nose>=1.3.0',
        'mock>=1.0.1'
    ],
    zip_safe=False,
)
