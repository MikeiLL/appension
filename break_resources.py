from __future__ import print_function
import resource
import time

"""
python break_resources.py

Used this to try and emulate limited system memory
Does not work on my OS X dev server.
"""

usage = resource.getrusage(resource.RUSAGE_SELF)

for name, desc in [
    ('ru_utime', 'User time'),
    ('ru_stime', 'System time'),
    ('ru_maxrss', 'Max. Resident Set Size'),
    ('ru_ixrss', 'Shared Memory Size'),
    ('ru_idrss', 'Unshared Memory Size'),
    ('ru_isrss', 'Stack Size'),
    ('ru_inblock', 'Block inputs'),
    ('ru_oublock', 'Block outputs'),
    ]:
    print('%-25s (%-10s) = %s' % (desc, name, getattr(usage, name)))

for n in range(0, 1000000000):
    n = n * 100000000000

resource.setrlimit(resource.RLIMIT_CORE, (1, 100))
