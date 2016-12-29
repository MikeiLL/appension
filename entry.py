# cProfile doesn't know how to import a package, so this bouncer is needed.
# time python -m cProfile -o profile.log entry.py major_glitch --dev
# python -m pstats profile.log
import glitch.__main__
