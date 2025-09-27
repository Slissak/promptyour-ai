"""Setup configuration for the project."""

from setuptools import setup, find_packages

setup(
    name="promp-your-ai",
    version="0.1.0",
    description="A Python project with frontend, backend, tests, and evaluations",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Add your dependencies here
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "backend=backend.main:main",
            "frontend=frontend.app:create_app",
            "evaluate=evaluations.run_evaluations:run_all_evaluations",
        ],
    },
)