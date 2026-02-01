"""Functional tests for sun path and seasonal shading

Tests end-to-end sun exposure calculation with database integration.
All tests marked with @pytest.mark.sun_path for easy filtering.
"""
import pytest
from sqlalchemy.orm import Session
from app.models.land import Land
from app.models.garden import Garden, GardenType
from app.models.tree import Tree
from app.services.sun_exposure_service import SunExposureService
from app.services.sun_exposure_rule_engine import SunExposureRuleEngine, RuleSeverity
from app.utils.sun_model import Season


pytestmark = pytest.mark.sun_path


class TestSunExposureService:
    """Test sun exposure service with database integration"""

    def test_garden_without_placement_returns_none(self, db: Session, test_user):
        """Garden not placed on land has no sun exposure data"""
        garden = Garden(
            user_id=test_user.id,
            name="Unplaced Garden",
            garden_type=GardenType.OUTDOOR
        )
        db.add(garden)
        db.commit()

        exposure = SunExposureService.get_garden_sun_exposure(garden, db)

        assert exposure["seasonal_exposure_score"] is None
        assert exposure["seasonal_shading"] is None
        assert "not placed" in exposure["warnings"][0].lower()

    def test_garden_with_no_trees_full_sun(self, db: Session, test_user):
        """Garden with no nearby trees has full sun exposure"""
        # Create land (latitude will default to 40.0 in service)
        land = Land(
            user_id=test_user.id,
            name="Sunny Land",
            width=100.0,
            height=100.0
        )
        db.add(land)
        db.flush()

        # Create garden on land
        garden = Garden(
            user_id=test_user.id,
            name="Sunny Garden",
            garden_type=GardenType.OUTDOOR,
            land_id=land.id,
            x=50.0,
            y=50.0,
            width=10.0,
            height=10.0
        )
        db.add(garden)
        db.commit()

        exposure = SunExposureService.get_garden_sun_exposure(garden, db)

        # Should have perfect sun exposure (score = 1.0)
        assert exposure["seasonal_exposure_score"] == 1.0
        assert exposure["exposure_category"] == "Full Sun"
        assert len(exposure["shading_sources"]) == 0

        # Check all seasons have 0% shading
        for season_name, season_data in exposure["seasonal_shading"].items():
            assert season_data["shaded_percentage"] == 0.0
            assert season_data["exposure_category"] == "Full Sun"

    def test_garden_with_tree_south_has_shading(self, db: Session, test_user):
        """Garden with tree to the south (NH) receives shading"""
        # Create land (will use default latitude 40.0 for Northern Hemisphere)
        land = Land(
            user_id=test_user.id,
            name="Test Land",
            width=100.0,
            height=100.0
        )
        db.add(land)
        db.flush()

        # Create garden
        garden = Garden(
            user_id=test_user.id,
            name="Shaded Garden",
            garden_type=GardenType.OUTDOOR,
            land_id=land.id,
            x=50.0,
            y=50.0,
            width=10.0,
            height=10.0
        )
        db.add(garden)
        db.flush()

        # Create tree to the south (lower Y) of garden
        tree = Tree(
            user_id=test_user.id,
            land_id=land.id,
            name="Oak Tree",
            x=50.0,
            y=30.0,  # South of garden (Y=50)
            height=15.0,
            canopy_radius=3.0
        )
        db.add(tree)
        db.commit()

        exposure = SunExposureService.get_garden_sun_exposure(garden, db)

        # Should have some shading
        assert exposure["seasonal_exposure_score"] < 1.0
        assert tree.id in exposure["shading_sources"]

        # Winter should have more shading than summer (longer shadows)
        winter_shading = exposure["seasonal_shading"]["winter"]["shaded_percentage"]
        summer_shading = exposure["seasonal_shading"]["summer"]["shaded_percentage"]
        assert winter_shading > 0  # Some shading in winter
        # Note: Summer may also have shading depending on shadow length

    def test_garden_with_tree_north_minimal_shading(self, db: Session, test_user):
        """Garden with tree to the north (NH) receives minimal/no shading"""
        # Create land in Northern Hemisphere
        land = Land(
            user_id=test_user.id,
            name="Test Land",
            width=100.0,
            height=100.0,
        )
        db.add(land)
        db.flush()

        # Create garden
        garden = Garden(
            user_id=test_user.id,
            name="Garden",
            garden_type=GardenType.OUTDOOR,
            land_id=land.id,
            x=50.0,
            y=50.0,
            width=10.0,
            height=10.0
        )
        db.add(garden)
        db.flush()

        # Create tree to the north (higher Y) of garden
        tree = Tree(
            user_id=test_user.id,
            land_id=land.id,
            name="Oak Tree",
            x=50.0,
            y=70.0,  # North of garden (Y=50)
            height=15.0,
            canopy_radius=3.0
        )
        db.add(tree)
        db.commit()

        exposure = SunExposureService.get_garden_sun_exposure(garden, db)

        # Should have minimal or no shading (shadow cast away from garden)
        assert exposure["seasonal_exposure_score"] > 0.9
        assert tree.id not in exposure["shading_sources"]

    def test_seasonal_variation_in_shading(self, db: Session, test_user):
        """Shading varies by season due to sun angle changes"""
        land = Land(
            user_id=test_user.id,
            name="Test Land",
            width=100.0,
            height=100.0,
        )
        db.add(land)
        db.flush()

        garden = Garden(
            user_id=test_user.id,
            name="Garden",
            garden_type=GardenType.OUTDOOR,
            land_id=land.id,
            x=50.0,
            y=50.0,
            width=10.0,
            height=10.0
        )
        db.add(garden)
        db.flush()

        # Tall tree to south
        tree = Tree(
            user_id=test_user.id,
            land_id=land.id,
            name="Tall Oak",
            x=50.0,
            y=25.0,
            height=20.0,
            canopy_radius=4.0
        )
        db.add(tree)
        db.commit()

        exposure = SunExposureService.get_garden_sun_exposure(garden, db)

        # Extract seasonal shading
        winter_shading = exposure["seasonal_shading"]["winter"]["shaded_percentage"]
        equinox_shading = exposure["seasonal_shading"]["equinox"]["shaded_percentage"]
        summer_shading = exposure["seasonal_shading"]["summer"]["shaded_percentage"]

        # Winter should have most shading (low sun angle = long shadows)
        assert winter_shading >= equinox_shading
        assert winter_shading >= summer_shading


