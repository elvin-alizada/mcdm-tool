from setuptools import setup, find_packages

setup(
    name="mcdm",  # paket adı
    version="0.1.0",
    description="Multi-Criteria Decision Making (AHP, TOPSIS) toolkit",
    author="Elvin Əlizadə",
    author_email="elvin.e.alizada@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
    ],
    python_requires=">=3.8",
)

