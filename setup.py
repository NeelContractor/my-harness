from setuptools import setup

setup(
    name="my-harness",
    version="1.0.0",
    description="A layered AI agent harness built from scratch",
    packages=[
        "layer_01", "layer_02", "layer_03", "layer_04",
        "layer_05", "layer_06", "layer_07", "layer_08",
        "layer_09", "layer_10", "layer_11",
    ],
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27.0",
        "python-dotenv>=1.0.0",
        "beautifulsoup4>=4.12.0",
        "watchdog>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "harness=layer_10.cli:main",
        ],
    },
)