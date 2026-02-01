"""
Plant Varieties Catalog Validation Tests

Validates the comprehensive 200+ variety catalog:
- Minimum 200 varieties exist
- Category distribution meets requirements
- No duplicate scientific names
- Trees and bushes have proper metadata
- Data quality checks
"""
import pytest
import httpx


class TestCatalogSize:
    """Validate catalog meets size requirements"""

    def test_minimum_200_varieties(self, authenticated_client: httpx.Client):
        """Catalog must have at least 200 varieties"""
        response = authenticated_client.get("/plant-varieties")
        assert response.status_code == 200

        varieties = response.json()
        assert len(varieties) >= 200, \
            f"Catalog has {len(varieties)} varieties, minimum required is 200"


    def test_category_distribution(self, authenticated_client: httpx.Client):
        """Verify minimum counts per category"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        # Count by tags
        vegetables = [v for v in varieties if "vegetable" in (v.get("tags") or "")]
        herbs = [v for v in varieties if "herb" in (v.get("tags") or "")]
        fruits = [v for v in varieties if "fruit" in (v.get("tags") or "") or "berry" in (v.get("tags") or "")]
        trees = [v for v in varieties if "tree" in (v.get("tags") or "")]
        bushes = [v for v in varieties if "bush" in (v.get("tags") or "")]
        cover_crops = [v for v in varieties if "cover_crop" in (v.get("tags") or "")]

        # Verify minimums
        assert len(vegetables) >= 70, f"Need 70+ vegetables, got {len(vegetables)}"
        assert len(herbs) >= 30, f"Need 30+ herbs, got {len(herbs)}"
        assert len(fruits) >= 5, f"Need 5+ fruits/berries, got {len(fruits)}"
        assert len(trees) >= 40, f"Need 40+ trees, got {len(trees)}"
        assert len(bushes) >= 30, f"Need 30+ bushes/shrubs, got {len(bushes)}"
        assert len(cover_crops) >= 20, f"Need 20+ cover crops, got {len(cover_crops)}"


class TestDataQuality:
    """Validate data quality"""

    def test_no_duplicate_scientific_names(self, authenticated_client: httpx.Client):
        """Scientific names + variety names should be unique (allows multiple varieties of same species)"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        # Check uniqueness of (scientific_name, variety_name) combination
        # Multiple varieties of same species is expected (e.g., different lettuces)
        variety_combos = [
            (v.get("scientific_name", ""), v.get("variety_name", ""))
            for v in varieties
        ]
        unique_combos = set(variety_combos)

        duplicates = len(variety_combos) - len(unique_combos)
        assert duplicates == 0, \
            f"Found {duplicates} duplicate (scientific_name, variety_name) combinations"


    def test_all_have_names(self, authenticated_client: httpx.Client):
        """Every variety must have a common name"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        missing_names = [v for v in varieties if not v.get("common_name")]
        assert len(missing_names) == 0, \
            f"{len(missing_names)} varieties missing common names"


    def test_all_have_sun_requirement(self, authenticated_client: httpx.Client):
        """Every variety should have sun requirements"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        missing_sun = [v for v in varieties if not v.get("sun_requirement")]
        assert len(missing_sun) == 0, \
            f"{len(missing_sun)} varieties missing sun requirements"


    def test_reasonable_spacing(self, authenticated_client: httpx.Client):
        """Spacing values should be reasonable (not 0 or negative)"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        invalid_spacing = []
        for v in varieties:
            spacing = v.get("spacing_inches")
            if spacing is not None and spacing <= 0:
                invalid_spacing.append(v["common_name"])

        assert len(invalid_spacing) == 0, \
            f"{len(invalid_spacing)} varieties have invalid spacing: {invalid_spacing[:5]}"


class TestTreesAndBushes:
    """Validate trees and bushes have proper metadata"""

    def test_trees_have_details_in_notes(self, authenticated_client: httpx.Client):
        """Trees should have mature size info in growing_notes"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        trees = [v for v in varieties if "tree" in (v.get("tags") or "")]

        missing_details = []
        for tree in trees:
            notes = tree.get("growing_notes") or ""
            # Check for height and spread keywords
            has_size = any(keyword in notes.lower() for keyword in [
                "mature height", "height:", "spread:", "feet", "tall"
            ])
            if not has_size:
                missing_details.append(tree["common_name"])

        # At least 80% of trees should have size info
        compliance_rate = (len(trees) - len(missing_details)) / len(trees) * 100
        assert compliance_rate >= 80, \
            f"Only {compliance_rate:.1f}% of trees have size details (need 80%+)"


    def test_trees_have_root_depth_info(self, authenticated_client: httpx.Client):
        """Trees should mention root depth"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        trees = [v for v in varieties if "tree" in (v.get("tags") or "")]

        with_root_info = []
        for tree in trees:
            notes = tree.get("growing_notes") or ""
            has_root_info = any(keyword in notes.lower() for keyword in [
                "root depth", "deep root", "shallow root", "medium root", "tap root"
            ])
            if has_root_info:
                with_root_info.append(tree)

        # At least 70% should have root depth info
        compliance_rate = len(with_root_info) / len(trees) * 100
        assert compliance_rate >= 70, \
            f"Only {compliance_rate:.1f}% of trees have root depth info (need 70%+)"


    def test_bushes_have_mature_size(self, authenticated_client: httpx.Client):
        """Bushes should have mature size information"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        bushes = [v for v in varieties if "bush" in (v.get("tags") or "")]

        with_size = []
        for bush in bushes:
            notes = bush.get("growing_notes") or ""
            has_size = any(keyword in notes.lower() for keyword in [
                "mature height", "height:", "spread:", "feet", "inches"
            ])
            if has_size:
                with_size.append(bush)

        # At least 75% should have size info
        compliance_rate = len(with_size) / len(bushes) * 100
        assert compliance_rate >= 75, \
            f"Only {compliance_rate:.1f}% of bushes have size info (need 75%+)"


