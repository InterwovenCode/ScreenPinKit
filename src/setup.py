import setuptools
from version import *
from pkg_resources import parse_requirements

with open("../README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("../requirements.txt", encoding="utf-8") as fp:
    install_requires = [str(requirement) for requirement in parse_requirements(fp)]

setuptools.setup(
    name="ScreenPinKit",
    version=VERSION,
    keywords="pyqt ScreenPinKit screenshot screen-paint",
    author="YaoXuanZhi",
    author_email="yaoxuanzhi@outlook.com",
    description="A mini screenshot and annotation tool that incorporates ideas from Snipaste, Excalidraw, ShareX, and others.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/YaoXuanZhi/ScreenPinKit",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    extras_require={},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Youtube": "https://www.youtube.com/playlist?list=PL3uuKTASzjRYNdl7wYlgUd7agQIA2_y5V",
        "Documentation": "https://github.com/YaoXuanZhi/ScreenPinKit/wiki",
        "Source Code": "https://github.com/YaoXuanZhi/ScreenPinKit",
        "Bug Tracker": "https://github.com/YaoXuanZhi/ScreenPinKit/issues",
    },
    py_modules=["main"],
    entry_points={"console_scripts": ["ScreenPinKit = main:main"]},
)
