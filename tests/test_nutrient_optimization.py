"""Tests for Nutrient Optimization Service"""
import pytest
from datetime import date, timedelta
from app.services.nutrient_optimization_service import NutrientOptimizationService
from app.models.garden import Garden, GardenType, HydroSystemType
from app.models.plant_variety import PlantVariety
from app.models.planting_event import PlantingEvent, PlantingMethod
from app.models.growth_stage import GrowthStage


@pytest.fixture
def nutrient_service():
    """Create nutrient optimization service instance"""
    return NutrientOptimizationService()


@pytest.fixture
def hydroponic_garden(test_db, sample_user):
    """Create a hydroponic DWC garden"""
    garden = Garden(
        user_id=sample_user.id,
        name="Hydroponic Test Garden",
        garden_type=GardenType.INDOOR,
        is_hydroponic=True,
        hydro_system_type=HydroSystemType.DWC,
        reservoir_size_liters=50.0,
        ph_min=5.5,
        ph_max=6.5,
        ec_min=1.0,
        ec_max=2.0
    )
    test_db.add(garden)
    test_db.commit()
    test_db.refresh(garden)
    return garden


@pytest.fixture
def tomato_variety_with_nutrients(test_db):
    """Create tomato variety with full nutrient profile"""
    variety = PlantVariety(
        common_name="Tomato",
        scientific_name="Solanum lycopersicum",
        days_to_harvest=80,
        # Nutrient profiles
        seedling_ec_min=0.8,
        seedling_ec_max=1.2,
        vegetative_ec_min=1.5,
        vegetative_ec_max=2.0,
        flowering_ec_min=2.0,
        flowering_ec_max=2.5,
        fruiting_ec_min=2.5,
        fruiting_ec_max=3.0,
        optimal_ph_min=5.5,
        optimal_ph_max=6.5,
        solution_change_days_min=7,
        solution_change_days_max=14
    )
    test_db.add(variety)
    test_db.commit()
    test_db.refresh(variety)
    return variety


@pytest.fixture
def lettuce_variety_with_nutrients(test_db):
    """Create lettuce variety with nutrient profile"""
    variety = PlantVariety(
        common_name="Lettuce",
        scientific_name="Lactuca sativa",
        days_to_harvest=60,
        # Nutrient profiles (lower demand than tomato)
        seedling_ec_min=0.4,
        seedling_ec_max=0.8,
        vegetative_ec_min=0.8,
        vegetative_ec_max=1.2,
        optimal_ph_min=5.5,
        optimal_ph_max=6.5,
        solution_change_days_min=7,
        solution_change_days_max=10
    )
    test_db.add(variety)
    test_db.commit()
    test_db.refresh(variety)
    return variety


@pytest.mark.nutrient_optimization
class TestGrowthStageCalculation:
    """Test growth stage determination"""

    def test_seedling_stage_early(self, nutrient_service, test_db, hydroponic_garden, tomato_variety_with_nutrients, sample_user):
        """Test seedling stage (0-25% of cycle)"""
        planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=10),  # 10/80 = 12.5%
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()
        test_db.refresh(planting)

        stage = nutrient_service._calculate_growth_stage(planting)
        assert stage == GrowthStage.SEEDLING

    def test_vegetative_stage(self, nutrient_service, test_db, hydroponic_garden, tomato_variety_with_nutrients, sample_user):
        """Test vegetative stage (25-60% of cycle)"""
        planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=35),  # 35/80 = 43.75%
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()
        test_db.refresh(planting)

        stage = nutrient_service._calculate_growth_stage(planting)
        assert stage == GrowthStage.VEGETATIVE

    def test_flowering_stage(self, nutrient_service, test_db, hydroponic_garden, tomato_variety_with_nutrients, sample_user):
        """Test flowering stage (60-90% of cycle)"""
        planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=56),  # 56/80 = 70%
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()
        test_db.refresh(planting)

        stage = nutrient_service._calculate_growth_stage(planting)
        assert stage == GrowthStage.FLOWERING

    def test_fruiting_stage(self, nutrient_service, test_db, hydroponic_garden, tomato_variety_with_nutrients, sample_user):
        """Test fruiting stage (90-100% of cycle)"""
        planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=75),  # 75/80 = 93.75%
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()
        test_db.refresh(planting)

        stage = nutrient_service._calculate_growth_stage(planting)
        assert stage == GrowthStage.FRUITING

    def test_default_to_vegetative_when_no_harvest_data(self, nutrient_service, test_db, hydroponic_garden, sample_user):
        """Test defaults to vegetative when no harvest date available"""
        variety_no_harvest = PlantVariety(
            common_name="Test Plant",
            days_to_harvest=None  # No harvest data
        )
        test_db.add(variety_no_harvest)
        test_db.commit()

        planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=variety_no_harvest.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=30),
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()
        test_db.refresh(planting)

        stage = nutrient_service._calculate_growth_stage(planting)
        assert stage == GrowthStage.VEGETATIVE