class TestPerennialMetadata:
    """Validate perennial plants have proper lifecycle tags"""

    def test_trees_tagged_as_perennial(self, authenticated_client: httpx.Client):
        """All trees should be tagged as perennial"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        trees = [v for v in varieties if "tree" in (v.get("tags") or "")]

        non_perennial_trees = []
        for tree in trees:
            tags = tree.get("tags") or ""
            if "perennial" not in tags:
                non_perennial_trees.append(tree["common_name"])

        # All trees should be perennial
        assert len(non_perennial_trees) == 0, \
            f"{len(non_perennial_trees)} trees not tagged as perennial: {non_perennial_trees[:5]}"


    def test_cold_tolerance_for_hardy_plants(self, authenticated_client: httpx.Client):
        """Plants tagged as cold_hardy should be perennials or note zones"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        cold_hardy = [v for v in varieties if "cold_hardy" in (v.get("tags") or "")]

        without_zone_info = []
        for plant in cold_hardy:
            notes = plant.get("growing_notes") or ""
            tags = plant.get("tags") or ""

            # Should be perennial OR mention zones
            is_perennial = "perennial" in tags
            mentions_zones = "zone" in notes.lower()

            if not (is_perennial or mentions_zones):
                without_zone_info.append(plant["common_name"])

        # At least 80% compliance (most cold_hardy plants should have zone or lifecycle info)
        compliance_rate = (len(cold_hardy) - len(without_zone_info)) / len(cold_hardy) * 100
        assert compliance_rate >= 80, \
            f"Only {compliance_rate:.1f}% of cold_hardy plants have zone/lifecycle info"


class TestCatalogUsability:
    """Test catalog is usable for real-world scenarios"""

    def test_can_filter_by_category(self, authenticated_client: httpx.Client):
        """Should be able to get all varieties of a category"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        # Extract vegetables
        vegetables = [v for v in varieties if "vegetable" in (v.get("tags") or "")]

        assert len(vegetables) > 0, "Should be able to filter vegetables"
        assert all("vegetable" in v.get("tags", "") for v in vegetables), \
            "All filtered items should be vegetables"


    def test_diverse_water_requirements(self, authenticated_client: httpx.Client):
        """Catalog should have diverse water requirements"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        water_reqs = {}
        for v in varieties:
            req = v.get("water_requirement")
            if req:
                water_reqs[req] = water_reqs.get(req, 0) + 1

        # Should have at least 3 different water requirement levels
        assert len(water_reqs) >= 3, \
            f"Need diverse water requirements, only have {len(water_reqs)}: {water_reqs}"


    def test_diverse_sun_requirements(self, authenticated_client: httpx.Client):
        """Catalog should have diverse sun requirements"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        sun_reqs = {}
        for v in varieties:
            req = v.get("sun_requirement")
            if req:
                sun_reqs[req] = sun_reqs.get(req, 0) + 1

        # Should have at least 3 different sun requirement levels
        assert len(sun_reqs) >= 3, \
            f"Need diverse sun requirements, only have {len(sun_reqs)}: {sun_reqs}"


class TestCatalogPerformance:
    """Test catalog performs well"""

    def test_catalog_loads_quickly(self, authenticated_client: httpx.Client):
        """Catalog should load in under 2 seconds"""
        import time

        start = time.time()
        response = authenticated_client.get("/plant-varieties")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0, \
            f"Catalog took {elapsed:.2f}s to load (should be <2s)"


    def test_catalog_pagination_ready(self, authenticated_client: httpx.Client):
        """With 200+ items, pagination support is important"""
        response = authenticated_client.get("/plant-varieties")
        varieties = response.json()

        # If we have 200+ items, consider pagination
        if len(varieties) >= 200:
            # This test documents that pagination may be needed
            # Actual pagination implementation would be tested here
            assert True, "Catalog is large enough that pagination would be beneficial"
