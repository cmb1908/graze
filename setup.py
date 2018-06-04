import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graze",
    version="0.0.2",
    author="Craig Brown",
    author_email="cmb1908@gmail.com",
    description="Generic web scraping framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmb1908/graze",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        "console_scripts": [
            "graze = graze.graze:main"
        ]
    }
)

