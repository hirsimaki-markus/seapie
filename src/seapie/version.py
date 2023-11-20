#!/usr/bin/env python3

"""Updating __version__ information:
    * Format is <major>.<minor>.<patch>
    * Never use leading or trailing zeroes in any of major/minor/patch.
    * A lone zero is allowed.
    * Increment more if an increment results in a leading or trailing zero.
    * Incrementing major resets minor and patch to 0.
    * Incrementing minor resets patch to 0.
    * Incrementing patch does not affect other numbers.
    * Never decrement a number except when resetting to zero like above.


    version has been placed in separate file to avoid circular dependencies.
"""

__version__ = "3.0.0"
