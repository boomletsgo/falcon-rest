from setuptools import setup, find_packages


classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries',
]

setup(
    name='falcon-rest',
    author='Jordan Ambra',
    author_email='jordan@serenitysoftware.io',
    url='https://github.com/boomletsgo/falcon-rest',
    version='0.1.1',
    classifiers=classifiers,
    description='Falcon REST framework for API automation',
    keywords='falcon rest framework json',
    packages=["falcon_rest"],
    install_requires=["falcon>=1.0.0", "falcon-json-middleware>=0.3.1"],
    include_package_data=True,
    license='The Unlicense',
)
