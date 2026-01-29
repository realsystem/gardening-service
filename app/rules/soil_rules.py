"""
Soil science-based recommendation engine.

Provides actionable, numeric advice for soil amendments based on:
- Current soil chemistry (pH, N, P, K, organic matter, moisture)
- Plant-specific requirements
- Scientific best practices for soil management
"""

from typing import List, Optional, Dict
from app.schemas.soil_sample import SoilRecommendation
from app.models.soil_sample import SoilSample
from app.models.plant_variety import PlantVariety


# Plant-specific optimal soil ranges (based on agricultural research)
PLANT_SOIL_REQUIREMENTS = {
    # Vegetables
    "tomato": {"ph_min": 6.0, "ph_max": 6.8, "n_min": 20, "n_max": 50, "p_min": 25, "p_max": 75, "k_min": 150, "k_max": 250},
    "lettuce": {"ph_min": 6.0, "ph_max": 7.0, "n_min": 30, "n_max": 60, "p_min": 20, "p_max": 60, "k_min": 120, "k_max": 200},
    "carrot": {"ph_min": 5.5, "ph_max": 7.0, "n_min": 15, "n_max": 40, "p_min": 30, "p_max": 80, "k_min": 140, "k_max": 220},
    "pepper": {"ph_min": 6.0, "ph_max": 7.0, "n_min": 20, "n_max": 50, "p_min": 25, "p_max": 75, "k_min": 150, "k_max": 250},
    "cucumber": {"ph_min": 5.5, "ph_max": 7.0, "n_min": 25, "n_max": 55, "p_min": 30, "p_max": 70, "k_min": 140, "k_max": 230},
    "broccoli": {"ph_min": 6.0, "ph_max": 7.5, "n_min": 30, "n_max": 70, "p_min": 25, "p_max": 75, "k_min": 150, "k_max": 250},
    "spinach": {"ph_min": 6.5, "ph_max": 7.5, "n_min": 30, "n_max": 65, "p_min": 20, "p_max": 60, "k_min": 140, "k_max": 220},
    "basil": {"ph_min": 6.0, "ph_max": 7.5, "n_min": 25, "n_max": 55, "p_min": 20, "p_max": 60, "k_min": 120, "k_max": 200},

    # Default for unknown plants
    "default": {"ph_min": 6.0, "ph_max": 7.0, "n_min": 20, "n_max": 60, "p_min": 25, "p_max": 75, "k_min": 120, "k_max": 250},
}


def get_plant_requirements(plant_name: Optional[str]) -> Dict[str, float]:
    """Get soil requirements for a specific plant."""
    if not plant_name:
        return PLANT_SOIL_REQUIREMENTS["default"]

    # Normalize plant name (lowercase, first word only)
    plant_key = plant_name.lower().split()[0]
    return PLANT_SOIL_REQUIREMENTS.get(plant_key, PLANT_SOIL_REQUIREMENTS["default"])


def generate_soil_recommendations(
    soil_sample: SoilSample,
    plant_variety: Optional[PlantVariety] = None
) -> List[SoilRecommendation]:
    """
    Generate actionable soil recommendations based on sample data and plant requirements.

    Returns:
        List of specific, numeric recommendations for soil amendments.
    """
    recommendations = []

    # Get plant-specific requirements
    plant_name = plant_variety.plant_name if plant_variety else None
    requirements = get_plant_requirements(plant_name)

    # pH Recommendations
    recommendations.append(_analyze_ph(soil_sample.ph, requirements, plant_name))

    # Nitrogen recommendations
    if soil_sample.nitrogen_ppm is not None:
        recommendations.append(_analyze_nitrogen(soil_sample.nitrogen_ppm, requirements, plant_name))

    # Phosphorus recommendations
    if soil_sample.phosphorus_ppm is not None:
        recommendations.append(_analyze_phosphorus(soil_sample.phosphorus_ppm, requirements, plant_name))

    # Potassium recommendations
    if soil_sample.potassium_ppm is not None:
        recommendations.append(_analyze_potassium(soil_sample.potassium_ppm, requirements, plant_name))

    # Organic matter recommendations
    if soil_sample.organic_matter_percent is not None:
        recommendations.append(_analyze_organic_matter(soil_sample.organic_matter_percent))

    # Moisture recommendations
    if soil_sample.moisture_percent is not None:
        recommendations.append(_analyze_moisture(soil_sample.moisture_percent, plant_name))

    return [rec for rec in recommendations if rec is not None]


