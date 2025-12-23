#!/usr/bin/env python3

# Package metadata
__version__ = "1.0.0"
__author__ = "Hossein Fuller <hossfuller@protonmail.com>"
__description__ = "Hit By Pitches - Find's the MLB HBP events and posts them to Bluesky."

# Import key components to make them available at package level
from . import constants
from . import functions

# Package-level variables
__all__ = [
    'constants',
    'functions'
]
