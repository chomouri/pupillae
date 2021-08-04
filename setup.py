import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pupillae",
    version="0.1.1",
    author="Jason Henson",
    author_email="jason.matthew.henson@gmail.com",
    description="A coven of tools for PnP RPGs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chomouri/pupillae",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 2 - Pre-Alpha",
    ],
    package_dir={"src": ""},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
