from setuptools import find_packages, setup, Command

# https://github.com/pypa/pypi-legacy/issues/148
try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except ImportError:
    LONG_DESCRIPTION = open('README.md').read()

setup(
    name='kako',
    version='1.1.0',
    description='Manifest driven IoT honeypots',
    long_description=LONG_DESCRIPTION,
    author='Peter Adkins',
    author_email='peter.adkins@kernelpicnic.net',
    url='https://www.github.com/darkarnium/kako',
    packages=find_packages('src'),
    license='MIT',
    download_url='https://github.com/darkarnium/kako/archive/1.1.0.tar.gz',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    package_dir={
        'kako': 'src/kako',
    },
    scripts=[
        'src/kako-master'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    install_requires=[
        'click==7.1.2',
        'boto3==1.14.48',
        'PyYAML==5.3.1',
        'requests==2.24.0',
        'cerberus==1.3.2',
    ]
)
