"""
numwords.py 
https://github.com/ramueller11/py-numwords

Interconvert English words with whole numbers.

Example: 
    int2words('555') = 'five hundred fifty five'
    words2int('one') = 1
    words2int('first') = 1 
    words2int('a hundred') = 100
    words2int('none') = 0
    words2int('negative ten') = -10
"""

import math

# word bank --> convert words to a numeric value (pre-compiled result of _generate_wordbank() )
# otherwise, set this value to None and it will be generated on the first run of words2int
_wordbank = {
"none": 0, "nill": 0, "nothing": 0, "zeroth": 0, "hundred": 100, "a": 1,
"first": 1, "second": 2, "third": 3, "hundredth": 100, "negative": -1, 
"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, 
"seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, 
"thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, 
"eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "fourty": 40, 
"fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "thousand": 1000, 
"million": 1000000, "billion": 1000000000, "trillion": 1000000000000, "quadrillion": 1000000000000000, 
"quintillion": 1000000000000000000, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, 
"ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14, 
"fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eightteenth": 18, "nineteenth": 19, "twentieth": 20, 
"thirtieth": 30, "fourtieth": 40, "fiftieth": 50, "sixtieth": 60, "seventieth": 70, "eightieth": 80, "ninetieth": 90, 
"thousandth": 1000, "millionth": 1000000, "billionth": 1000000000, "trillionth": 1000000000000, 
"quadrillionth": 1000000000000000, "quintillionth": 1000000000000000000
}

# digits
_digits   = {
    0: 'zero', 1: 'one',   2: 'two',   3: 'three', 4: 'four', 5: 'five',
    6: 'six',  7: 'seven', 8: 'eight', 9: 'nine'
}

# powers of 1000
_pow1000 = {
    0:  '', 1:  'thousand',  2:  'million', 3:  'billion', 4: 'trillion', 
    5: 'quadrillion', 6: 'quintillion',  7:  'sexillion', 8: 'septillion', 
    9: 'octillion',  10: 'nonillion', 11:'decillion'
}

def _generate_wordbank():
    """
    Internal function.
    Generates a word bank from scratch.
    """

    wordbank = {
        'none': 0, 'nill': 0, 'nothing': 0, 'zeroth':0,
        'hundred': 0, 'first': 1, 'second': 2, 'third': 3,
        'hundredth': 100, 'negative': -1,
    }

    wordbank.update({ _convert_hundreds(i):i for i in range(20) })
    wordbank.update({ _convert_hundreds(i*10):10*i for i in range(2,10) })
    wordbank['hundred'] = 100
    wordbank.update({ int2words(1000**i).split(' ')[-1] : 1000 ** i for i in range(1,7) })
    
    # generate ordinals
    wordbank.update({

    })

    for x in range(4,20):
        k = _convert_hundreds(x).rstrip('et').replace('iv','if').replace('lv','lf') + 'th'
        wordbank[k] = x
    
    for x in range(2,10):
        k = _convert_hundreds(10*x).rstrip('y') + 'ieth'
        wordbank[k] = 10 * x

    for x in range(1,7):
        k = int2words(1000**x).split(' ')[-1] + 'th'
        wordbank[k] = 1000**x

    return wordbank

# -----------------------------------------

def _convert_hundreds( val ):
    """
    Internal function, converts a nominal value between 0 - 999.
    This is grouped together by orders of thousands in the int2words.

    Parameters:
        val - numeric value to convert

    Notes:
        Refers to the module global value _digits.
    """

    global _digits

    if val < -999 or val > 999:
        raise ValueError('Value should be within -999 to 999')
    
    if val == 0: 
        return 'zero'
    
    h = int( val / 100 )
    t = int( ( val % 100 ) / 10 )
    o = ( val % 10 )

    result = ['','','']

    if h > 0:
        result[0] = _digits[h] + ' hundred'

    if t == 1:
        if o > 2:
            result[1] = _digits[o].rstrip('t').replace('ree','ir').replace('ive','if') 
            result[1] += 'teen'
        elif o == 2: 
            result[1] = 'twelve'
        elif o == 1: 
            result[1] = 'eleven'
        elif o == 0: 
            result[1] = 'ten'
        o = 0
    elif t > 1:
        result[1] = _digits[t].rstrip('t').replace('ree','ir').replace('ive','if').replace('wo','wen') 
        result[1] += 'ty'
    
    if o > 0:
        result[2] = _digits[o]

    result = ' '.join([ x for x in result if len(x) > 0 ]).strip()
    if val < 0: result = 'negative ' + result

    return result

# --------------------------

def int2words(val):
    """
    Obtain the written representation of the given value.

    Parameters:
        val - the number to convert ( will be converted to an integer )

    Notes:
        References the _pow1000 global variable for names of powers of 1000.
    """

    global _pow1000
    if ( abs(val) > 184e17 ): raise ValueError('Value is larger than can be represented by a 64 bit integer.')

    # a 64 bit integer (long long) can hold only 1.84e19 ~ 18 * 1000 ^ 6
    # above around 1e22, the precision doesn't really work correctly

    if val == 0: return 'zero'

    groups = max( int( math.log(abs(val)) / math.log(1000) ), 0 )

    result = []

    for g in range(groups,-1,-1):
        curpow   = 1000 ** g
        curGroup = int( ( abs(val) % (1000 * curpow) ) / curpow )

        if curGroup == 0: continue
        result.append( _convert_hundreds(curGroup) + ' ' + _pow1000[g] )

    result = ', '.join(result)
    if val < 0: result = 'negative ' + result

    return result.strip()
   
# ----------------------------

def words2int(val):
    """
    Convert a written representation of the given value to an integer.

    Parameters:
        val - the written representation of the value

    Notes:
        References the _wordbank global variable for names of powers of 1000.
    """

    global _wordbank
    if _wordbank == None: _wordbank = _generate_wordbank()
    
    # try a naive conversion first
    try:
        return( float(val) )
    except:
        pass
    
    try:
        return( float(val.replace(',','').replace(' ','')) )
    except:
        pass
    
    # split into phrases -> convert all delimiters to ' '
    val = val.replace(',',' ').replace('-', ' ')
    phrases = [ x.strip() for x in val.split(' ') if len(x.strip()) > 0 ]

    # intialize state
    result = 0; mantissa  = 0; sign   = 1

    for p in phrases:
        p_alpha   = ''.join([ c for c in p if c not in '0123456789' ]).lower().strip()
        p_numeric = ''.join([ c for c in p if c in '0123456789'])

        if p_alpha in {'and',}: continue

        # process current phrase        
        if p in _wordbank:
            # known phrase
            pn = _wordbank[p]
        elif len(p_alpha) < 1:
            # is a numeric phrase
            pn = int(p_numeric)
        elif p_alpha == '-':
            pn = -1 * int(p_numeric)
        elif len(p_numeric) > 0 and p_alpha in {'nd','rd','st','th'}:
            # is an ordinal phrase
            pn = int(p_numeric)
        else:
            raise ValueError('Unable to interpret phrase "%s".' % p)
        
        # is a synonmyn of negative
        if pn < 0: 
            sign = -1
            continue
        elif pn > 99:
            # we hit a "power" of ten phrase (e.g. hundred, thousand, million)
            if mantissa != 0:
                mantissa = mantissa * pn
            else:
                mantissa = pn
            
            # reset the mantissa for groupings of thousand
            if pn > 999: 
                result += mantissa
                mantissa = 0
        else:
            # we have a normal digit
            mantissa += pn
    
    # add the remaining mantissa and multiply by the sign
    result += mantissa
    result = result * sign

    return result

# -----------------------------------
