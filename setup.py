from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pygdtf",
    version="1.0.3",
    description="General Device Type Format library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Jack Page, vanous",
    author_email="noreply@nodomain.com",
    packages=["pygdtf", "pygdtf.utils"],
    url="https://github.com/open-stage/python-gdtf",
    project_urls={
        "Source": "https://github.com/open-stage/python-gdtf",
        "Changelog": "https://github.com/open-stage/python-gdtf/blob/master/CHANGELOG.md",
    },
)