class TestSunExposureRuleEngine:
    """Test rule engine for sun exposure warnings"""

    def test_full_sun_plant_in_shade_critical_warning(self):
        """Full sun plant in shade triggers critical warning"""
        exposure_data = {
            "garden_id": 1,
            "exposure_category": "Shade",
            "seasonal_shading": {
                "winter": {"shaded_percentage": 80.0, "affected_by_count": 1},
                "equinox": {"shaded_percentage": 75.0, "affected_by_count": 1},
                "summer": {"shaded_percentage": 70.0, "affected_by_count": 1}
            }
        }

        rules = SunExposureRuleEngine.evaluate_garden_sun_exposure(
            exposure_data,
            plant_sun_requirement="full_sun"
        )

        # Should trigger critical warning
        critical_rules = [r for r in rules if r.severity == RuleSeverity.CRITICAL]
        assert len(critical_rules) > 0
        assert any("full sun" in r.title.lower() for r in critical_rules)

    def test_shade_plant_in_full_sun_warning(self):
        """Shade plant in full sun triggers warning"""
        exposure_data = {
            "garden_id": 1,
            "exposure_category": "Full Sun",
            "seasonal_shading": {
                "winter": {"shaded_percentage": 10.0, "affected_by_count": 0},
                "equinox": {"shaded_percentage": 5.0, "affected_by_count": 0},
                "summer": {"shaded_percentage": 0.0, "affected_by_count": 0}
            }
        }

        rules = SunExposureRuleEngine.evaluate_garden_sun_exposure(
            exposure_data,
            plant_sun_requirement="shade"
        )

        # Should trigger warning about shade plant in sun
        warnings = [r for r in rules if r.severity == RuleSeverity.WARNING]
        assert len(warnings) > 0
        assert any("shade plant" in r.title.lower() for r in warnings)

    def test_high_seasonal_variability_warning(self):
        """High seasonal variability triggers warning"""
        exposure_data = {
            "garden_id": 1,
            "exposure_category": "Partial Sun",
            "seasonal_shading": {
                "winter": {"shaded_percentage": 90.0, "affected_by_count": 1},
                "equinox": {"shaded_percentage": 50.0, "affected_by_count": 1},
                "summer": {"shaded_percentage": 20.0, "affected_by_count": 1}
            }
        }

        rules = SunExposureRuleEngine.evaluate_garden_sun_exposure(
            exposure_data,
            plant_sun_requirement=None
        )

        # Should trigger variability warning
        assert any("variability" in r.title.lower() for r in rules)

    def test_tree_south_of_garden_warning(self):
        """Tree positioned south of garden triggers warning"""
        garden1 = {"id": 1, "x": 50.0, "y": 50.0}

        rules = SunExposureRuleEngine.evaluate_tree_placement(
            tree_x=50.0,
            tree_y=30.0,  # South of garden
            nearby_gardens=[garden1],
            tree_id=10,
            hemisphere="northern"
        )

        # Should warn about tree south of garden
        assert len(rules) > 0
        assert any("south" in r.title.lower() for r in rules)

    def test_tree_north_of_garden_no_warning(self):
        """Tree positioned north of garden (NH) does not trigger warning"""
        garden1 = {"id": 1, "x": 50.0, "y": 50.0}

        rules = SunExposureRuleEngine.evaluate_tree_placement(
            tree_x=50.0,
            tree_y=70.0,  # North of garden
            nearby_gardens=[garden1],
            tree_id=10,
            hemisphere="northern"
        )

        # Should not warn (shadows cast away from gardens)
        assert len(rules) == 0


