"""
dintspec.py
Defines the DateIntervalSpec class definition.
"""

import datetime
from .parsing import parse as _parse

# -------------------------------------------

class DateIntervalSpec():
    """
    Date interval specification, representation of all required 
    modulus period, modules phases and indices for days, months
    and years needed to construct a date interval.

    This is a state that is parsed from a semantic date interval.

    For example: 
        "every day" --> day modulus period of 1, phase = 0
        "every other day" --> day modulus period of 2, phase = 0
        "every odd day" --> day modulus period of 2, phase = 0

    """
    def __init__(self, phrase=None):
        self.day_mod          = None  # resulting day - modulus period filter
        self.day_mod_val      = 0     # resulting day - modulus phase filter
        self.dow              = None  # day of week filter (0-6)
        self.dom              = None  # day of month filter (1-31)
        self.week_indx        = None  # week of month filter (0-5)
        self.month_mod        = None  # month - modulus period filter 
        self.month_mod_val    = 0     # month - modulus phase filter
        self.month_indx       = None  # month index filter (1-12)
        self.year_mod         = None  # year - modulus period filter 
        self.year_mod_val     = 0     # year - modulus phase filter
        self.year_indx        = None  # year index filter
        self.start_date       = datetime.date.today()   # effective start date of interval
        self.phrase           = ""
        
        if phrase != None:
            self.phrase = phrase
        
        _parse(self, phrase)
        
    @classmethod
    def from_phrase(cls, phrase):
        self = cls(phrase)
        return self
    
    # ---------------------------

    def previous(self, start_date=None, end_date=None):
        """
        Obtain the previous occurance in the given date range.

        Parameters: 
            start_date - the starting date range, all days prior are ignored.
            end_date   - the ending date range, all days after are ignored.

        Return:
            the previous occurance in the given range or None if one didn't occur in the range.

        Note: 
            This is equivalent to running .previous_occurances with a max_result of 1
        """

        result_ar = self.previous_occurances(start_date=start_date, end_date=end_date, max_results=1)
        if len(result_ar) > 0:
            return result_ar[0]
        else:
            return None
    
    # ---------------------------

    def previous_occurances(self, start_date=None, end_date=None, max_results=10):
        """
        Obtain the previous occurances that occur in the given date range.

        Parameters: 
            start_date  - the starting date range, all days prior are ignored.
            end_date    - the ending date range, all days after are ignored.
            max_results - limit to number of results to find
        
        Return:
            a list of previous occurances in the given range.

        Note: 
            This function essentially runs the next() method while iterating 
            backwards in time. The modulus may not work perfectly here.
        """

        if end_date == None:
            end_date = min( datetime.date.today(), self.start_date )
        if start_date == None: start_date = datetime.date(2,1,1)

        curdate = end_date

        # narrow the search range
        if self.year_indx != None:
            _chk_min = datetime.date(min(self.year_indx), 1, 1)
            _chk_min = _chk_min - datetime.timedelta(days=1)
            _chk_max = datetime.date(max(self.year_indx), 12, 31)

            # check if this happened in the future
            if _chk_min > end_date: return []
            
            # we can skip ahead to the specified year
            if curdate > _chk_max:
                curdate = _chk_max

            if start_date < _chk_min:
                start_date = _chk_min
        
        # initialize the loop
        result_cnt = 0
        results = []

        end_date = curdate - datetime.timedelta(days=1)
        curdate = curdate - datetime.timedelta(days=1)
        
        # we temporary disable the day modulus filter so we can
        # filter on this end. The math appears to be slightly off going
        # backwards.
        _d_mod = self.day_mod; self.day_mod = None

        while len(results) < max_results:
            curdate = curdate - datetime.timedelta(days=1)

            if curdate < start_date: break
            prevday = self.next(start_date=curdate, end_date=end_date)
            if prevday == None: continue
            end_date = prevday - datetime.timedelta(days=1)

            result_cnt += 1

            # day_mod is modulated on the resulting days
            if _d_mod != None:
                if self.dow == None:
                    # no specific day
                    if (result_cnt) % _d_mod != self.day_mod_val:
                        continue
                elif self.dow == {0,1,2,3,4,}:
                    # weekday case
                    if (result_cnt) % _d_mod != self.day_mod_val:
                        continue  
                else:
                    # week / weekend
                    repeat = int( (result_cnt - 1) / len(self.dow) )
                    if (repeat + 1) % _d_mod != self.day_mod_val:
                        continue
            
            results.append(prevday)

        # restore day_mod value
        self.day_mod = _d_mod

        return results

    # ----------------------------------------------------------------------
    
    def next(self, start_date=None, end_date=None):
        """
        Obtain the next occurance in the given date range.

        Parameters: 
            start_date - the starting date range, all days prior are ignored.
            end_date   - the ending date range, all days after are ignored.

        Return:
            the next occurance in the given range or None if one didn't occur in the range.

        Note: 
            This is equivalent to running .next_occurances with a max_result of 1
        """

        result_ar = self.next_occurances(start_date=start_date, end_date=end_date, max_results=1)
        if len(result_ar) > 0:
            return result_ar[0]
        else:
            return None
    
    # ---------------------------

    def next_occurances(self, start_date=None, end_date=None, max_results=10):
        """
        Obtain the next occurances that occur in the given date range.

        Parameters: 
            start_date  - the starting date range, all days prior are ignored.
            end_date    - the ending date range, all days after are ignored.
            max_results - limit to number of results to find
        
        Return:
            a list of next occurances in the given range.
        """

        if end_date == None: end_date = datetime.date(9999,1,1)
        if start_date == None: start_date = self.start_date

        # narrow the search range
        if self.year_indx != None:
            _chk_min = datetime.date(min(self.year_indx), self.month_indx if self.month_indx != None else 1, 1)
            _chk_min = _chk_min - datetime.timedelta(days=1)
            _chk_max = datetime.date(max(self.year_indx), 12, 31)

            # check if this happened in the past
            if start_date > _chk_max: return []
                
            # we can skip ahead to the specified month, year
            if start_date < _chk_min:
                start_date = _chk_min
            
            if end_date > _chk_max:
                end_date = _chk_max
        
        # initialize the loop
        curdate = start_date
        result_cnt = 0
        result = []

        # main iteration
        while ( len(result) < max_results ):
            # always add a day
            curdate = curdate + datetime.timedelta(days=1)
            if curdate > end_date: break
            week = int( (curdate.day - 1) / 7 )

            # year filtering
            if self.year_indx != None:
                if curdate.year > max(self.year_indx):
                    break
                if not curdate.year in self.year_indx: continue
            
            if self.year_mod != None:
                if (curdate.year % self.year_mod ) != self.year_mod_val: continue
            
            # month filtering
            if self.month_indx != None:
                if curdate.month != self.month_indx: continue

            if self.month_mod != None:
                if (curdate.month % self.month_mod) != self.month_mod_val: continue
            
            # day filtering
            if self.dow != None:
                if not curdate.weekday() in self.dow: continue
            
            if self.dom != None:
                if not curdate.day in self.dom: continue
            
            if self.week_indx != None:
                if week != self.week_indx: continue
            
            # we matched! 
            result_cnt += 1
            
            # day_mod is a modulated on the resulting days
            if self.day_mod != None:
                if self.dow == None:
                    # no specific day
                    if (result_cnt) % self.day_mod != self.day_mod_val:
                        continue
                elif self.dow == {0,1,2,3,4,}:
                    # weekday case
                    if (result_cnt - 1) % self.day_mod != self.day_mod_val:
                        continue       
                else:
                    # week / weekend
                    repeat = int( (result_cnt - 1) / len(self.dow) )
                    if repeat % self.day_mod != self.day_mod_val:
                        continue
                    # ignore the first match
                    if repeat < 1 and self.day_mod > 1: continue  
            
            result.append(curdate)
            #print(result_cnt, week, curdate)

        return result

    # -------------------------------------------------