@pytest.mark.nutrient_optimization
class TestECCalculation:
    """Test EC range calculation"""

    def test_seedling_ec_low_demand(self, nutrient_service, test_db, hydroponic_garden, tomato_variety_with_nutrients, sample_user):
        """Test EC for seedling stage uses low values"""
        planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=10),  # Seedling
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()
        test_db.refresh(planting)

        result = nutrient_service.optimize_for_garden(hydroponic_garden, test_db)

        assert result.ec_recommendation.min_ms_cm == 0.8
        assert result.ec_recommendation.max_ms_cm == 1.2
        assert "seedling" in result.ec_recommendation.rationale.lower()

    def test_fruiting_ec_high_demand(self, nutrient_service, test_db, hydroponic_garden, tomato_variety_with_nutrients, sample_user):
        """Test EC for fruiting stage uses high values"""
        planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=75),  # Fruiting
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()
        test_db.refresh(planting)

        result = nutrient_service.optimize_for_garden(hydroponic_garden, test_db)

        assert result.ec_recommendation.min_ms_cm == 2.5
        assert result.ec_recommendation.max_ms_cm == 3.0
        assert "fruiting" in result.ec_recommendation.rationale.lower()

    def test_mixed_crops_use_max_demand(self, nutrient_service, test_db, hydroponic_garden,
                                        tomato_variety_with_nutrients, lettuce_variety_with_nutrients, sample_user):
        """Test mixed crops use highest EC demand (tomato > lettuce)"""
        # Tomato in fruiting (high EC)
        tomato_planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=75),
            planting_method=PlantingMethod.TRANSPLANT
        )
        # Lettuce in vegetative (low EC)
        lettuce_planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=lettuce_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=30),
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add_all([tomato_planting, lettuce_planting])
        test_db.commit()

        result = nutrient_service.optimize_for_garden(hydroponic_garden, test_db)

        # Should use tomato's higher EC (2.5-3.0) not lettuce's lower EC (0.8-1.2)
        assert result.ec_recommendation.max_ms_cm == 3.0
        assert "tomato" in result.ec_recommendation.rationale.lower()
        assert "highest demand" in result.ec_recommendation.rationale.lower()

    def test_empty_garden_returns_defaults(self, nutrient_service, test_db, hydroponic_garden):
        """Test empty garden returns default EC values"""
        result = nutrient_service.optimize_for_garden(hydroponic_garden, test_db)

        assert result.ec_recommendation.min_ms_cm == 1.0
        assert result.ec_recommendation.max_ms_cm == 2.0
        assert "default" in result.ec_recommendation.rationale.lower()


@pytest.mark.nutrient_optimization
class TestPHCalculation:
    """Test pH range calculation"""

    def test_ph_intersection_compatible_crops(self, nutrient_service, test_db, hydroponic_garden,
                                               tomato_variety_with_nutrients, lettuce_variety_with_nutrients, sample_user):
        """Test pH intersection for compatible crops (both 5.5-6.5)"""
        tomato_planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=30),
            planting_method=PlantingMethod.TRANSPLANT
        )
        lettuce_planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=lettuce_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=20),
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add_all([tomato_planting, lettuce_planting])
        test_db.commit()

        result = nutrient_service.optimize_for_garden(hydroponic_garden, test_db)

        assert result.ph_recommendation.min_ph == 5.5
        assert result.ph_recommendation.max_ph == 6.5
        assert "compatible" in result.ph_recommendation.rationale.lower()

    def test_ph_conflict_incompatible_crops(self, nutrient_service, test_db, hydroponic_garden, sample_user):
        """Test pH conflict warning for incompatible crops"""
        # Blueberry: 4.5-5.5 (acidic)
        blueberry = PlantVariety(
            common_name="Blueberry",
            days_to_harvest=90,
            optimal_ph_min=4.5,
            optimal_ph_max=5.5
        )
        # Asparagus: 6.5-7.5 (alkaline)
        asparagus = PlantVariety(
            common_name="Asparagus",
            days_to_harvest=365,
            optimal_ph_min=6.5,
            optimal_ph_max=7.5
        )
        test_db.add_all([blueberry, asparagus])
        test_db.commit()

        blueberry_planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=blueberry.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=30),
            planting_method=PlantingMethod.TRANSPLANT
        )
        asparagus_planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=asparagus.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=30),
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add_all([blueberry_planting, asparagus_planting])
        test_db.commit()

        result = nutrient_service.optimize_for_garden(hydroponic_garden, test_db)

        # Should use compromise range
        assert result.ph_recommendation.min_ph == 5.5
        assert result.ph_recommendation.max_ph == 6.5
        assert "conflict" in result.ph_recommendation.rationale.lower()


