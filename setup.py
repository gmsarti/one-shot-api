from setuptools import find_packages, setup

setup(
    name="one-shot-api",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn>=0.34.0",
        "langchain>=0.3.0",
        "langchain-community>=0.0.10",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "one-shot-api=one_shot_api.__main__:main",
        ],
    },
)