def _analyze_ph(ph: float, requirements: Dict, plant_name: Optional[str]) -> SoilRecommendation:
    """Analyze pH and provide specific amendment recommendations."""
    ph_min, ph_max = requirements["ph_min"], requirements["ph_max"]
    optimal_range = f"{ph_min:.1f} - {ph_max:.1f}"
    plant_desc = f" for {plant_name}" if plant_name else ""

    if ph < ph_min - 1.0:
        # Severely acidic
        ph_increase = ph_min - ph
        lime_lbs_per_100sqft = ph_increase * 5  # Approximate: 5 lbs lime per pH unit per 100 sq ft
        return SoilRecommendation(
            parameter="pH",
            current_value=ph,
            optimal_range=optimal_range,
            status="critical",
            recommendation=f"Soil is severely acidic{plant_desc}. Add approximately {lime_lbs_per_100sqft:.1f} lbs of garden lime per 100 sq ft to raise pH to {ph_min:.1f}. Apply in fall or early spring, mix into top 6 inches of soil.",
            priority="critical"
        )
    elif ph < ph_min:
        # Moderately acidic
        ph_increase = ph_min - ph
        lime_lbs_per_100sqft = ph_increase * 5
        return SoilRecommendation(
            parameter="pH",
            current_value=ph,
            optimal_range=optimal_range,
            status="low",
            recommendation=f"Soil is slightly acidic{plant_desc}. Add {lime_lbs_per_100sqft:.1f} lbs of dolomitic lime per 100 sq ft. Wood ash (2-3 lbs per 100 sq ft) is also effective.",
            priority="high"
        )
    elif ph > ph_max + 1.0:
        # Severely alkaline
        ph_decrease = ph - ph_max
        sulfur_lbs_per_100sqft = ph_decrease * 1.5  # Approximate: 1.5 lbs sulfur per pH unit per 100 sq ft
        return SoilRecommendation(
            parameter="pH",
            current_value=ph,
            optimal_range=optimal_range,
            status="critical",
            recommendation=f"Soil is severely alkaline{plant_desc}. Add {sulfur_lbs_per_100sqft:.1f} lbs of elemental sulfur per 100 sq ft to lower pH to {ph_max:.1f}. Alternatively, add 15-20 lbs of sulfate-based fertilizer or 3-4 inches of peat moss worked into soil.",
            priority="critical"
        )
    elif ph > ph_max:
        # Moderately alkaline
        return SoilRecommendation(
            parameter="pH",
            current_value=ph,
            optimal_range=optimal_range,
            status="high",
            recommendation=f"Soil is slightly alkaline{plant_desc}. Add sulfur (1-2 lbs per 100 sq ft) or organic matter like compost (2-3 inches worked in). Coffee grounds and pine needles also help acidify soil gradually.",
            priority="medium"
        )
    else:
        # Optimal
        return SoilRecommendation(
            parameter="pH",
            current_value=ph,
            optimal_range=optimal_range,
            status="optimal",
            recommendation=f"pH is optimal{plant_desc}. Maintain current levels with regular compost additions.",
            priority="low"
        )


def _analyze_nitrogen(n_ppm: float, requirements: Dict, plant_name: Optional[str]) -> SoilRecommendation:
    """Analyze nitrogen levels and provide fertilizer recommendations."""
    n_min, n_max = requirements["n_min"], requirements["n_max"]
    optimal_range = f"{n_min:.0f} - {n_max:.0f} ppm"
    plant_desc = f" for {plant_name}" if plant_name else ""

    if n_ppm < n_min * 0.5:
        # Severely deficient
        deficit = n_min - n_ppm
        compost_inches = max(2, deficit / 10)
        return SoilRecommendation(
            parameter="Nitrogen",
            current_value=n_ppm,
            optimal_range=optimal_range,
            status="critical",
            recommendation=f"Nitrogen is severely deficient{plant_desc}. Apply {compost_inches:.0f} inches of aged compost or manure, or use blood meal (12-0-0) at 3 lbs per 100 sq ft. Side-dress with fish emulsion (5-1-1) every 2 weeks during growing season.",
            priority="critical"
        )
    elif n_ppm < n_min:
        # Low
        return SoilRecommendation(
            parameter="Nitrogen",
            current_value=n_ppm,
            optimal_range=optimal_range,
            status="low",
            recommendation=f"Nitrogen is low{plant_desc}. Add 2 inches of compost, or apply alfalfa meal (3-0-2) at 2 lbs per 100 sq ft. Plant nitrogen-fixing cover crops (clover, peas) between seasons.",
            priority="high"
        )
    elif n_ppm > n_max * 1.5:
        # Excessive
        return SoilRecommendation(
            parameter="Nitrogen",
            current_value=n_ppm,
            optimal_range=optimal_range,
            status="high",
            recommendation=f"Nitrogen is excessive{plant_desc}. Avoid nitrogen fertilizers. Plant heavy nitrogen feeders (corn, brassicas) to use excess. Water deeply to leach some nitrogen below root zone.",
            priority="medium"
        )
    elif n_ppm > n_max:
        # Slightly high
        return SoilRecommendation(
            parameter="Nitrogen",
            current_value=n_ppm,
            optimal_range=optimal_range,
            status="high",
            recommendation=f"Nitrogen is slightly elevated{plant_desc}. Skip nitrogen fertilizers this season. Monitor plants for excessive leafy growth at expense of fruit.",
            priority="low"
        )
    else:
        # Optimal
        return SoilRecommendation(
            parameter="Nitrogen",
            current_value=n_ppm,
            optimal_range=optimal_range,
            status="optimal",
            recommendation=f"Nitrogen is optimal{plant_desc}. Maintain with 1-2 inches of compost annually.",
            priority="low"
        )


