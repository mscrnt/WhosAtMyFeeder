import subprocess
import sys


def run_tests():
    """Run the project's test suite using pytest."""
    result = subprocess.run([sys.executable, '-m', 'pytest'], check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(run_tests())
