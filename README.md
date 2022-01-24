# py-semsched
https://github.com/ramueller11/py-semsched

A simple implementation of a semantic interpreter of human readable schedule 
interval phrases. The phrases are interpreted into a simple 
date interval structure (DateIntervalSpecification) 
which can be used to generate the next and previous matches to the schedule
from a start or anchor date.

One possible use case of this project is to interpret a designated schedule.

Effectively, the specification defines the simple filters needed 
to  select matching days.

## Interval Syntax

A typical human specified schedule is modelled as having 3 parts:
    - day selectors 
    - month selectors
    - year selectors

The most natural way to describe a schedule is to order from 
day -> month -> year groups. This is the recommended order. 

For example: 
```
Mondays in Feb 2020
First Friday of Every Other Month
15th day of Feb 2021
15 - 20 of each month
```

The syntax for each group is as follows: 
`[modifiers] [arguments] [specifier]`

The actual words connecting specifiers and arguments are not really important, 
choose which ever makes sense to you. Any character that is not alphanumeric is ignored.
All matches are case-insensitive.

For example, `on every monday` and `every given monday` and `(EvErY single, monday)` are 
treated equivalently.

### Modifiers:
* `every` and aliases `each, all` convert numeric arguments to numeric arguments. 
  Without `every`, numeric arguments are treated as indices. For example: `every three days` 
  is an interval, `3rd day of the month` is an indice.
* `other` skips every other resulting days
* `odd` selects every odd resulting day
* `even` selects every even resulting day

### Arguments:
* Arguments are currently limited to numeric and numeric like arguments.
  Examples: `1st`,`second`, `third`, `25`, `25th`
* If two numerical arguments are present, it is assumed to be a min-max range.

Specifiers:
Specifiers describe sets or subsets of days, months and years. For example:
`Mondays` is a specifier of days which selects only mondays.

#### Day Specifiers
    `day`,`days` - all days
    `{day of week name,abbrev,letter}` - selects only that day of the week, ex. `F`,`Sat`,`Mondays`
    `{weekdays}` - selects all days, Monday - Friday inclusive. 
    `{weeks}`    - selects all days
    `{weekends}` - selects Saturday and Sunday inclusive.

#### Month Specifiers
    `month`,`months` - all months
    `{month, abbrev}` - selects only that month, ex. `Feb`,`January`

#### Year Specifiers
    `year`,`years`  - all years
    `{year number}` - specify the year, ex. `2022`

#### Query Recommendation
If you are looking for a little more structure, consider a SQL-like synatax notation:
`SELECT [day group] OF [month group] IN [year group];`

These become:
`SELECT first monday OF Feb IN 2022;`
`SELECT every workday OF * IN *;`

## DateIntervalSpecification Class
The date specification defined in the syntax above can be broken down into a 
handful of filter values that are specified in the DateIntervalSpecification
class. 

`day_mod`       - resulting day - modulus period filter
`day_mod_val`   - resulting day - modulus phase filter
`dow`           - day of week filter (0-6)
`dom`           - day of month filter (1-31)
`week_indx`     - week of month filter (0-5)
`month_mod`     - month - modulus period filter 
`month_mod_val` - month - modulus phase filter
`month_indx`    - month index filter (1-12)
`year_mod`      - year - modulus period filter 
`year_mod_val`  - year - modulus phase filter
`year_indx`     - year index filter

# Dependencies 
There are no other dependencies other than the python standard library.
It should work in both python 2.7 and python 3 environments.

# Tests 
To perform testing using `pytest` of the project in the local cloned directory, type:
```
pytest
```

Or equivalently, 
```
python -m pytest
```

# Installation
A setup.py file is defined for this project. 
In the cloned directory, type: 
```
pip install .
```
