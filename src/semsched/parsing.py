"""
parse.py

Implementation of semantic parser of date phrases.
"""

import re, datetime
from . import numwords
from .defs import _modifiers, _days, _months, _make_pattern, _spec_alias_lookup

# this holds a cached version of the regex representation of regex patterns 
# for semantic parsing
_pattn = None

# -------------------------------------------------

def _parse_groups( phrase ):
    """
    Internal function.
    Filter and segment an input phrase into day, month, year groups for further processing. 

    Input: 
        phrase - the phrase to process.
    
    Return:
        A dictionary of grouped data with keys 'year', 'month', 'day'. Values are 
        2-tuples - ( specifier [str], args ). Where the specifier are defined in the 
        alias maps above in _months, _days and args are relevant parameters associated
        with each grouping.
    
    Notes: 
        This references _days, _months, _modifiers, _pattn private arrays above.
    """
    global _days, _months, _modifiers, _pattn
    
    # compile regex patterns (as needed)
    if _pattn == None:
        _pattn = {}
        _pattn['sep']   = re.compile('((for|of|in|to)[ ]*(the|a)?|to|for|of|in|[ ])', re.I)
        _pattn['year']  = re.compile('(year[s]?|[0-9][0-9][0-9][0-9])', re.I)
        _pattn['day']   = _make_pattern(_days, exact_match=True, plurals=2)
        _pattn['month'] = _make_pattern(_months, exact_match=True, plurals=3)
        _pattn['mods']  = _make_pattern(_modifiers, exact_match=True, plurals=0)
    
    # pre-process, remove non-alphanumeric characters
    phrase = phrase.replace(',',' ').replace('-',' ').replace('\t',' ')
    allow_characters = '0123456789abcdefghijklmnopqmnopqrstuvwxyz '
    phrase = ''.join([ c for c in phrase if c.lower() in allow_characters ])
    parts = [ x for x in _pattn['sep'].sub('|', phrase).split('|') if len(x.strip()) > 0 ]

    parsed = {'other':[]}
    args = []

    for p in parts:
        # see if the current part is a modifier
        if _pattn['mods'].match(p):
            args.append(p)
            continue

        # see if the current part is numeric 
        # of can be interpreted as numeric
        try:
            val = numwords.words2int(p)
            args.append(val)
            continue
        except:
            pass

        matched = False
        
        # iterate over groups
        for k in ('year','month','day',):
            if _pattn[k].match(p):
                parsed[k] = (p,args)
                args = []
                matched = True
                break
        
        # we found an unknown part
        if matched == False:
            parsed['other'].append((p,[]))

    # ---------------- end of part decoding loop

    # in the current implemenation, a year value 
    # maybe sitting in the remaining arguments
    for x in args:
        if not isinstance(x,(int,float)): continue
        if x < 100: continue

        if 'year' in parsed:
            parsed['year'][1].append(x)
        else:
            parsed['year'] = ('%i' % x, [x])
                
    return parsed

# ---------------------------------------------------

