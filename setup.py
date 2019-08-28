from setuptools import setup, find_namespace_packages

with open("README.md", "r") as openReadMe:
    long_description = openReadMe.read()

setup(
    name="Group Buy Organizer",
    version="1.0.2",
    author="Mark Michon",
    author_email="markmichon7@gmail.com",
    description="📦 Quickly coordinate large wholesale group orders with this easy to use web app.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarkMichon1/Group-Buy-Organizer",
    packages=find_namespace_packages(),
    install_requires=[
        'flask',
        'flask-bcrypt',
        'flask-login',
        'flask-sqlalchemy',
        'flask-wtf',
        'pdfkit',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)