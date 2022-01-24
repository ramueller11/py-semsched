"""
setup.py
Setuptools configuration for project.

Follows guidelines found at:
    https://packaging.python.org/en/latest/tutorials/packaging-projects/
"""
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="semsched-ramueller11",
    version="0.1",
    author="Rob Mueller",
    author_email="ramueller11@gmail.com",
    description="Semantically parse a human readable schedule.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ramueller11/py-semsched",
    project_urls={
        "Bug Tracker": "https://github.com/ramueller11/py-semsched/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Text Processing :: Filters",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Software Development :: Libraries",
        "Topic :: Office/Business :: Scheduling",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=2.7",
)