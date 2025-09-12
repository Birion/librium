import unittest

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    # Exit with non-zero if tests failed to reflect status in CI-like runs
    import sys

    sys.exit(0 if result.wasSuccessful() else 1)
