"""Science-based rule engine for irrigation analysis

This module implements deterministic rules grounded in plant physiology and irrigation science.
Rules evaluate watering practices and provide actionable feedback.

NO ML predictions, NO region-specific promises, NO false precision.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class RuleSeverity(str, Enum):
    """Rule severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class IrrigationRule:
    """Represents a triggered irrigation rule"""
    rule_id: str
    severity: RuleSeverity
    title: str
    explanation: str
    suggested_action: str
    affected_zones: List[int] = None
    affected_gardens: List[int] = None

    def __post_init__(self):
        if self.affected_zones is None:
            self.affected_zones = []
        if self.affected_gardens is None:
            self.affected_gardens = []


class IrrigationRuleEngine:
    """
    Evaluates irrigation practices against science-based rules.

    Rules are conservative and explain WHY, not just WHAT.
    """

    @staticmethod
    def evaluate_zone_watering_frequency(
        zone: Any,
        watering_events: List[Any],
        days_to_analyze: int = 14
    ) -> List[IrrigationRule]:
        """
        Evaluate if watering frequency aligns with good practices.

        Science basis: Most established plants need deep, infrequent watering
        (every 3-7 days) rather than frequent shallow watering.
        """
        rules = []

        if not watering_events:
            return rules

        # Calculate average interval between waterings
        if len(watering_events) > 1:
            sorted_events = sorted(watering_events, key=lambda e: e.watered_at)
            intervals = []
            for i in range(1, len(sorted_events)):
                delta = sorted_events[i].watered_at - sorted_events[i-1].watered_at
                intervals.append(delta.days + delta.seconds / 86400.0)

            if intervals:
                avg_interval = sum(intervals) / len(intervals)

                # Rule: Too frequent watering
                if avg_interval < 2.0:
                    rules.append(IrrigationRule(
                        rule_id="FREQ_001",
                        severity=RuleSeverity.WARNING,
                        title="Watering Too Frequently",
                        explanation=(
                            f"Zone '{zone.name}' is watered every {avg_interval:.1f} days on average. "
                            "Frequent shallow watering encourages shallow root growth and increases "
                            "water waste through evaporation. Most established garden plants benefit "
                            "from deep, infrequent watering that encourages deep root development."
                        ),
                        suggested_action=(
                            "Consider watering less frequently (every 3-7 days) but for longer duration. "
                            "This allows water to penetrate deeper into soil and encourages stronger root systems. "
                            "Check soil moisture 2-3 inches below surface before watering."
                        ),
                        affected_zones=[zone.id]
                    ))

                # Rule: Possibly too infrequent
                elif avg_interval > 10.0:
                    rules.append(IrrigationRule(
                        rule_id="FREQ_002",
                        severity=RuleSeverity.INFO,
                        title="Infrequent Watering Detected",
                        explanation=(
                            f"Zone '{zone.name}' is watered every {avg_interval:.1f} days on average. "
                            "While deep watering is beneficial, very long intervals may stress plants during "
                            "active growth periods, especially in hot weather or sandy soils."
                        ),
                        suggested_action=(
                            "Verify soil moisture before each watering. If soil is consistently dry at 2-3 inches "
                            "depth, consider slightly more frequent watering. Adjust based on weather, soil type, "
                            "and plant needs."
                        ),
                        affected_zones=[zone.id]
                    ))

        return rules

    @staticmethod
    def evaluate_watering_duration(
        zone: Any,
        watering_events: List[Any]
    ) -> List[IrrigationRule]:
        """
        Evaluate if watering duration is appropriate.

        Science basis: Shallow watering (< 10-15 min) rarely penetrates beyond
        top few inches. Deep watering (20-30+ min) reaches root zone.
        """
        rules = []

        if not watering_events:
            return rules

        # Check recent events for short duration
        short_waterings = [e for e in watering_events if e.duration_minutes < 10]
        if len(short_waterings) > len(watering_events) * 0.5:  # More than half are short
            rules.append(IrrigationRule(
                rule_id="DUR_001",
                severity=RuleSeverity.WARNING,
                title="Frequent Shallow Watering",
                explanation=(
                    f"Zone '{zone.name}' has many short watering sessions (< 10 minutes). "
                    "Short watering typically only wets the top 1-2 inches of soil. This encourages "
                    "shallow root growth, increases evaporation loss, and provides poor drought resistance. "
                    "Water needs to penetrate 6-12 inches for most vegetables and flowers."
                ),
                suggested_action=(
                    "Increase watering duration to 20-30 minutes per session (adjust for soil type and "
                    f"delivery method: {zone.delivery_type}). Water less frequently but more deeply. "
                    "Use a soil probe or screwdriver to verify water penetrates 6+ inches."
                ),
                affected_zones=[zone.id]
            ))

        return rules

    @staticmethod
    def evaluate_zone_plant_conflicts(
        zone: Any,
        gardens_in_zone: List[Any],
        planting_events: Dict[int, List[Any]]
    ) -> List[IrrigationRule]:
        """
        Detect if gardens in same zone have conflicting water needs.

        Science basis: Different plants have vastly different water requirements.
        Watering all together can over-water or under-water some plants.
        """
        rules = []

        if len(gardens_in_zone) < 2:
            return rules

        # This is a placeholder for more sophisticated analysis
        # In production, would check plant varieties' water needs
        # For now, we'll check if ANY gardens have soil texture overrides indicating conflict

        soil_types = set()
        for garden in gardens_in_zone:
            if garden.soil_texture_override:
                soil_types.add(garden.soil_texture_override)

        # If mixing sandy and clay soils in same zone
        if 'sandy' in soil_types and 'clay' in soil_types:
            rules.append(IrrigationRule(
                rule_id="CONFLICT_001",
                severity=RuleSeverity.WARNING,
                title="Mixed Soil Types in Same Zone",
                explanation=(
                    f"Zone '{zone.name}' contains gardens with different soil textures (sandy and clay). "
                    "Sandy soil drains quickly and needs more frequent watering. Clay soil retains water "
                    "longer and can become waterlogged if watered as frequently as sandy soil. "
                    "Watering both on the same schedule may over-water clay gardens or under-water sandy ones."
                ),
                suggested_action=(
                    "Consider splitting this zone into separate zones based on soil type, or manually "
                    "adjust watering for individual gardens. Sandy soils may need watering every 3-4 days "
                    "while clay soils may only need watering every 7-10 days."
                ),
                affected_zones=[zone.id],
                affected_gardens=[g.id for g in gardens_in_zone]
            ))

        return rules

    @staticmethod
    def evaluate_soil_moisture_response(
        zone: Any,
        gardens_in_zone: List[Any],
        watering_events: List[Any],
        soil_samples: Dict[int, List[Any]]
    ) -> List[IrrigationRule]:
        """
        Check if soil moisture readings show expected response to watering.

        Science basis: If watering events don't increase soil moisture,
        water may be running off, evaporating, or system has leaks.
        """
        rules = []

        # This requires soil moisture data shortly after watering events
        # For now, check if ANY gardens have persistent low moisture despite watering

        for garden in gardens_in_zone:
            garden_samples = soil_samples.get(garden.id, [])
            if not garden_samples:
                continue

            # Get recent samples (last 30 days)
            recent_samples = [s for s in garden_samples
                            if (datetime.utcnow() - s.date_collected).days <= 30]

            # If multiple samples show consistently low moisture
            low_moisture_count = sum(1 for s in recent_samples
                                    if s.moisture_percent and s.moisture_percent < 20)

            if len(recent_samples) >= 3 and low_moisture_count >= 2:
                # Check if there were watering events
                recent_waterings = [e for e in watering_events
                                  if (datetime.utcnow() - e.watered_at).days <= 30]

                if recent_waterings:
                    rules.append(IrrigationRule(
                        rule_id="RESPONSE_001",
                        severity=RuleSeverity.WARNING,
                        title="Low Soil Moisture Despite Watering",
                        explanation=(
                            f"Garden '{garden.name}' in zone '{zone.name}' shows persistently low soil "
                            "moisture (< 20%) despite recent watering events. This suggests water may not "
                            "be penetrating effectively due to: compacted soil, runoff on slopes, "
                            "extremely sandy soil, or delivery system issues."
                        ),
                        suggested_action=(
                            "Check that water is reaching this garden. For compacted soil, aerate before "
                            "watering. For slopes, create berms or use slower delivery. For sandy soil, "
                            "add compost to improve water retention. Verify emitters/sprinklers are "
                            "functioning properly."
                        ),
                        affected_zones=[zone.id],
                        affected_gardens=[garden.id]
                    ))

        return rules

    @staticmethod
    def evaluate_all(
        zones: List[Any],
        watering_events_by_zone: Dict[int, List[Any]],
        gardens_by_zone: Dict[int, List[Any]],
        soil_samples_by_garden: Dict[int, List[Any]] = None,
        planting_events_by_garden: Dict[int, List[Any]] = None
    ) -> List[IrrigationRule]:
        """
        Evaluate all irrigation rules for all zones.

        Returns comprehensive list of triggered rules.
        """
        all_rules = []

        if soil_samples_by_garden is None:
            soil_samples_by_garden = {}
        if planting_events_by_garden is None:
            planting_events_by_garden = {}

        for zone in zones:
            zone_events = watering_events_by_zone.get(zone.id, [])
            zone_gardens = gardens_by_zone.get(zone.id, [])

            # Evaluate frequency
            all_rules.extend(
                IrrigationRuleEngine.evaluate_zone_watering_frequency(zone, zone_events)
            )

            # Evaluate duration
            all_rules.extend(
                IrrigationRuleEngine.evaluate_watering_duration(zone, zone_events)
            )

            # Evaluate conflicts
            all_rules.extend(
                IrrigationRuleEngine.evaluate_zone_plant_conflicts(
                    zone, zone_gardens, planting_events_by_garden
                )
            )

            # Evaluate soil response
            all_rules.extend(
                IrrigationRuleEngine.evaluate_soil_moisture_response(
                    zone, zone_gardens, zone_events, soil_samples_by_garden
                )
            )

        return all_rules
