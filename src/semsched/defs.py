"""
defs.py

Defintions used for parsing and related helper functions.
"""

import re

# define the modifiers which act on a given schedule group
# map keywords to alias sets
_modifiers = {
    'every': {'every', 'each', 'all'},  # recurring
    'other': {'other',},                # "every other" (second, 2nd...) are already interpreted
    'odd':  {'odd'},                    # every odd instance 
    'even': {'even'},                   # every even instance
    'next': {'next'},
}

# define day specifications
_days = {
    'day':   {'day','daily'},
    'weekday': {'weekday'},
    'weekend': {'weekend'},
    'week':   {'week'},
    'mon':   {'m', 'mon', 'monday'},
    'tue':   {'t', 'tue', 'tues', 'tuesday'},
    'wed':   {'w', 'wed', 'weds', 'wednesday', },
    'thu':   {'r', 'thu', 'thurs', 'thursday' },
    'fri':   {'f', 'fri', 'friday', },
    'sat':   {'s', 'sa', 'sat', 'saturday', },
    'sun':   {'u', 'su', 'sun', 'sunday', },   
}

# define month specifications
_months = {
    'month': {'month','monthly'}, 
    'jan': {'jan', 'january' },
    'feb': {'feb', 'febuary' },
    'mar': {'mar', 'march'},
    'apr': {'apr', 'april'},
    'may': {'may'},
    'jun': {'jun'},
    'jul': {'jul','july'},
    'aug': {'aug','august'},
    'sep': {'sep','sept','september'},
    'oct': {'oct','october'},
    'nov': {'nov','november'},
    'dec': {'dec','december'},
}

# --------------------------------------------------------------

def _make_pattern(d, exact_match=True, plurals=2):
    """
    Internal function.
    Generates a compiled regex pattern based on a given alias array.
    
    Parameters:
        d - the alias map/dict to compile into a regex pattern
        exact_match - compile with pattern starting and ending anchors
        plurals     - If > 0, add 's' aliases to members greater than this value.
    
    Return:
        Compiled regex pattern.
    """

    entries = []
    [ entries.extend([y for y in x]) for x in d.values() ]
    
    
    if plurals > 0:
        entries = [ ( x + '[s]?' if len(x) > plurals else x ) for x in entries ]
        
    if exact_match:
        return re.compile('^(' + '|'.join(entries) + ')$', re.I)
    else:
        return re.compile('(' + '|'.join(entries) + ')', re.I)


# --------------------------------------------------------------

def _spec_alias_lookup( defs, alias):
    """
    Internal function.
    This is a helper function that reverse looks up an alias 
    value in a given definition map to obtain the standardized
    key.

    Parameters:
        defs   - key --> alias map to lookup with 
        alias  - alias to lookup (str)

    Return:
        Return the matching key if known. 
        Returns None if it doesn't exist in the alias map.
    """

    if not isinstance(alias, type(u'a')): return None
    alias = alias.lower()
    
    for k, curset in defs.items():
        # exact match
        if alias in curset:
            return k
        # try the pluralized version
        if alias.rstrip('s') in curset:
            return k
    
    return None

# --------------------------------------------------------------