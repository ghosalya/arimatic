from setuptools import setup, find_packages

setup(
    author='Natuna',
    name='arimatic',
    install_requires=[],
    version="0.0.1",
    packages=find_packages(exclude=["tests_*", "*example*"]),
    entry_points="""
    [console_scripts]
    arimatic=arimatic.launcher:run
    """
)