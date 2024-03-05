from setuptools import find_packages, setup

setup(
    name="eclipse-ai",
    version="1.0.0b2",
    description="AI Powered Sensitive Information Detector",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="David I",
    author_email="david@berylliumsec.com",
    url="https://github.com/berylliumsec/eclipse",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: Text Processing :: Linguistic",
    ],
    license="BSD",
    keywords="AI, PII, Machine Learning, Sensitive Information Detection, Privacy",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={"eclipse": ["images/*"]},  # Make sure this path is correct
    install_requires=[
        "torch>=1.0.1",  # Specify versions if needed
        "transformers>=4.34.0",  # Specify versions if needed
        "requests",  # Add any additional packages you require
        "termcolor",  # Specify versions if needed
        "prompt_toolkit",  # Specify versions if needed
    ],
    entry_points={
        "console_scripts": ["eclipse=eclipse.eclipse:main"],
    },
    python_requires=">=3.10",
)