class TestPlacementWarnings:
    """Test placement warnings during garden creation"""

    def test_placement_with_no_trees_no_warnings(self, db: Session, test_user):
        """Placing garden with no trees generates no warnings"""
        land = Land(
            user_id=test_user.id,
            name="Empty Land",
            width=100.0,
            height=100.0,
        )
        db.add(land)
        db.commit()

        warnings = SunExposureService.check_placement_warnings(
            garden_x=50.0,
            garden_y=50.0,
            garden_width=10.0,
            garden_height=10.0,
            land=land,
            db=db
        )

        assert len(warnings) == 0

    def test_placement_in_heavy_shade_generates_warning(self, db: Session, test_user):
        """Placing garden in heavily shaded area generates warning"""
        land = Land(
            user_id=test_user.id,
            name="Shaded Land",
            width=100.0,
            height=100.0,
        )
        db.add(land)
        db.flush()

        # Large tree to south
        tree = Tree(
            user_id=test_user.id,
            land_id=land.id,
            name="Huge Oak",
            x=50.0,
            y=30.0,
            height=25.0,
            canopy_radius=8.0
        )
        db.add(tree)
        db.commit()

        # Try to place garden close to tree shadow path
        warnings = SunExposureService.check_placement_warnings(
            garden_x=50.0,
            garden_y=55.0,
            garden_width=10.0,
            garden_height=10.0,
            land=land,
            db=db
        )

        # Should generate shading warnings
        assert len(warnings) > 0
        assert any("shad" in w.lower() for w in warnings)


class TestTreeShadowExtent:
    """Test tree shadow extent calculation"""

    def test_tree_shadow_extent_all_seasons(self, db: Session, test_user):
        """Tree shadow extent includes all seasons"""
        land = Land(
            user_id=test_user.id,
            name="Test Land",
            width=100.0,
            height=100.0,
        )
        db.add(land)
        db.flush()

        tree = Tree(
            user_id=test_user.id,
            land_id=land.id,
            name="Oak",
            x=50.0,
            y=50.0,
            height=15.0,
            canopy_radius=3.0
        )
        db.add(tree)
        db.commit()

        shadow_info = SunExposureService.get_tree_shadow_extent(tree, latitude=40.0)

        assert "seasonal_shadows" in shadow_info
        assert "max_shadow_length" in shadow_info
        assert shadow_info["max_shadow_length"] > 0

        # Should have shadows for all seasons
        assert "winter" in shadow_info["seasonal_shadows"]
        assert "equinox" in shadow_info["seasonal_shadows"]
        assert "summer" in shadow_info["seasonal_shadows"]

    def test_tree_without_placement_returns_none(self, db: Session, test_user):
        """Tree without complete coordinates has no shadow extent"""
        land = Land(
            user_id=test_user.id,
            name="Test Land",
            width=100.0,
            height=100.0,
        )
        db.add(land)
        db.flush()

        # Create tree without height (incomplete data for shadow calculation)
        tree = Tree(
            user_id=test_user.id,
            land_id=land.id,
            name="Tree Without Height",
            x=50.0,
            y=50.0,
            canopy_radius=3.0
            # height is None (not set)
        )
        db.add(tree)
        db.commit()

        # Shadow extent requires height, so should return None
        shadow_info = SunExposureService.get_tree_shadow_extent(tree, latitude=40.0)

        assert shadow_info["seasonal_shadows"] is None
        assert shadow_info["max_shadow_length"] is None


@pytest.fixture
def test_user(db: Session):
    """Create a test user"""
    from app.models.user import User
    from app.services.auth_service import AuthService

    user = User(
        email="sunpath_test@example.com",
        hashed_password=AuthService.hash_password("password123")
    )
    db.add(user)
    db.commit()
    return user
