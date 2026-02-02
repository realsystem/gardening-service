"""Main runner for performance tests.

Usage:
    python tests/performance/run_performance_tests.py

This script:
1. Generates synthetic data (100 users, 1000 gardens, 10000 plantings)
2. Measures performance under load
3. Generates detailed report
4. Cleans up test data

DO NOT run this on production database!
"""
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database import SessionLocal
from tests.performance.synthetic_data_generator import generate_synthetic_data
from tests.performance.measure_performance import PerformanceMeasurement


def main():
    """Run performance test suite."""
    print("="*60)
    print("SYNTHETIC LOAD PERFORMANCE TEST SUITE")
    print("="*60)
    print("\n⚠️  WARNING: This will create and delete test data")
    print("   DO NOT run on production database!")
    print("\nTest scenario:")
    print("  - 100 users")
    print("  - 1,000 gardens")
    print("  - 10,000 planting events")
    print("\n" + "="*60)

    # Confirm
    confirm = input("\nContinue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Aborted.")
        return

    db = SessionLocal()

    try:
        # Generate synthetic data
        print("\n" + "="*60)
        print("STEP 1: GENERATE SYNTHETIC DATA")
        print("="*60)

        start_time = time.time()
        generator = generate_synthetic_data(
            db,
            num_users=100,
            num_gardens=1000,
            num_plantings=10000
        )
        generation_time = time.time() - start_time

        print(f"\nData generation completed in {generation_time:.2f} seconds")

        # Measure performance
        print("\n" + "="*60)
        print("STEP 2: MEASURE PERFORMANCE")
        print("="*60)

        measurement = PerformanceMeasurement(db)
        results = measurement.measure_all()

        # Generate report
        print("\n" + "="*60)
        print("STEP 3: GENERATE REPORT")
        print("="*60)

        report = measurement.generate_report()

        # Save report
        report_path = Path(__file__).parent / 'PERFORMANCE_REPORT.md'
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\nReport saved to: {report_path}")
        print("\n" + report)

        # Cleanup
        print("\n" + "="*60)
        print("STEP 4: CLEANUP")
        print("="*60)

        cleanup = input("\nDelete generated test data? (yes/no): ")
        if cleanup.lower() == 'yes':
            generator.cleanup()
            print("\nCleanup complete.")
        else:
            print("\nTest data retained. Clean up manually if needed.")
            print("Email pattern: perftest_user_%@example.com")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()

    print("\n" + "="*60)
    print("PERFORMANCE TEST COMPLETE")
    print("="*60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
