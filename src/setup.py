import setuptools
from version import *


def read_requirements(path):
    requirements = []
    with open(path, encoding="utf-8") as fp:
        for line in fp:
            requirement = line.strip()
            if (
                not requirement
                or requirement.startswith("#")
                or requirement.startswith("--")
            ):
                continue
            requirements.append(requirement)
    return requirements

def main():
    with open("../README.md", encoding="utf-8") as f:
        long_description = f.read()

    install_requires = read_requirements("../requirements.txt")

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
            "Programming Language :: Python :: 3.12",
            'License :: OSI Approved :: MIT License',
            "Operating System :: OS Independent",
        ],
        python_requires=">=3.12.10,<3.13",
        project_urls={
            "Youtube": "https://www.youtube.com/playlist?list=PL3uuKTASzjRYNdl7wYlgUd7agQIA2_y5V",
            "Documentation": "https://github.com/YaoXuanZhi/ScreenPinKit/wiki",
            "Source Code": "https://github.com/YaoXuanZhi/ScreenPinKit",
            "Bug Tracker": "https://github.com/YaoXuanZhi/ScreenPinKit/issues",
        },
        py_modules=["main"],
        entry_points={"console_scripts": ["ScreenPinKit = main:main"]},
    )


if __name__ == "__main__":
    main()