@pytest.mark.nutrient_optimization
class TestReplacementSchedule:
    """Test water replacement schedule calculation"""

    def test_small_reservoir_shorter_cycle(self, nutrient_service, test_db, sample_user, tomato_variety_with_nutrients):
        """Test small reservoir requires more frequent changes"""
        small_garden = Garden(
            user_id=sample_user.id,
            name="Small System",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.DWC,
            reservoir_size_liters=15.0  # Small
        )
        test_db.add(small_garden)
        test_db.commit()

        planting = PlantingEvent(
            garden_id=small_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=30),
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()

        result = nutrient_service.optimize_for_garden(small_garden, test_db)

        # Small reservoir should have shorter intervals
        assert result.replacement_schedule.full_replacement_days < 14
        assert result.replacement_schedule.topoff_interval_days == 1  # Always daily

    def test_large_reservoir_longer_cycle(self, nutrient_service, test_db, sample_user, tomato_variety_with_nutrients):
        """Test large reservoir allows longer intervals"""
        large_garden = Garden(
            user_id=sample_user.id,
            name="Large System",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.NFT,
            reservoir_size_liters=100.0  # Large
        )
        test_db.add(large_garden)
        test_db.commit()

        planting = PlantingEvent(
            garden_id=large_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=30),
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()

        result = nutrient_service.optimize_for_garden(large_garden, test_db)

        # Large reservoir should have longer intervals
        assert result.replacement_schedule.full_replacement_days >= 10


@pytest.mark.nutrient_optimization
class TestWarningDetection:
    """Test nutrient warning generation"""

    def test_no_plantings_warning(self, nutrient_service, test_db, hydroponic_garden):
        """Test warning when no active plantings"""
        result = nutrient_service.optimize_for_garden(hydroponic_garden, test_db)

        warning_ids = [w.warning_id for w in result.warnings]
        assert "NO_PLANTS" in warning_ids

    def test_small_reservoir_warning(self, nutrient_service, test_db, sample_user):
        """Test warning for very small reservoir (<10L)"""
        tiny_garden = Garden(
            user_id=sample_user.id,
            name="Tiny System",
            garden_type=GardenType.INDOOR,
            is_hydroponic=True,
            hydro_system_type=HydroSystemType.DWC,
            reservoir_size_liters=8.0  # Very small
        )
        test_db.add(tiny_garden)
        test_db.commit()

        result = nutrient_service.optimize_for_garden(tiny_garden, test_db)

        warning_ids = [w.warning_id for w in result.warnings]
        assert "SMALL_RESERVOIR" in warning_ids

        small_res_warning = next(w for w in result.warnings if w.warning_id == "SMALL_RESERVOIR")
        assert small_res_warning.severity == "warning"
        assert "8" in small_res_warning.message or "8.0" in small_res_warning.message

    def test_high_ec_warning(self, nutrient_service, test_db, hydroponic_garden, sample_user):
        """Test warning for very high EC (> 3.0)"""
        high_ec_variety = PlantVariety(
            common_name="Heavy Feeder",
            days_to_harvest=100,
            fruiting_ec_min=3.0,
            fruiting_ec_max=3.5,  # Very high EC
            optimal_ph_min=5.5,
            optimal_ph_max=6.5
        )
        test_db.add(high_ec_variety)
        test_db.commit()

        planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=high_ec_variety.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=95),  # Fruiting stage
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()

        result = nutrient_service.optimize_for_garden(hydroponic_garden, test_db)

        warning_ids = [w.warning_id for w in result.warnings]
        assert "HIGH_EC" in warning_ids


@pytest.mark.nutrient_optimization
class TestFullOptimization:
    """Test complete optimization flow"""

    def test_complete_optimization_result(self, nutrient_service, test_db, hydroponic_garden,
                                          tomato_variety_with_nutrients, sample_user):
        """Test complete optimization returns all expected fields"""
        planting = PlantingEvent(
            garden_id=hydroponic_garden.id,
            plant_variety_id=tomato_variety_with_nutrients.id,
            user_id=sample_user.id,
            planting_date=date.today() - timedelta(days=35),  # Vegetative
            planting_method=PlantingMethod.TRANSPLANT
        )
        test_db.add(planting)
        test_db.commit()

        result = nutrient_service.optimize_for_garden(hydroponic_garden, test_db)

        # Verify all fields present
        assert result.garden_id == hydroponic_garden.id
        assert result.garden_name == "Hydroponic Test Garden"
        assert result.system_type == "dwc"

        # EC recommendation
        assert result.ec_recommendation.min_ms_cm > 0
        assert result.ec_recommendation.max_ms_cm > result.ec_recommendation.min_ms_cm
        assert len(result.ec_recommendation.rationale) > 0

        # pH recommendation
        assert 4.0 <= result.ph_recommendation.min_ph <= 7.0
        assert result.ph_recommendation.max_ph > result.ph_recommendation.min_ph
        assert len(result.ph_recommendation.rationale) > 0

        # Replacement schedule
        assert result.replacement_schedule.topoff_interval_days > 0
        assert result.replacement_schedule.full_replacement_days > 0
        assert len(result.replacement_schedule.rationale) > 0

        # Active plantings
        assert len(result.active_plantings) == 1
        assert result.active_plantings[0]['plant_name'] == "Tomato"
        assert result.active_plantings[0]['growth_stage'] == "vegetative"

        # Generated timestamp
        assert result.generated_at is not None