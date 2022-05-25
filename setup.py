from setuptools import setup  # type: ignore[import]


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="eiffel",
    version="0.3.4",
    packages=["eiffel"],
    package_data={
        "eiffel": ["__init__.py", "py.typed", "debugimpl.py",
                   "optimizedimpl.py", "test_eiffel.py"],
    },

    zip_safe=True,
    author="Alan Cristhian",
    author_email="alan.cristh@gmail.com",
    description="Another Python Design By Contract implementation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
        'Typing :: Typed'
      ],
    license="MIT",
    keywords="design by contract, eiffel",
    url="https://github.com/AlanCristhian/eiffel",
)
