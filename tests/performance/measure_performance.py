"""Performance measurement for synthetic load scenarios.

Measures:
- Rule engine execution time under load
- Layout rendering performance
- Database query performance
- API endpoint latency

Documents bottlenecks without optimization.
"""
import time
import statistics
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.garden import Garden
from app.models.planting_event import PlantingEvent
from app.rules.task_generator import TaskGenerator


class PerformanceMeasurement:
    """Measures performance under synthetic load."""

    def __init__(self, db: Session):
        self.db = db
        self.results: Dict[str, Any] = {}

    def measure_all(self) -> Dict[str, Any]:
        """Run all performance measurements.

        Returns:
            Dictionary with performance metrics
        """
        print("\n" + "="*60)
        print("PERFORMANCE MEASUREMENT SUITE")
        print("="*60)

        self.results['database_stats'] = self._measure_database_stats()
        self.results['rule_engine'] = self._measure_rule_engine_performance()
        self.results['layout_rendering'] = self._measure_layout_rendering()
        self.results['query_performance'] = self._measure_query_performance()

        print("\n" + "="*60)
        print("MEASUREMENT COMPLETE")
        print("="*60)

        return self.results

    def _measure_database_stats(self) -> Dict[str, int]:
        """Get baseline database statistics."""
        print("\n--- Database Statistics ---")

        stats = {
            'users': self.db.query(User).count(),
            'gardens': self.db.query(Garden).count(),
            'plantings': self.db.query(PlantingEvent).count(),
        }

        print(f"Users: {stats['users']:,}")
        print(f"Gardens: {stats['gardens']:,}")
        print(f"Plantings: {stats['plantings']:,}")

        return stats

    def _measure_rule_engine_performance(self) -> Dict[str, Any]:
        """Measure rule engine performance under load."""
        print("\n--- Rule Engine Performance ---")

        # Sample plantings for testing
        sample_size = 100
        plantings = self.db.query(PlantingEvent).limit(sample_size).all()

        print(f"Testing with {len(plantings)} planting events...")

        generator = TaskGenerator()
        execution_times = []
        task_counts = []

        for i, planting in enumerate(plantings):
            start_time = time.time()

            # Generate tasks for this planting
            tasks = generator.generate_tasks_for_planting(
                self.db,
                planting,
                planting.user_id
            )

            execution_time = (time.time() - start_time) * 1000  # Convert to ms

            execution_times.append(execution_time)
            task_counts.append(len(tasks))

            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(plantings)} plantings...")

        # Calculate statistics
        results = {
            'sample_size': len(plantings),
            'execution_times_ms': {
                'min': min(execution_times),
                'max': max(execution_times),
                'mean': statistics.mean(execution_times),
                'median': statistics.median(execution_times),
                'p95': statistics.quantiles(execution_times, n=20)[18],  # 95th percentile
                'p99': statistics.quantiles(execution_times, n=100)[98],  # 99th percentile
            },
            'tasks_generated': {
                'total': sum(task_counts),
                'mean_per_planting': statistics.mean(task_counts),
                'min': min(task_counts),
                'max': max(task_counts),
            },
            'throughput': {
                'plantings_per_second': len(plantings) / (sum(execution_times) / 1000),
            }
        }

        print("\nRule Engine Results:")
        print(f"  Execution time (ms):")
        print(f"    Min: {results['execution_times_ms']['min']:.2f}")
        print(f"    Mean: {results['execution_times_ms']['mean']:.2f}")
        print(f"    Median: {results['execution_times_ms']['median']:.2f}")
        print(f"    p95: {results['execution_times_ms']['p95']:.2f}")
        print(f"    p99: {results['execution_times_ms']['p99']:.2f}")
        print(f"    Max: {results['execution_times_ms']['max']:.2f}")
        print(f"  Tasks generated: {results['tasks_generated']['total']}")
        print(f"  Throughput: {results['throughput']['plantings_per_second']:.2f} plantings/sec")

        # Identify bottlenecks
        if results['execution_times_ms']['p95'] > 100:
            print("\n  ⚠️  BOTTLENECK: p95 latency > 100ms")
            print(f"     Rule engine is slow. Consider optimization.")

        if results['execution_times_ms']['max'] > 500:
            print("\n  ⚠️  BOTTLENECK: Max latency > 500ms")
            print(f"     Some plantings take very long to process.")

        return results

    def _measure_layout_rendering(self) -> Dict[str, Any]:
        """Measure layout rendering performance."""
        print("\n--- Layout Rendering Performance ---")

        # Sample gardens with many plantings
        gardens_with_plantings = (
            self.db.query(Garden)
            .join(PlantingEvent)
            .group_by(Garden.id)
            .limit(50)
            .all()
        )

        print(f"Testing with {len(gardens_with_plantings)} gardens...")

        rendering_times = []
        planting_counts = []

        for i, garden in enumerate(gardens_with_plantings):
            # Get plantings for this garden
            plantings = (
                self.db.query(PlantingEvent)
                .filter(PlantingEvent.garden_id == garden.id)
                .all()
            )

            start_time = time.time()

            # Simulate layout rendering (get positions, calculate overlaps)
            layout_data = self._simulate_layout_rendering(plantings)

            rendering_time = (time.time() - start_time) * 1000  # ms

            rendering_times.append(rendering_time)
            planting_counts.append(len(plantings))

            if (i + 1) % 10 == 0:
                print(f"  Rendered {i + 1}/{len(gardens_with_plantings)} gardens...")

        # Calculate statistics
        results = {
            'sample_size': len(gardens_with_plantings),
            'rendering_times_ms': {
                'min': min(rendering_times) if rendering_times else 0,
                'max': max(rendering_times) if rendering_times else 0,
                'mean': statistics.mean(rendering_times) if rendering_times else 0,
                'median': statistics.median(rendering_times) if rendering_times else 0,
                'p95': statistics.quantiles(rendering_times, n=20)[18] if len(rendering_times) > 20 else max(rendering_times) if rendering_times else 0,
            },
            'planting_counts': {
                'mean': statistics.mean(planting_counts) if planting_counts else 0,
                'max': max(planting_counts) if planting_counts else 0,
            }
        }

        print("\nLayout Rendering Results:")
        print(f"  Rendering time (ms):")
        print(f"    Min: {results['rendering_times_ms']['min']:.2f}")
        print(f"    Mean: {results['rendering_times_ms']['mean']:.2f}")
        print(f"    Median: {results['rendering_times_ms']['median']:.2f}")
        print(f"    p95: {results['rendering_times_ms']['p95']:.2f}")
        print(f"    Max: {results['rendering_times_ms']['max']:.2f}")
        print(f"  Mean plantings per garden: {results['planting_counts']['mean']:.1f}")

        # Identify bottlenecks
        if results['rendering_times_ms']['p95'] > 50:
            print("\n  ⚠️  BOTTLENECK: p95 rendering time > 50ms")
            print(f"     Layout calculation is slow. Consider:")
            print(f"     - Spatial indexing")
            print(f"     - Client-side rendering")
            print(f"     - Pagination for large gardens")

        return results

    def _simulate_layout_rendering(self, plantings: List[PlantingEvent]) -> Dict[str, Any]:
        """Simulate layout rendering (position calculation, overlap detection)."""
        import math

        layout_data = {
            'plantings': [],
            'overlaps': [],
        }

        # Calculate positions
        for planting in plantings:
            if planting.x is not None and planting.y is not None:
                layout_data['plantings'].append({
                    'id': planting.id,
                    'x': planting.x,
                    'y': planting.y,
                })

        # Check for overlaps (O(n²) - potential bottleneck!)
        for i, p1 in enumerate(layout_data['plantings']):
            for p2 in layout_data['plantings'][i+1:]:
                distance = math.sqrt(
                    (p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2
                )
                if distance < 0.5:  # 50cm threshold
                    layout_data['overlaps'].append({
                        'planting1': p1['id'],
                        'planting2': p2['id'],
                        'distance': distance,
                    })

        return layout_data

    def _measure_query_performance(self) -> Dict[str, Any]:
        """Measure database query performance."""
        print("\n--- Query Performance ---")

        queries = {
            'user_gardens': self._measure_user_gardens_query,
            'garden_plantings': self._measure_garden_plantings_query,
            'active_plantings': self._measure_active_plantings_query,
        }

        results = {}

        for query_name, query_func in queries.items():
            print(f"\nTesting {query_name}...")
            results[query_name] = query_func()

        return results

    def _measure_user_gardens_query(self) -> Dict[str, Any]:
        """Measure user gardens query (common operation)."""
        # Get 20 random users
        users = self.db.query(User).limit(20).all()

        execution_times = []

        for user in users:
            start_time = time.time()

            # Query user's gardens
            gardens = (
                self.db.query(Garden)
                .filter(Garden.user_id == user.id)
                .all()
            )

            execution_time = (time.time() - start_time) * 1000

            execution_times.append(execution_time)

        results = {
            'mean_ms': statistics.mean(execution_times),
            'p95_ms': statistics.quantiles(execution_times, n=20)[18] if len(execution_times) > 20 else max(execution_times),
            'max_ms': max(execution_times),
        }

        print(f"  Mean: {results['mean_ms']:.2f}ms")
        print(f"  p95: {results['p95_ms']:.2f}ms")

        if results['p95_ms'] > 50:
            print(f"  ⚠️  BOTTLENECK: Slow user gardens query")

        return results

    def _measure_garden_plantings_query(self) -> Dict[str, Any]:
        """Measure garden plantings query (common operation)."""
        # Get 20 random gardens
        gardens = self.db.query(Garden).limit(20).all()

        execution_times = []

        for garden in gardens:
            start_time = time.time()

            # Query garden's plantings
            plantings = (
                self.db.query(PlantingEvent)
                .filter(PlantingEvent.garden_id == garden.id)
                .all()
            )

            execution_time = (time.time() - start_time) * 1000

            execution_times.append(execution_time)

        results = {
            'mean_ms': statistics.mean(execution_times),
            'p95_ms': statistics.quantiles(execution_times, n=20)[18] if len(execution_times) > 20 else max(execution_times),
            'max_ms': max(execution_times),
        }

        print(f"  Mean: {results['mean_ms']:.2f}ms")
        print(f"  p95: {results['p95_ms']:.2f}ms")

        if results['p95_ms'] > 50:
            print(f"  ⚠️  BOTTLENECK: Slow garden plantings query")

        return results

    def _measure_active_plantings_query(self) -> Dict[str, Any]:
        """Measure active plantings query (for dashboard)."""
        from datetime import date, timedelta

        execution_times = []

        # Run query 10 times
        for _ in range(10):
            start_time = time.time()

            # Query plantings from last 30 days
            cutoff_date = date.today() - timedelta(days=30)
            plantings = (
                self.db.query(PlantingEvent)
                .filter(PlantingEvent.planting_date >= cutoff_date)
                .all()
            )

            execution_time = (time.time() - start_time) * 1000

            execution_times.append(execution_time)

        results = {
            'mean_ms': statistics.mean(execution_times),
            'max_ms': max(execution_times),
        }

        print(f"  Mean: {results['mean_ms']:.2f}ms")
        print(f"  Max: {results['max_ms']:.2f}ms")

        if results['mean_ms'] > 100:
            print(f"  ⚠️  BOTTLENECK: Slow active plantings query")
            print(f"     Consider adding index on planting_date")

        return results

    def generate_report(self) -> str:
        """Generate performance report.

        Returns:
            Markdown-formatted report
        """
        report = []
        report.append("# Performance Test Report\n")
        report.append(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("\n## Database Statistics\n")
        report.append(f"- Users: {self.results['database_stats']['users']:,}")
        report.append(f"- Gardens: {self.results['database_stats']['gardens']:,}")
        report.append(f"- Plantings: {self.results['database_stats']['plantings']:,}\n")

        report.append("\n## Rule Engine Performance\n")
        re = self.results['rule_engine']
        report.append(f"- Sample size: {re['sample_size']} plantings")
        report.append(f"- Mean execution time: {re['execution_times_ms']['mean']:.2f}ms")
        report.append(f"- p95 execution time: {re['execution_times_ms']['p95']:.2f}ms")
        report.append(f"- p99 execution time: {re['execution_times_ms']['p99']:.2f}ms")
        report.append(f"- Throughput: {re['throughput']['plantings_per_second']:.2f} plantings/sec")
        report.append(f"- Tasks generated: {re['tasks_generated']['total']}\n")

        report.append("\n## Layout Rendering Performance\n")
        lr = self.results['layout_rendering']
        report.append(f"- Sample size: {lr['sample_size']} gardens")
        report.append(f"- Mean rendering time: {lr['rendering_times_ms']['mean']:.2f}ms")
        report.append(f"- p95 rendering time: {lr['rendering_times_ms']['p95']:.2f}ms")
        report.append(f"- Max rendering time: {lr['rendering_times_ms']['max']:.2f}ms")
        report.append(f"- Mean plantings per garden: {lr['planting_counts']['mean']:.1f}\n")

        report.append("\n## Query Performance\n")
        qp = self.results['query_performance']
        report.append(f"### User Gardens Query")
        report.append(f"- Mean: {qp['user_gardens']['mean_ms']:.2f}ms")
        report.append(f"- p95: {qp['user_gardens']['p95_ms']:.2f}ms\n")
        report.append(f"### Garden Plantings Query")
        report.append(f"- Mean: {qp['garden_plantings']['mean_ms']:.2f}ms")
        report.append(f"- p95: {qp['garden_plantings']['p95_ms']:.2f}ms\n")
        report.append(f"### Active Plantings Query")
        report.append(f"- Mean: {qp['active_plantings']['mean_ms']:.2f}ms")
        report.append(f"- Max: {qp['active_plantings']['max_ms']:.2f}ms\n")

        return "\n".join(report)
