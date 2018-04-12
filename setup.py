from pip.req import parse_requirements
from setuptools import setup, find_packages


requirements = [
    str(line.req) for line in parse_requirements("requirements.txt", session=False)
]


setup(
    name="swagger-aor-generator",
    version="0.0.1",
    description="Generate an Admin on Rest client from a Swagger specification",
    long_description="""
    This utility parses Swagger specifications and creates a main Admin on Rest
    App component in `App.js` along with resource js files containing List, 
    Show, Edit or Create components for each resource found in the swagger 
    specification along with list filters if found. A basic authClient file and
    swaggerRestServer file are included in the generation.
    """,
    author="Praekelt Consulting",
    author_email="dev@praekelt.com",
    license="BSD",
    url="",
    packages=find_packages(),
    install_requires=requirements,
    package_data={
        "templates": ["*.py"]
    },
    tests_require=[],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
