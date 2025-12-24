#!/usr/bin/env python3

# Package metadata
__version__ = "1.0.0"
__author__ = "Hossein Fuller <hossfuller@protonmail.com>"
__description__ = "Hit By Pitches - Find's the MLB HBP events and posts them to Bluesky."

# Import key components to make them available at package level
from .libhbp import constants
from .libhbp import func_general
from .libhbp import func_baseball
from .libhbp import func_skeet

# Package-level variables
__all__ = [
    'constants',
    'func_general',
    'func_baseball',
    'func_skeet',
]