def _analyze_phosphorus(p_ppm: float, requirements: Dict, plant_name: Optional[str]) -> SoilRecommendation:
    """Analyze phosphorus levels and provide amendment recommendations."""
    p_min, p_max = requirements["p_min"], requirements["p_max"]
    optimal_range = f"{p_min:.0f} - {p_max:.0f} ppm"
    plant_desc = f" for {plant_name}" if plant_name else ""

    if p_ppm < p_min * 0.5:
        # Severely deficient
        return SoilRecommendation(
            parameter="Phosphorus",
            current_value=p_ppm,
            optimal_range=optimal_range,
            status="critical",
            recommendation=f"Phosphorus is severely deficient{plant_desc}. Add bone meal (3-15-0) at 3-4 lbs per 100 sq ft, or rock phosphate (0-3-0) at 5 lbs per 100 sq ft. Mix into top 6 inches of soil in fall for best results.",
            priority="critical"
        )
    elif p_ppm < p_min:
        # Low
        return SoilRecommendation(
            parameter="Phosphorus",
            current_value=p_ppm,
            optimal_range=optimal_range,
            status="low",
            recommendation=f"Phosphorus is low{plant_desc}. Apply bone meal (2 lbs per 100 sq ft) or fish bone meal (4-12-0) at planting. Work into root zone for best uptake.",
            priority="high"
        )
    elif p_ppm > p_max * 1.5:
        # Excessive
        return SoilRecommendation(
            parameter="Phosphorus",
            current_value=p_ppm,
            optimal_range=optimal_range,
            status="high",
            recommendation=f"Phosphorus is excessive{plant_desc}. Avoid all phosphorus fertilizers. Excess phosphorus can interfere with iron and zinc uptake. Plant phosphorus-loving crops (legumes, root vegetables).",
            priority="medium"
        )
    elif p_ppm > p_max:
        # Slightly high
        return SoilRecommendation(
            parameter="Phosphorus",
            current_value=p_ppm,
            optimal_range=optimal_range,
            status="high",
            recommendation=f"Phosphorus is adequate to high{plant_desc}. No phosphorus fertilizers needed this season.",
            priority="low"
        )
    else:
        # Optimal
        return SoilRecommendation(
            parameter="Phosphorus",
            current_value=p_ppm,
            optimal_range=optimal_range,
            status="optimal",
            recommendation=f"Phosphorus is optimal{plant_desc}. Maintain with occasional bone meal applications.",
            priority="low"
        )


def _analyze_potassium(k_ppm: float, requirements: Dict, plant_name: Optional[str]) -> SoilRecommendation:
    """Analyze potassium levels and provide amendment recommendations."""
    k_min, k_max = requirements["k_min"], requirements["k_max"]
    optimal_range = f"{k_min:.0f} - {k_max:.0f} ppm"
    plant_desc = f" for {plant_name}" if plant_name else ""

    if k_ppm < k_min * 0.5:
        # Severely deficient
        return SoilRecommendation(
            parameter="Potassium",
            current_value=k_ppm,
            optimal_range=optimal_range,
            status="critical",
            recommendation=f"Potassium is severely deficient{plant_desc}. Add greensand (0-0-3) at 5-10 lbs per 100 sq ft, or sulfate of potash (0-0-50) at 1-2 lbs per 100 sq ft. Wood ash is also excellent (0-0-8) at 2-3 lbs per 100 sq ft, but avoid if soil pH is already high.",
            priority="critical"
        )
    elif k_ppm < k_min:
        # Low
        return SoilRecommendation(
            parameter="Potassium",
            current_value=k_ppm,
            optimal_range=optimal_range,
            status="low",
            recommendation=f"Potassium is low{plant_desc}. Apply kelp meal (1-0-2) at 2 lbs per 100 sq ft, or granite dust (0-0-4) at 5 lbs per 100 sq ft. Banana peels and comfrey leaves are also potassium-rich amendments.",
            priority="high"
        )
    elif k_ppm > k_max * 1.5:
        # Excessive
        return SoilRecommendation(
            parameter="Potassium",
            current_value=k_ppm,
            optimal_range=optimal_range,
            status="high",
            recommendation=f"Potassium is excessive{plant_desc}. Avoid potassium fertilizers. High potassium can interfere with magnesium and calcium uptake. Deep watering may help leach excess.",
            priority="medium"
        )
    elif k_ppm > k_max:
        # Slightly high
        return SoilRecommendation(
            parameter="Potassium",
            current_value=k_ppm,
            optimal_range=optimal_range,
            status="high",
            recommendation=f"Potassium is adequate{plant_desc}. No additional potassium fertilizers needed.",
            priority="low"
        )
    else:
        # Optimal
        return SoilRecommendation(
            parameter="Potassium",
            current_value=k_ppm,
            optimal_range=optimal_range,
            status="optimal",
            recommendation=f"Potassium is optimal{plant_desc}. Maintain with compost and occasional kelp meal.",
            priority="low"
        )


