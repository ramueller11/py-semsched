import pytest, sys, os
import datetime

# include ../src in the path search
mypath = os.path.dirname( os.path.realpath(__file__) )
sys.path.insert(0, os.path.join( os.path.dirname(mypath), 'src' ) )

import semsched as lib

def test_overall():
    f = lib.DateIntervalSpec.from_phrase

    # try with nothing specified
    phrase = ''
    s = f(phrase); s.start_date = datetime.date(2022,1,1)

    assert ( s.day_mod == None and s.day_mod_val == 0 and s.dow == None and s.dom == None 
             and s.week_indx == None and s.month_mod == None and s.month_mod_val == 0 and s.month_indx == None
             and s.year_mod == None and s.year_mod_val == 0 and s.year_indx == None )

    assert( s.next() == datetime.date(2022,1,2) )
    assert( s.previous() == datetime.date(2021,12,31) )

    # try every day
    phrase = 'every day'
    s = f(phrase); s.start_date = datetime.date(2022,1,1)

    assert ( s.day_mod == 1 and s.day_mod_val == 0 and s.dow == None and s.dom == None 
             and s.week_indx == None and s.month_mod == None and s.month_mod_val == 0 and s.month_indx == None
             and s.year_mod == None and s.year_mod_val == 0 and s.year_indx == None )

    assert( s.next() == datetime.date(2022,1,2) )
    assert( s.previous() == datetime.date(2021,12,31) )

    # try every other day
    phrase = 'every other day'
    s = f(phrase); s.start_date = datetime.date(2022,1,1)

    assert ( s.day_mod == 2 and s.day_mod_val == 0 and s.dow == None and s.dom == None 
             and s.week_indx == None and s.month_mod == None and s.month_mod_val == 0 and s.month_indx == None
             and s.year_mod == None and s.year_mod_val == 0 and s.year_indx == None )
    assert( s.next() == datetime.date(2022,1,3) )
    assert( s.previous() == datetime.date(2021,12,30) )

    # try every third day
    phrase = 'every third day'
    s = f(phrase); s.start_date = datetime.date(2022,1,1)

    assert ( s.day_mod == 3 and s.day_mod_val == 0 and s.dow == None and s.dom == None 
             and s.week_indx == None and s.month_mod == None and s.month_mod_val == 0 and s.month_indx == None
             and s.year_mod == None and s.year_mod_val == 0 and s.year_indx == None )
    assert( s.next() == datetime.date(2022,1,4) )
    assert( s.previous() == datetime.date(2021,12,29) )

    # try 1st day
    phrase = '1st day'
    s = f(phrase); s.start_date = datetime.date(2022,1,1)

    assert ( s.day_mod == None and s.day_mod_val == 0 and s.dow == None and s.dom == {1} 
             and s.week_indx == None and s.month_mod == None and s.month_mod_val == 0 and s.month_indx == None
             and s.year_mod == None and s.year_mod_val == 0 and s.year_indx == None )
    assert( s.next() == datetime.date(2022,2,1) )
    assert( s.previous() == datetime.date(2021,12,1) )

    # do we recover the correct next point?
    s.start_date = s.previous()
    assert( s.next() == datetime.date(2022,1,1) )
    s.start_date = s.next()
    assert( s.next() == datetime.date(2022,2,1) )

    # try odd days 
    phrase = 'every odd days'
    s = f(phrase); s.start_date = datetime.date(2022,1,1)

    assert ( s.day_mod == 2 and s.day_mod_val == 1 and s.dow == None and s.dom == None
             and s.week_indx == None and s.month_mod == None and s.month_mod_val == 0 and s.month_indx == None
             and s.year_mod == None and s.year_mod_val == 0 and s.year_indx == None )
    
    assert( s.next() == datetime.date(2022,1,2) )
    assert( s.previous() == datetime.date(2021,12,31) )

    days_p = s.next_occurances()
    days_m = s.previous_occurances()

    assert( len(days_p) == len(days_m) == 10 )

    assert( days_p[0] == s.next() )
    assert( days_m[0] == s.previous() )

    for i in range(9):
        assert( (days_p[i+1] - days_p[i]).days == 2 )
        assert( (days_m[i] - days_m[i+1]).days == 2 )    

    # try even days 
    phrase = 'every even days'
    s = f(phrase); s.start_date = datetime.date(2022,1,1)

    assert ( s.day_mod == 2 and s.day_mod_val == 0 and s.dow == None and s.dom == None
             and s.week_indx == None and s.month_mod == None and s.month_mod_val == 0 and s.month_indx == None
             and s.year_mod == None and s.year_mod_val == 0 and s.year_indx == None )

    assert( s.next() == datetime.date(2022,1,3) )
    assert( s.previous() == datetime.date(2021,12,30) )

    days_p = s.next_occurances()
    days_m = s.previous_occurances()

    assert( len(days_p) == len(days_m) == 10 )

    assert( days_p[0] == s.next() )
    assert( days_m[0] == s.previous() )

    for i in range(9):
        assert( (days_p[i+1] - days_p[i]).days == 2 )
        assert( (days_m[i] - days_m[i+1]).days == 2 )   