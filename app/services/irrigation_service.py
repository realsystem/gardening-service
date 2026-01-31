"""Irrigation service - orchestrates irrigation system operations"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.repositories.irrigation_zone_repository import IrrigationZoneRepository
from app.repositories.watering_event_repository import WateringEventRepository
from app.repositories.irrigation_source_repository import IrrigationSourceRepository
from app.services.irrigation_rule_engine import IrrigationRuleEngine, IrrigationRule
from app.models.soil_sample import SoilSample
from app.models.planting_event import PlantingEvent


class IrrigationService:
    """
    High-level service for irrigation system operations.

    Orchestrates repositories and rule engine.
    """

    @staticmethod
    def get_irrigation_overview(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get complete irrigation overview for a user.

        Returns zones, sources, recent events, and upcoming scheduled waterings.
        """
        # Get all zones with garden counts
        zones_with_counts = IrrigationZoneRepository.get_with_garden_count(db, user_id)
        zones = [
            {
                'zone': zone,
                'garden_count': count
            }
            for zone, count in zones_with_counts
        ]

        # Get all sources
        sources = IrrigationSourceRepository.get_all(db, user_id)

        # Get recent watering events (last 30 days)
        recent_events = WateringEventRepository.get_all(db, user_id, limit=50)

        # Calculate upcoming scheduled waterings
        upcoming = IrrigationService._calculate_upcoming_waterings(zones, recent_events)

        return {
            'zones': zones,
            'sources': sources,
            'recent_events': recent_events,
            'upcoming_waterings': upcoming
        }

    @staticmethod
    def _calculate_upcoming_waterings(
        zones: List[Dict[str, Any]],
        recent_events: List[Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculate when zones are next scheduled to be watered.

        Based on schedule and last watering event.
        """
        upcoming = []

        for zone_data in zones:
            zone = zone_data['zone']

            # Only if zone has a schedule
            if not zone.schedule or 'frequency_days' not in zone.schedule:
                continue

            frequency_days = zone.schedule.get('frequency_days', 0)
            if frequency_days <= 0:
                continue

            # Find last watering for this zone
            zone_events = [e for e in recent_events if e.irrigation_zone_id == zone.id]
            if not zone_events:
                # Never watered, show as due today
                upcoming.append({
                    'zone_id': zone.id,
                    'zone_name': zone.name,
                    'next_watering': datetime.utcnow(),
                    'days_until': 0,
                    'status': 'overdue'
                })
                continue

            # Get most recent
            last_watering = max(zone_events, key=lambda e: e.watered_at)
            next_watering = last_watering.watered_at + timedelta(days=frequency_days)

            days_until = (next_watering - datetime.utcnow()).days

            status = 'upcoming'
            if days_until < 0:
                status = 'overdue'
            elif days_until == 0:
                status = 'today'

            upcoming.append({
                'zone_id': zone.id,
                'zone_name': zone.name,
                'next_watering': next_watering,
                'days_until': days_until,
                'status': status,
                'last_watered': last_watering.watered_at
            })

        # Sort by due date
        upcoming.sort(key=lambda x: x['next_watering'])

        return upcoming

    @staticmethod
    def get_zone_details(db: Session, zone_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific irrigation zone.

        Includes gardens, recent watering history, and analysis.
        """
        zone = IrrigationZoneRepository.get_by_id(db, zone_id, user_id)
        if not zone:
            return None

        # Get gardens in zone
        gardens = IrrigationZoneRepository.get_gardens_in_zone(db, zone_id, user_id)

        # Get watering history (last 60 days)
        events = WateringEventRepository.get_by_zone(db, zone_id, user_id, days=60)

        # Calculate statistics
        stats = IrrigationService._calculate_zone_statistics(events)

        return {
            'zone': zone,
            'gardens': gardens,
            'recent_events': events[:10],  # Most recent 10
            'statistics': stats
        }

    @staticmethod
    def _calculate_zone_statistics(events: List[Any]) -> Dict[str, Any]:
        """Calculate summary statistics for watering events"""
        if not events:
            return {
                'total_events': 0,
                'avg_duration_minutes': 0,
                'total_duration_hours': 0,
                'manual_count': 0,
                'automated_count': 0
            }

        return {
            'total_events': len(events),
            'avg_duration_minutes': sum(e.duration_minutes for e in events) / len(events),
            'total_duration_hours': sum(e.duration_minutes for e in events) / 60,
            'manual_count': sum(1 for e in events if e.is_manual),
            'automated_count': sum(1 for e in events if not e.is_manual)
        }

    @staticmethod
    def get_irrigation_insights(db: Session, user_id: int) -> List[IrrigationRule]:
        """
        Run rule engine to get irrigation insights and recommendations.

        Returns science-based analysis of irrigation practices.
        """
        # Get all zones
        zones = IrrigationZoneRepository.get_all(db, user_id)

        # Prepare data structures for rule engine
        watering_events_by_zone = {}
        gardens_by_zone = {}

        for zone in zones:
            # Get events for each zone (last 30 days)
            events = WateringEventRepository.get_by_zone(db, zone.id, user_id, days=30)
            watering_events_by_zone[zone.id] = events

            # Get gardens in each zone
            gardens = IrrigationZoneRepository.get_gardens_in_zone(db, zone.id, user_id)
            gardens_by_zone[zone.id] = gardens

        # Get soil samples (last 60 days) - grouped by garden
        soil_samples_by_garden = {}
        cutoff = datetime.utcnow() - timedelta(days=60)
        for zone_gardens in gardens_by_zone.values():
            for garden in zone_gardens:
                samples = db.query(SoilSample).filter(
                    SoilSample.garden_id == garden.id,
                    SoilSample.date_collected >= cutoff
                ).all()
                if samples:
                    soil_samples_by_garden[garden.id] = samples

        # Get planting events - grouped by garden (for conflict detection)
        planting_events_by_garden = {}
        for zone_gardens in gardens_by_zone.values():
            for garden in zone_gardens:
                plantings = db.query(PlantingEvent).filter(
                    PlantingEvent.garden_id == garden.id
                ).all()
                if plantings:
                    planting_events_by_garden[garden.id] = plantings

        # Run rule engine
        rules = IrrigationRuleEngine.evaluate_all(
            zones=zones,
            watering_events_by_zone=watering_events_by_zone,
            gardens_by_zone=gardens_by_zone,
            soil_samples_by_garden=soil_samples_by_garden,
            planting_events_by_garden=planting_events_by_garden
        )

        return rules

    @staticmethod
    def assign_garden_to_zone(
        db: Session,
        garden_id: int,
        zone_id: Optional[int],
        user_id: int
    ) -> bool:
        """
        Assign a garden to an irrigation zone (or remove from zone if zone_id is None).

        Returns True if successful, False if garden or zone not found.
        """
        from app.repositories.garden_repository import GardenRepository

        garden_repo = GardenRepository(db)
        garden = garden_repo.get_by_id(garden_id)
        if not garden or garden.user_id != user_id:
            return False

        if zone_id is not None:
            zone = IrrigationZoneRepository.get_by_id(db, zone_id, user_id)
            if not zone:
                return False

        garden.irrigation_zone_id = zone_id
        db.commit()
        return True
