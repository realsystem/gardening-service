"""
Nutrient Optimization Service

Science-based EC/pH optimization for hydroponic, fertigation, and container systems.
Provides deterministic, explainable recommendations based on plant growth stages and requirements.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.garden import Garden, HydroSystemType
from app.models.planting_event import PlantingEvent
from app.models.plant_variety import PlantVariety
from app.models.growth_stage import GrowthStage


@dataclass
class NutrientWarning:
    """A warning or alert about nutrient management"""
    warning_id: str
    severity: str  # "info", "warning", "critical"
    message: str
    mitigation: str


@dataclass
class ECRecommendation:
    """EC range recommendation with rationale"""
    min_ms_cm: float
    max_ms_cm: float
    rationale: str


@dataclass
class PHRecommendation:
    """pH range recommendation with rationale"""
    min_ph: float
    max_ph: float
    rationale: str


@dataclass
class ReplacementSchedule:
    """Water replacement schedule recommendation"""
    topoff_interval_days: int
    full_replacement_days: int
    rationale: str


@dataclass
class NutrientOptimizationResult:
    """Complete nutrient optimization result for a garden"""
    garden_id: int
    garden_name: str
    system_type: str

    ec_recommendation: ECRecommendation
    ph_recommendation: PHRecommendation
    replacement_schedule: ReplacementSchedule

    warnings: List[NutrientWarning]
    active_plantings: List[dict]

    generated_at: datetime


class NutrientOptimizationService:
    """
    Service for generating science-based nutrient optimization recommendations.

    Based on:
    - Plant growth stages
    - Crop nutrient requirements
    - System type (hydroponic, fertigation, container)
    - Reservoir size
    - Plant density
    """

    # Safe EC bounds (mS/cm) - absolute limits for plant health
    ABSOLUTE_EC_MIN = 0.4
    ABSOLUTE_EC_MAX = 3.5

    # Safe pH bounds - most nutrients available in this range
    ABSOLUTE_PH_MIN = 4.0
    ABSOLUTE_PH_MAX = 8.0

    # Default values for missing data
    DEFAULT_EC_MIN = 1.0
    DEFAULT_EC_MAX = 2.0
    DEFAULT_PH_MIN = 5.5
    DEFAULT_PH_MAX = 6.5
    DEFAULT_CHANGE_DAYS = 10

    def optimize_for_garden(self, garden: Garden, db: Session) -> NutrientOptimizationResult:
        """
        Generate complete nutrient optimization for a garden.

        Args:
            garden: Garden instance (must be hydroponic/fertigation/container)
            db: Database session

        Returns:
            NutrientOptimizationResult with EC/pH/schedule recommendations
        """
        # Get active plantings
        active_plantings = self._get_active_plantings(garden, db)

        # Determine growth stages for each planting
        planting_stages = []
        for planting in active_plantings:
            stage = self._calculate_growth_stage(planting)
            planting_stages.append({
                'planting': planting,
                'variety': planting.plant_variety,
                'growth_stage': stage
            })

        # Calculate EC recommendation
        ec_rec = self._calculate_ec_recommendation(planting_stages)

        # Calculate pH recommendation
        ph_rec = self._calculate_ph_recommendation(planting_stages)

        # Calculate replacement schedule
        schedule = self._calculate_replacement_schedule(
            garden.reservoir_size_liters,
            len(active_plantings),
            garden.hydro_system_type,
            planting_stages
        )

        # Detect warnings
        warnings = self._detect_warnings(garden, planting_stages, ec_rec, ph_rec)

        # Build active plantings summary
        active_summary = [
            {
                'plant_name': ps['variety'].common_name if ps['variety'] else 'Unknown',
                'growth_stage': ps['growth_stage'].value
            }
            for ps in planting_stages
        ]

        return NutrientOptimizationResult(
            garden_id=garden.id,
            garden_name=garden.name,
            system_type=garden.hydro_system_type.value if garden.hydro_system_type else "unknown",
            ec_recommendation=ec_rec,
            ph_recommendation=ph_rec,
            replacement_schedule=schedule,
            warnings=warnings,
            active_plantings=active_summary,
            generated_at=datetime.utcnow()
        )

    def _get_active_plantings(self, garden: Garden, db: Session) -> List[PlantingEvent]:
        """Get all active plantings for a garden (not harvested yet)"""
        return db.query(PlantingEvent).filter(
            PlantingEvent.garden_id == garden.id
        ).all()

    def _calculate_growth_stage(self, planting: PlantingEvent) -> GrowthStage:
        """
        Determine growth stage based on days since planting and days to harvest.

        Growth stages:
        - 0-25% of cycle: SEEDLING
        - 25-60% of cycle: VEGETATIVE
        - 60-90% of cycle: FLOWERING
        - 90-100% of cycle: FRUITING

        If no harvest data, default to VEGETATIVE (most conservative)
        """
        days_since_planting = (date.today() - planting.planting_date).days

        if not planting.plant_variety or not planting.plant_variety.days_to_harvest:
            # Default to vegetative if no data
            return GrowthStage.VEGETATIVE

        days_to_harvest = planting.plant_variety.days_to_harvest
        progress_percent = (days_since_planting / days_to_harvest) * 100

        if progress_percent < 25:
            return GrowthStage.SEEDLING
        elif progress_percent < 60:
            return GrowthStage.VEGETATIVE
        elif progress_percent < 90:
            return GrowthStage.FLOWERING
        else:
            return GrowthStage.FRUITING

    def _calculate_ec_recommendation(self, planting_stages: List[dict]) -> ECRecommendation:
        """
        Calculate EC range based on all active plantings.

        Strategy: Use MAXIMUM EC demand among all plants (highest EC wins).
        Rationale: Prevents under-feeding high-demand crops. Lower-demand crops
        can tolerate slightly higher EC better than high-demand crops can tolerate
        deficiency.
        """
        if not planting_stages:
            # No plantings - return safe defaults
            return ECRecommendation(
                min_ms_cm=self.DEFAULT_EC_MIN,
                max_ms_cm=self.DEFAULT_EC_MAX,
                rationale="Default EC range for empty system. Add plants to get customized recommendations."
            )

        ec_min = 0.0
        ec_max = 0.0
        rationale_parts = []

        for ps in planting_stages:
            variety = ps['variety']
            stage = ps['growth_stage']

            if not variety:
                continue

            # Get EC for this plant's current growth stage
            plant_ec_min, plant_ec_max = self._get_ec_for_stage(variety, stage)

            # Use maximum demand (highest EC)
            if plant_ec_max > ec_max:
                ec_max = plant_ec_max
                ec_min = plant_ec_min
                dominant_plant = variety.common_name
                dominant_stage = stage.value

        # Clamp to safe bounds
        ec_min = max(self.ABSOLUTE_EC_MIN, ec_min)
        ec_max = min(self.ABSOLUTE_EC_MAX, ec_max)

        # Build rationale
        if len(planting_stages) == 1:
            rationale = f"Optimized for {dominant_plant} in {dominant_stage} stage"
        else:
            rationale = (
                f"Optimized for highest demand crop: {dominant_plant} ({dominant_stage}). "
                f"Multiple crops present - EC set to prevent under-feeding."
            )

        return ECRecommendation(
            min_ms_cm=round(ec_min, 1),
            max_ms_cm=round(ec_max, 1),
            rationale=rationale
        )

    def _get_ec_for_stage(self, variety: PlantVariety, stage: GrowthStage) -> Tuple[float, float]:
        """Get EC min/max for a variety at a specific growth stage"""
        if stage == GrowthStage.SEEDLING:
            ec_min = variety.seedling_ec_min or self.DEFAULT_EC_MIN
            ec_max = variety.seedling_ec_max or self.DEFAULT_EC_MAX
        elif stage == GrowthStage.VEGETATIVE:
            ec_min = variety.vegetative_ec_min or self.DEFAULT_EC_MIN
            ec_max = variety.vegetative_ec_max or self.DEFAULT_EC_MAX
        elif stage == GrowthStage.FLOWERING:
            ec_min = variety.flowering_ec_min or self.DEFAULT_EC_MIN
            ec_max = variety.flowering_ec_max or self.DEFAULT_EC_MAX
        elif stage == GrowthStage.FRUITING:
            ec_min = variety.fruiting_ec_min or self.DEFAULT_EC_MIN
            ec_max = variety.fruiting_ec_max or self.DEFAULT_EC_MAX
        else:
            ec_min = self.DEFAULT_EC_MIN
            ec_max = self.DEFAULT_EC_MAX

        return (ec_min, ec_max)

    def _calculate_ph_recommendation(self, planting_stages: List[dict]) -> PHRecommendation:
        """
        Calculate pH range based on all active plantings.

        Strategy: Find INTERSECTION of all pH ranges (most restrictive wins).
        Rationale: All plants must be able to uptake nutrients. If ranges don't
        overlap, flag warning and use most common range.
        """
        if not planting_stages:
            return PHRecommendation(
                min_ph=self.DEFAULT_PH_MIN,
                max_ph=self.DEFAULT_PH_MAX,
                rationale="Default pH range for empty system"
            )

        # Collect all pH ranges
        ph_ranges = []
        for ps in planting_stages:
            variety = ps['variety']
            if variety and variety.optimal_ph_min and variety.optimal_ph_max:
                ph_ranges.append({
                    'min': variety.optimal_ph_min,
                    'max': variety.optimal_ph_max,
                    'plant': variety.common_name
                })

        if not ph_ranges:
            return PHRecommendation(
                min_ph=self.DEFAULT_PH_MIN,
                max_ph=self.DEFAULT_PH_MAX,
                rationale="Using default pH range (no crop-specific data available)"
            )

        # Find intersection
        intersection_min = max(r['min'] for r in ph_ranges)
        intersection_max = min(r['max'] for r in ph_ranges)

        # Check if intersection is valid
        if intersection_min > intersection_max:
            # No overlap - use most common range (5.5-6.5)
            return PHRecommendation(
                min_ph=5.5,
                max_ph=6.5,
                rationale=(
                    f"pH conflict detected between crops. Using compromise range 5.5-6.5. "
                    f"Consider separating incompatible crops into different systems."
                )
            )

        # Valid intersection found
        rationale = f"pH range compatible with all {len(planting_stages)} crops"

        return PHRecommendation(
            min_ph=round(intersection_min, 1),
            max_ph=round(intersection_max, 1),
            rationale=rationale
        )

    def _calculate_replacement_schedule(
        self,
        reservoir_size: Optional[float],
        plant_count: int,
        system_type: Optional[HydroSystemType],
        planting_stages: List[dict]
    ) -> ReplacementSchedule:
        """
        Calculate water replacement schedule.

        Factors:
        - Reservoir size: Larger = more stable, longer intervals
        - Plant count: More plants = faster depletion
        - System type: DWC/NFT different dynamics
        - Growth stage: Fruiting = higher uptake
        """
        # Base change interval
        if planting_stages:
            # Get average recommended change days from varieties
            change_days_list = []
            for ps in planting_stages:
                variety = ps['variety']
                if variety and variety.solution_change_days_max:
                    change_days_list.append(variety.solution_change_days_max)

            if change_days_list:
                base_days = sum(change_days_list) / len(change_days_list)
            else:
                base_days = self.DEFAULT_CHANGE_DAYS
        else:
            base_days = self.DEFAULT_CHANGE_DAYS

        # Adjust for reservoir size
        if reservoir_size:
            if reservoir_size < 20:  # Small reservoir
                size_multiplier = 0.7
            elif reservoir_size < 50:  # Medium reservoir
                size_multiplier = 1.0
            else:  # Large reservoir
                size_multiplier = 1.3
        else:
            size_multiplier = 1.0

        # Adjust for plant density
        if plant_count == 0:
            density_multiplier = 1.5
        elif plant_count < 5:
            density_multiplier = 1.2
        elif plant_count < 15:
            density_multiplier = 1.0
        else:
            density_multiplier = 0.8

        # Calculate final days
        full_replacement_days = int(base_days * size_multiplier * density_multiplier)
        full_replacement_days = max(5, min(21, full_replacement_days))  # Clamp to 5-21 days

        # Top-off is daily for all systems
        topoff_interval_days = 1

        # Build rationale
        rationale_parts = []
        if reservoir_size and reservoir_size < 20:
            rationale_parts.append("Small reservoir requires more frequent changes")
        if plant_count > 15:
            rationale_parts.append("High plant density accelerates nutrient depletion")
        if system_type in [HydroSystemType.DWC, HydroSystemType.NFT]:
            rationale_parts.append("Recirculating system requires regular monitoring")

        if rationale_parts:
            rationale = ". ".join(rationale_parts) + "."
        else:
            rationale = "Standard replacement schedule based on system characteristics"

        return ReplacementSchedule(
            topoff_interval_days=topoff_interval_days,
            full_replacement_days=full_replacement_days,
            rationale=rationale
        )

    def _detect_warnings(
        self,
        garden: Garden,
        planting_stages: List[dict],
        ec_rec: ECRecommendation,
        ph_rec: PHRecommendation
    ) -> List[NutrientWarning]:
        """Detect potential issues and generate warnings"""
        warnings = []

        # Warning: No plantings
        if not planting_stages:
            warnings.append(NutrientWarning(
                warning_id="NO_PLANTS",
                severity="info",
                message="No active plantings in this garden",
                mitigation="Add plantings to receive crop-specific nutrient recommendations"
            ))

        # Warning: Very small reservoir
        if garden.reservoir_size_liters and garden.reservoir_size_liters < 10:
            warnings.append(NutrientWarning(
                warning_id="SMALL_RESERVOIR",
                severity="warning",
                message=f"Small reservoir ({garden.reservoir_size_liters}L) may be unstable",
                mitigation="Monitor EC/pH daily. Consider upgrading to larger reservoir (20L+) for better stability"
            ))

        # Warning: pH conflict (detected in pH calculation)
        if "conflict" in ph_rec.rationale.lower():
            warnings.append(NutrientWarning(
                warning_id="PH_CONFLICT",
                severity="warning",
                message="Crops have incompatible pH requirements",
                mitigation="Separate crops into different systems or accept compromise pH range"
            ))

        # Warning: High EC (> 3.0)
        if ec_rec.max_ms_cm > 3.0:
            warnings.append(NutrientWarning(
                warning_id="HIGH_EC",
                severity="warning",
                message=f"High EC recommendation ({ec_rec.max_ms_cm} mS/cm) - monitor for salt stress",
                mitigation="Watch for leaf tip burn. Reduce EC if plants show stress symptoms"
            ))

        # Warning: Very low EC (< 0.5)
        if ec_rec.min_ms_cm < 0.5:
            warnings.append(NutrientWarning(
                warning_id="LOW_EC",
                severity="info",
                message=f"Low EC recommendation ({ec_rec.min_ms_cm} mS/cm) for sensitive crops",
                mitigation="Normal for seedlings and sensitive greens. Increase EC as plants mature"
            ))

        return warnings