def _analyze_organic_matter(om_percent: float) -> SoilRecommendation:
    """Analyze organic matter content."""
    optimal_range = "3.0 - 6.0%"

    if om_percent < 2.0:
        # Low
        compost_inches = 4 - om_percent
        return SoilRecommendation(
            parameter="Organic Matter",
            current_value=om_percent,
            optimal_range=optimal_range,
            status="low",
            recommendation=f"Organic matter is low. Add {compost_inches:.0f}-4 inches of aged compost or well-rotted manure. Work into top 6-8 inches of soil. Plant cover crops (clover, rye) in off-season and till in before planting.",
            priority="high"
        )
    elif om_percent > 8.0:
        # Too high (rare but possible)
        return SoilRecommendation(
            parameter="Organic Matter",
            current_value=om_percent,
            optimal_range=optimal_range,
            status="high",
            recommendation=f"Organic matter is very high. This is usually beneficial but may indicate excess nitrogen. Skip compost additions this year. Ensure good drainage to prevent waterlogging.",
            priority="low"
        )
    else:
        # Optimal
        return SoilRecommendation(
            parameter="Organic Matter",
            current_value=om_percent,
            optimal_range=optimal_range,
            status="optimal",
            recommendation=f"Organic matter is excellent. Maintain with 1-2 inches of compost annually and mulching.",
            priority="low"
        )


def _analyze_moisture(moisture_percent: float, plant_name: Optional[str]) -> SoilRecommendation:
    """Analyze soil moisture levels."""
    optimal_range = "20 - 60% (field capacity)"
    plant_desc = f" for {plant_name}" if plant_name else ""

    if moisture_percent < 15:
        # Very dry
        return SoilRecommendation(
            parameter="Soil Moisture",
            current_value=moisture_percent,
            optimal_range=optimal_range,
            status="critical",
            recommendation=f"Soil is very dry{plant_desc}. Water immediately and deeply (1-2 inches). Add 2-3 inches of organic mulch to retain moisture. Consider drip irrigation for consistent moisture.",
            priority="critical"
        )
    elif moisture_percent < 20:
        # Dry
        return SoilRecommendation(
            parameter="Soil Moisture",
            current_value=moisture_percent,
            optimal_range=optimal_range,
            status="low",
            recommendation=f"Soil is dry{plant_desc}. Increase watering frequency. Apply mulch to reduce evaporation.",
            priority="high"
        )
    elif moisture_percent > 70:
        # Waterlogged
        return SoilRecommendation(
            parameter="Soil Moisture",
            current_value=moisture_percent,
            optimal_range=optimal_range,
            status="critical",
            recommendation=f"Soil is waterlogged{plant_desc}. Risk of root rot. Stop watering immediately. Improve drainage by adding organic matter (compost, peat moss) and creating raised beds. Consider installing drainage tiles.",
            priority="critical"
        )
    elif moisture_percent > 60:
        # Too wet
        return SoilRecommendation(
            parameter="Soil Moisture",
            current_value=moisture_percent,
            optimal_range=optimal_range,
            status="high",
            recommendation=f"Soil moisture is high{plant_desc}. Reduce watering frequency. Ensure good drainage. Monitor for signs of overwatering (yellowing leaves, wilting despite wet soil).",
            priority="medium"
        )
    else:
        # Optimal
        return SoilRecommendation(
            parameter="Soil Moisture",
            current_value=moisture_percent,
            optimal_range=optimal_range,
            status="optimal",
            recommendation=f"Soil moisture is optimal{plant_desc}. Maintain current watering schedule.",
            priority="low"
        )