def _get_day_config( spec=None, args=[] ):
    """
    Internal function. 
    This decodes the parsed 'day' group into the corresponding 
    day filtering configuration.

    Parameters:
        spec - the day specification alias (default=None)
        args - a list/tuple of arguments associated with the day specification (default=[])

    Return:
        Returns a 5-tuple with the following components:
            0 - modulus period   (int or None)
            1 - modulus phase    (int)
            2 - day of the week  (set or None)
            3 - day of the month (set or None)
            4 - week index       (int or None)
    
    Notes: 
        * This function references internal variables _modifiers and _days.
        * This is the most complicated of the configuration decoders.

    Example:
        The parsed phrase 'every day' could be represented as:

        spec='day'  args=['every']
        This is converted by the function to:
            1, 0, None, None, None
    """
    global _modifiers, _days
    
    # default values (every day)
    # value of None is an internally coded default - no filtering
    mod      = None         # result modulus period
    mod_val  = 0            # result modulus phase
    dow      = None         # day of the week
    dom      = None         # day of the month 
    week     = None         # week index
    
    # decode the specification and arguments
    spec = _spec_alias_lookup( _days, spec )
    
    kwargs = set( _spec_alias_lookup( _modifiers, x ) for x in args )
    kwargs = { x for x in kwargs if x != None }
    intargs = [ int(x) for x in args if isinstance(x,(int,float)) ]

    #print('Parsed Day:')
    #print('  spec', spec)
    #print('  kwargs: ', kwargs)
    #print('  intargs: ', intargs)
    
    # decode the specification
    if   spec == 'mon': dow = {0}
    elif spec == 'tue': dow = {1}
    elif spec == 'wed': dow = {2}
    elif spec == 'thu': dow = {3} 
    elif spec == 'fri': dow = {4} 
    elif spec == 'sat': dow = {5}
    elif spec == 'sun': dow = {6}
    elif spec == 'weekday': dow = {0,1,2,3,4}
    elif spec == 'weekend': dow = {5,6}
    elif spec == 'week': dow = {0,1,2,3,4,5,6}
    elif spec == 'day': dow = None
    elif spec == None: pass
    else:
        raise NotImplementedError('Unknown day specifier "%s".' % spec)
    
    # decode the kw arguments
    if 'every' in kwargs:
        mod = 1  
    if 'odd' in kwargs: 
        mod_val = 1
        mod = 2
    if 'even' in kwargs: 
        mod_val = 0
        mod = 2  
    if 'other' in kwargs: 
        mod = 2
    
    # decode the integer arguments
    # here context matters! 
    if len(intargs) > 0:
        val = intargs[0]
        if 'every' in kwargs:
            # every second, every third, every 10...
            # this means that we have a interval defined --> result mod
            if val < 1:
                raise ValueError('Specified interval is smaller than a day: %i' % val)
            mod = intargs[0]
        elif spec == 'day':
            # 15th day of the month for example --> this is a day of month
            if val < 1 or val > 31:
                raise ValueError('Incorrect day of month specification: %i' % val)
                
            if len(intargs) < 2:
                # single day was specified
                dom = {val}
            else:
                # range was specified
                _minval = max(1, min(intargs))
                _maxval = min( max(intargs), 31)
                dom = { x for x in range(_minval,_maxval + 1) }
        
        elif spec == 'weekday':
            # this is a special case of the below case
            # first weekday, 15th weekday
            if val < 1 or val > 22:
                raise ValueError('Incorrect weekday index specification: %i' % val)
                
            mod = 5  # the weekday selector should provide 5 matches
            mod_val = ( val - 1 ) % 5
            week = int( (val - 1) / 5 )
        else:
            # not day or weekday (no every modifer)
            # first saturday, 2nd friday.. --> this is a week index
            if val < 1 or val > 5:
                raise ValueError('Incorrect week index specification: %i' % val)
            week = val - 1
    
    return (mod, mod_val, dow, dom, week)

# ----------------------------------------------------------

def _get_month_config( spec=None, args=[] ):
    """
    Internal function. 
    This decodes the parsed 'month' group into the corresponding 
    month filtering configuration.

    Parameters:
        spec - the month specification alias (default=None)
        args - a list/tuple of arguments associated with the month specification (default=[])

    Return:
        Returns a 4-tuple with the following components:
            0 - modulus period   (int or None)
            1 - modulus phase    (int)
            2 - month index      (int or None)
            3 - day of the month (set or None)
    
    Notes: 
        * This function references internal variables _modifiers and _months.
        * The day of month maybe grouped with month if the day group isn't provided.
            ex: '25th day of Feb' will produce
                spec = 'feb', args = []
            ex: '25th of Feb' will produce
                spec = 'feb,  args=[25.0]
    """
    global modifiers, months
    
    # default values (every day)
    mod      = None         # result modulus
    mod_val  = 0            # result modulus value 
    indx     = None         # month ndex
    dom      = None         # day of the month
      
    # decode the specification and arguments
    spec = _spec_alias_lookup( _months, spec )
    
    kwargs = set( _spec_alias_lookup( _modifiers, x ) for x in args )
    kwargs = { x for x in kwargs if x != None }
    intargs = [ int(x) for x in args if isinstance(x,(int,float)) ]
    
    #print('Parsed Month:')
    #print('  spec', spec)
    #print('  kwargs: ', kwargs)
    #print('  intargs: ', intargs)
    
    # decode the specification
    if   spec == 'jan': indx = 1
    elif spec == 'feb': indx = 2
    elif spec == 'mar': indx = 3
    elif spec == 'apr': indx = 4 
    elif spec == 'may': indx = 5 
    elif spec == 'jun': indx = 6
    elif spec == 'jul': indx = 7
    elif spec == 'aug': indx = 8
    elif spec == 'sep': indx = 9
    elif spec == 'oct': indx = 10
    elif spec == 'nov': indx = 11
    elif spec == 'dec': indx = 12
    elif spec == 'month': indx = None
    elif spec == None: pass
    else:
        raise NotImplementedError('Unknown month specifier "%s".' % spec)
    
    # decode the kw arguments
    if 'every' in kwargs:
        mod = 1  
    if 'odd' in kwargs: 
        mod_val = 1
        mod = 2
    if 'even' in kwargs: 
        mod_val = 0
        mod = 2  
    if 'other' in kwargs: 
        mod = 2

    # decode the integer arguments
    if len(intargs) > 0:
        val = intargs[0]
        if 'every' in kwargs:
            # every second, every third, every 10...
            # this means that we have a interval defined --> result mod
            if val < 1:
                raise ValueError('Specified interval is smaller than a month: %i' % val)
            mod = val
        elif val < 32 and spec != 'month':
            # a day of a specific month was specified
            if len(intargs) < 2:
                # single day was specified
                dom = {val}
            else:
                # range was specified
                _minval = max(1, min(intargs))
                _maxval = min( max(intargs), 31)
                dom = { x for x in range(_minval, _maxval + 1) }
        else:
            raise ValueError('Unknown index or interval given: %i' % val)
    
    return (mod, mod_val, indx, dom)

