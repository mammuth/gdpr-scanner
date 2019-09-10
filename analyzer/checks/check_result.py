from collections import namedtuple

CheckResult = namedtuple('CheckResult', 'passed identifier severity')  # passed means everything is fine, the Check did not fail.
