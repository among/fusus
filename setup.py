from setuptools import setup

setup(
    name="pipeline",
    packages=[
        "pipeline",
    ],
    install_requires=[
        "pyyaml",
        "ipython",
        "numpy",
        "pillow",
        "opencv-contrib-python",
        "text-fabric",
    ],
    python_requires=">=3.7.0",
    include_package_data=True,
    exclude_package_data={"": ["pipeline.egg-info", "__pycache__", ".DS_Store"]},
    zip_safe=False,
    version='0.0.1',
    description="""Pipeline for converting Arabic scanned pages into readable text""",
    author="Cornelis van Lit, Dirk Roorda",
    author_email="info@annotation.nl",
    url="https://github.com/among/fusus",
    keywords=[
        "text",
        "image processing",
        "arabic",
        "OCR",
        "medieval",
        "islam",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Religion",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Natural Language :: Arabic",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Religion",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Sociology :: History",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Fonts",
        "Topic :: Text Processing :: Markup",
    ],
    long_description="""\
Pipeline from scanned pages of Arabic Medieval books to readable text.
With cleaning before OCR, OCR itself, and postprocessing.
Tools to read text corpora with (linguistic) annotations
and process them efficiently.
With a built in web-interface for querying a corpus.
More info on https://among.github.io/fusus/
""",
)
