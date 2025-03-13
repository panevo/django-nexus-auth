from setuptools import setup, find_packages
import os


setup(
    name="django-nexus-auth",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Django>=3.2",
        "djangorestframework>=3.12.0",
        "django-tenants>=3.4.0",
        "djangorestframework-simplejwt>=3.1.1"
    ],
    author="Panevo Services Ltd.",
    author_email="dev@iotorq-lean.com",
    description="OIDC Authentication for Django REST Framework with JWT support",
    long_description="",
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
