# File: main.py
from tests import run_comprehensive_tests, run_performance_tests

def main():
    print("Running comprehensive tests...")
    run_comprehensive_tests()
    
    print("\nRunning performance tests...")
    run_performance_tests()

if __name__ == "__main__":
    main()