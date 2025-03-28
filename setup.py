from setuptools import find_packages, setup

setup(
    name="django-nexus-auth",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "Django>=4.2.19",
        "djangorestframework>=3.14.0",
        "djangorestframework-simplejwt>=5.4.0",
    ],
    author="Gabriel Tan",
    author_email="gabriel.tan@panevo.com",
    description="OIDC Authentication for Django REST Framework with JWT support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/panevo/django-nexus-auth",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
