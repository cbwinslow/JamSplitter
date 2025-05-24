from pathlib import Path
from setuptools import setup, find_packages

def read_requirements():
    """Read requirements from requirements.txt."""
    with open("requirements.txt", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("#")]

def read_long_description():
    """Read the long description from README.md."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return ""

def main() -> None:
    """Run setup configuration."""
    setup(
        name="jam-splitter",
        version="0.1.0",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        install_requires=read_requirements(),
        python_requires=">=3.11",
        # Additional metadata
        author="Your Name",
        author_email="your.email@example.com",
        description="JamSplitter - Split your music into stems and generate lyrics",
        long_description=read_long_description(),
        long_description_content_type="text/markdown",
        url="https://github.com/yourusername/jam-splitter",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.11",
            "Topic :: Multimedia :: Sound/Audio :: Analysis",
        ],
    )

if __name__ == "__main__":
    main()
