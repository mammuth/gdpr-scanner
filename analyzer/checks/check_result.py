from collections import namedtuple

CheckResult = namedtuple('CheckResult', 'domain identifier passed severity')  # passed means everything is fine, the Check did not fail.
