from setuptools import setup

setup(
    name="mpd_radioalarm",
    version="0.0.1",
    author="Philp Stoop",
    author_email="philip.stoop@hotmail.com",
    description="Web Frontend for MPD with Radio and Audio Playback inclusive "
                "time controlled playback",
    license="LICENSE.txt",
    packages=["mpd_radioalarm", "mpd_radioalarm.data"],
    install_requires=[
        "tornado",
        "python-mpd2",
        "jsonschema",
        "peewee",
        "uuid"
    ]
)