# --------------------------------------------------

def _get_year_config( spec=None, args=[] ):
    """
    Internal function. 
    This decodes the parsed 'year' group into the corresponding 
    year filtering configuration.

    Parameters:
        spec - the year specification alias (default=None)
        args - a list/tuple of arguments associated with the year specification (default=[])

    Return:
        Returns a 3-tuple with the following components:
            0 - modulus period   (int or None)
            1 - modulus phase    (int)
            2 - year indices     (set or None)
    
    Notes: 
        * This function references internal variables _modifiers.
    """

    global _modifiers
    
    # default values (every day)
    mod      = None         # result modulus
    mod_val  = 0            # result modulus value 
    indx     = None         # month ndex
      
    # decode the specification and arguments   
    kwargs = set( _spec_alias_lookup( _modifiers, x ) for x in args )
    kwargs = { x for x in kwargs if x != None }
    intargs = [ int(x) for x in args if isinstance(x,(int,float)) ]
    
    #print('Parsed Year:')
    #print('  kwargs: ', kwargs)
    #print('  intargs: ', intargs)
            
    # decode the kw arguments
    if 'every' in kwargs:
        mod = 1  
    if 'odd' in kwargs: 
        mod_val = 1
        mod = 2
    if 'even' in kwargs: 
        mod_val = 0
        mod = 2  
    if 'other' in kwargs: 
        mod = 2
    
    # specific year(s) were specified
    if len(intargs) == 1:
        val = intargs[0]
        
        if 'every' in kwargs:
            # interval was specified
            if val < 1:
                raise ValueError('Specified year interval is zero or negative.')
            mod = val
        else:
            # single year index was specified
            indx = {val}
        
    elif len(intargs) > 1:
        # a range was specified
        _minval = min(intargs)
        _maxval = max(intargs)
        indx = { x for x in range(_minval, _maxval + 1) }
    else:
        # no specific years are specified.
        pass
    
    return (mod, mod_val, indx)

# ----------------------------------------------------------

def parse( dint, phrase ):
    """
    Parse a scheduling phrase into a DateIntervalSpec class which represents the 
    equivalent date filtering configuration.

    Parameters:
        dint   - result class instance to populate, compatible with DateIntervalSpec
        phrase - human readable phrase to parse
    
    Return: 
        A reference of the instance representing the specific date filtering configuration.
    """

    fmt = ( '%Y%M%d', '%d%b%Y', '%Y-%M', '%b%Y', '%d%b' )
    phrase2 = phrase.replace('-','').replace(' ','')
    for f in fmt:
        try:
            val = datetime.datetime.strptime(phrase2, f).date()
            if '%Y' in f:
                dint.year_indx = {val.year}

            dint.month_indx = val.month
            
            if '%d' in f:
                dint.dom = {val.day}
            return dint
        except Exception:
            pass

    # parse the input phrase into it's component groups
    groups = _parse_groups(phrase)   

    # obtain the day config
    _spec, _args = groups.get('day', (None,[]))
    dint.day_mod, dint.day_mod_val, dint.dow, dint.dom, dint.week_indx = _get_day_config(_spec, _args)

    # obtain the month config
    _spec, _args = groups.get('month', (None,[]))
    dint.month_mod, dint.month_mod_val, dint.month_indx, _m_dom  = _get_month_config(_spec, _args)

    # obtain the year config
    _spec, _args = groups.get('year', (None,[]))
    dint.year_mod, dint.year_mod_val, dint.year_indx = _get_year_config(_spec, _args)

    # re-concile dom from month if not in day args
    if dint.dom == None: dint.dom = _m_dom

    # re-concile year_mod from month if mon_indx != None
    # example: every other Feb
    if dint.month_mod != None and dint.month_indx != None:
        if dint.year_mod == None:
            dint.year_mod = dint.month_mod
            dint.year_mod_val = dint.month_mod_val
            dint.month_mod = None
            dint.month_mod_val = 0
        else:
            # this is an error 
            raise RuntimeError('Ambigious year and month keywords!')

    return dint

# ----------------------------