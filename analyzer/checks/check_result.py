from collections import namedtuple

# passed means everything is fine, the Check did not fail.
# ToDo: passed should probably be non-binary? (eg. passed, failed, uncertain
CheckResult = namedtuple('CheckResult', 'domain identifier passed severity')
