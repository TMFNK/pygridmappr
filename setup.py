"""
Setup configuration for pygridmappr
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pygridmappr",
    version="0.1.1",
    author="Python port of gridmappr by Roger Beecham",
    author_email="",
    description="Python implementation of R package gridmappr for automated gridmap layout generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tmfnk/pygridmappr",
    license="AGPL-3.0-or-later",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.1.0",
        "scipy>=1.5.0",
        "matplotlib>=3.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.9",
            "jupyter>=1.0",
        ],
    },
    keywords="gridmap, tilemaps, cartography, geovisualization, small-multiples, assignment-problem, hungarian-algorithm",
    project_urls={
        "Bug Reports": "https://github.com/tmfnk/pygridmappr/issues",
        "Source": "https://github.com/tmfnk/pygridmappr",
        "Original R Package": "https://github.com/rogerbeecham/gridmappr",
    },
)
