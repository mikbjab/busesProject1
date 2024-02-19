from setuptools import setup

setup(
    name="busesProject",
    version="0.1.0",
    packages=["transportanalysis"],
    entry_points={
        "console_scripts": [
            "analysis = scripts.main:main",
            "download = scripts.main_download:main"
        ]
    },
    install_requires=["numpy","pandas"]
)