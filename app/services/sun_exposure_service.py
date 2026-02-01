"""Sun exposure service for calculating garden sun exposure and shading sources

This service integrates the sun model and shadow projection to provide
high-level APIs for calculating garden sun exposure based on nearby trees.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.garden import Garden
from app.models.land import Land
from app.models.tree import Tree
from app.models.structure import Structure
from app.services.shadow_service import (
    calculate_seasonal_garden_shading,
    get_exposure_category,
    calculate_seasonal_exposure_score,
    project_tree_shadow,
    project_structure_shadow
)
from app.utils.sun_model import Season, DEFAULT_LATITUDE


class SunExposureService:
    """Service for calculating sun exposure and seasonal shading"""

    @staticmethod
    def get_garden_sun_exposure(garden: Garden, db: Session) -> Dict:
        """
        Calculate comprehensive sun exposure information for a garden.

        Args:
            garden: Garden model instance
            db: Database session

        Returns:
            Dictionary with:
            - seasonal_exposure_score: Overall score 0-1
            - seasonal_shading: Per-season shading percentages
            - exposure_category: Full Sun / Partial Sun / Shade
            - shading_sources: List of tree IDs casting shadows
            - warnings: List of warning messages
        """
        # Check if garden has spatial placement
        if garden.x is None or garden.y is None or garden.width is None or garden.height is None:
            return {
                "seasonal_exposure_score": None,
                "seasonal_shading": None,
                "exposure_category": None,
                "shading_sources": [],
                "warnings": ["Garden not placed on land"]
            }

        # Get land information
        if garden.land_id is None:
            return {
                "seasonal_exposure_score": None,
                "seasonal_shading": None,
                "exposure_category": None,
                "shading_sources": [],
                "warnings": ["Garden not assigned to land"]
            }

        land = db.query(Land).filter(Land.id == garden.land_id).first()
        if not land:
            return {
                "seasonal_exposure_score": None,
                "seasonal_shading": None,
                "exposure_category": None,
                "shading_sources": [],
                "warnings": ["Land not found"]
            }

        # Get latitude (use default if not set or attribute doesn't exist)
        latitude = getattr(land, 'latitude', None)
        if latitude is None:
            latitude = DEFAULT_LATITUDE

        # Get all trees on the same land
        trees = db.query(Tree).filter(
            Tree.land_id == garden.land_id,
            Tree.x.isnot(None),
            Tree.y.isnot(None),
            Tree.height.isnot(None),
            Tree.canopy_radius.isnot(None)
        ).all()

        # Convert trees to dict format
        tree_data = [
            {
                'id': tree.id,
                'x': tree.x,
                'y': tree.y,
                'height': tree.height,
                'canopy_radius': tree.canopy_radius
            }
            for tree in trees
        ]

        # Calculate seasonal shading
        seasonal_shading = calculate_seasonal_garden_shading(
            garden_x=garden.x,
            garden_y=garden.y,
            garden_width=garden.width,
            garden_height=garden.height,
            trees=tree_data,
            latitude=latitude
        )

        # Calculate overall exposure score
        exposure_score = calculate_seasonal_exposure_score(seasonal_shading)

        # Determine primary exposure category (use worst-case season)
        max_shading = max(
            info['shaded_percentage']
            for info in seasonal_shading.values()
        )
        exposure_category = get_exposure_category(max_shading)

        # Identify shading sources (trees that cast shadows on this garden)
        shading_sources = []
        for tree_dict in tree_data:
            # Check if tree casts shadow on garden in any season
            for season in Season:
                shadow = project_tree_shadow(
                    tree_x=tree_dict['x'],
                    tree_y=tree_dict['y'],
                    tree_height=tree_dict['height'],
                    canopy_radius=tree_dict['canopy_radius'],
                    latitude=latitude,
                    season=season
                )

                from app.services.shadow_service import ShadowRectangle
                garden_rect = ShadowRectangle(
                    garden.x, garden.y, garden.width, garden.height
                )

                if shadow.intersects(garden_rect):
                    if tree_dict['id'] not in shading_sources:
                        shading_sources.append(tree_dict['id'])
                    break

        # Generate warnings
        warnings = []
        if exposure_score < 0.4:
            warnings.append("Significant seasonal shading detected")
        if len(shading_sources) > 0:
            warnings.append(f"Shaded by {len(shading_sources)} tree(s)")

        # Convert seasonal shading to serializable format
        seasonal_shading_dict = {
            season.value: {
                "shaded_percentage": round(info['shaded_percentage'], 1),
                "exposure_category": get_exposure_category(info['shaded_percentage']),
                "affected_by_count": info['affected_by_count']
            }
            for season, info in seasonal_shading.items()
        }

        return {
            "seasonal_exposure_score": round(exposure_score, 2),
            "seasonal_shading": seasonal_shading_dict,
            "exposure_category": exposure_category,
            "shading_sources": shading_sources,
            "warnings": warnings
        }

    @staticmethod
    def get_tree_shadow_extent(tree: Tree, latitude: Optional[float] = None) -> Dict:
        """
        Calculate seasonal shadow extent for a tree.

        Args:
            tree: Tree model instance
            latitude: Optional latitude override

        Returns:
            Dictionary with seasonal shadow projections
        """
        if tree.x is None or tree.y is None or tree.height is None or tree.canopy_radius is None:
            return {
                "seasonal_shadows": None,
                "max_shadow_length": None
            }

        if latitude is None:
            latitude = DEFAULT_LATITUDE

        seasonal_shadows = {}
        max_shadow_length = 0.0

        for season in Season:
            shadow = project_tree_shadow(
                tree_x=tree.x,
                tree_y=tree.y,
                tree_height=tree.height,
                canopy_radius=tree.canopy_radius,
                latitude=latitude,
                season=season
            )

            shadow_dict = shadow.to_dict()
            seasonal_shadows[season.value] = shadow_dict

            # Track maximum shadow length
            shadow_length = max(shadow.width, shadow.height)
            max_shadow_length = max(max_shadow_length, shadow_length)

        return {
            "seasonal_shadows": seasonal_shadows,
            "max_shadow_length": round(max_shadow_length, 2)
        }

    @staticmethod
    def get_structure_shadow_extent(structure: Structure, latitude: Optional[float] = None) -> Dict:
        """
        Calculate seasonal shadow extent for a structure.

        Args:
            structure: Structure model instance
            latitude: Optional latitude override

        Returns:
            Dictionary with seasonal shadow projections
        """
        if structure.x is None or structure.y is None or structure.height is None or \
           structure.width is None or structure.depth is None:
            return {
                "seasonal_shadows": None,
                "max_shadow_length": None
            }

        if latitude is None:
            latitude = DEFAULT_LATITUDE

        seasonal_shadows = {}
        max_shadow_length = 0.0

        for season in Season:
            shadow = project_structure_shadow(
                structure_x=structure.x,
                structure_y=structure.y,
                structure_width=structure.width,
                structure_depth=structure.depth,
                structure_height=structure.height,
                latitude=latitude,
                season=season
            )

            shadow_dict = shadow.to_dict()
            seasonal_shadows[season.value] = shadow_dict

            # Track maximum shadow length
            shadow_length = max(shadow.width, shadow.height)
            max_shadow_length = max(max_shadow_length, shadow_length)

        return {
            "seasonal_shadows": seasonal_shadows,
            "max_shadow_length": round(max_shadow_length, 2)
        }

    @staticmethod
    def check_placement_warnings(
        garden_x: float,
        garden_y: float,
        garden_width: float,
        garden_height: float,
        land: Land,
        db: Session
    ) -> List[str]:
        """
        Check for sun exposure warnings when placing a garden.

        This is called during garden placement to provide soft warnings
        (does not block placement).

        Args:
            garden_x: Proposed garden x-coordinate
            garden_y: Proposed garden y-coordinate
            garden_width: Garden width
            garden_height: Garden height
            land: Land instance
            db: Database session

        Returns:
            List of warning messages
        """
        warnings = []

        # Get latitude (use default if not set or attribute doesn't exist)
        latitude = getattr(land, 'latitude', None)
        if latitude is None:
            latitude = DEFAULT_LATITUDE

        # Get all trees on land
        trees = db.query(Tree).filter(
            Tree.land_id == land.id,
            Tree.x.isnot(None),
            Tree.y.isnot(None),
            Tree.height.isnot(None),
            Tree.canopy_radius.isnot(None)
        ).all()

        if not trees:
            return warnings  # No trees, no shading concerns

        # Convert trees to dict format
        tree_data = [
            {
                'id': tree.id,
                'x': tree.x,
                'y': tree.y,
                'height': tree.height,
                'canopy_radius': tree.canopy_radius
            }
            for tree in trees
        ]

        # Calculate seasonal shading
        seasonal_shading = calculate_seasonal_garden_shading(
            garden_x=garden_x,
            garden_y=garden_y,
            garden_width=garden_width,
            garden_height=garden_height,
            trees=tree_data,
            latitude=latitude
        )

        # Check for significant shading
        for season, info in seasonal_shading.items():
            if info['shaded_percentage'] > 60:
                warnings.append(
                    f"High shading during {season.value} ({info['shaded_percentage']:.0f}% shaded)"
                )
            elif info['shaded_percentage'] > 25:
                warnings.append(
                    f"Partial shading during {season.value} ({info['shaded_percentage']:.0f}% shaded)"
                )

        return warnings
