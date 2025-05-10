"""
KappaML - A Python client to interact with the KappaML platform.
"""

from .kappaml import (
    KappaML,
    KappaMLError,
    ModelNotFoundError,
    ModelDeploymentError
)

__all__ = [
    "KappaML", 
    "KappaMLError", 
    "ModelNotFoundError", 
    "ModelDeploymentError"
]

__author__ = "Alex Imbrea" 
