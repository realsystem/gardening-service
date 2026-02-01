"""Companion Planting Relationship Model - Science-Based Plant Interactions"""
from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, Float, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RelationshipType(str, enum.Enum):
    """
    Type of companion planting relationship.

    Based on documented agronomic interactions:
    - BENEFICIAL: Proven positive effects (pest deterrence, growth enhancement, yield improvement)
    - NEUTRAL: No documented interaction
    - ANTAGONISTIC: Proven negative effects (growth inhibition, disease susceptibility, nutrient competition)
    """
    BENEFICIAL = "beneficial"
    NEUTRAL = "neutral"
    ANTAGONISTIC = "antagonistic"


class ConfidenceLevel(str, enum.Enum):
    """
    Confidence level of the relationship based on scientific evidence.

    - HIGH: Multiple peer-reviewed studies or extensive agricultural practice documentation
    - MEDIUM: Single peer-reviewed study or well-documented traditional practice with consistent results
    - LOW: Anecdotal evidence or limited documentation
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CompanionRelationship(Base):
    """
    Bidirectional plant-to-plant companion planting relationships.

    Each relationship must be:
    1. Science-based with documented source
    2. Explainable with specific mechanism
    3. Bidirectional (A→B implies B→A)
    4. Normalized (plant_a_id < plant_b_id to avoid duplicates)

    Example:
        Tomato + Basil (beneficial):
        - Mechanism: Basil repels aphids and whiteflies via aromatic oils
        - Source: Journal of Chemical Ecology, 2003
        - Confidence: HIGH
    """
    __tablename__ = "companion_relationships"

    id = Column(Integer, primary_key=True, index=True)

    # Normalized plant pair (plant_a_id < plant_b_id enforced at application level)
    plant_a_id = Column(Integer, nullable=False, index=True)  # ForeignKey to plant_varieties.id
    plant_b_id = Column(Integer, nullable=False, index=True)  # ForeignKey to plant_varieties.id

    # Relationship classification
    relationship_type = Column(
        SQLEnum(RelationshipType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True
    )

    # Scientific basis
    mechanism = Column(Text, nullable=False)  # e.g., "pest deterrence via aromatic compounds"
    confidence_level = Column(
        SQLEnum(ConfidenceLevel, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    # Distance parameters (in meters)
    effective_distance_m = Column(Float, nullable=False, default=1.0)  # Maximum distance for effect
    optimal_distance_m = Column(Float, nullable=True)  # Optimal distance (null = any distance within effective range)

    # Documentation
    source_reference = Column(Text, nullable=False)  # Scientific source or agricultural extension publication
    notes = Column(Text, nullable=True)  # Additional context or conditions

    # Constraints
    __table_args__ = (
        # Ensure uniqueness of plant pairs (normalized)
        UniqueConstraint('plant_a_id', 'plant_b_id', name='unique_plant_pair'),
        # Composite index for fast lookups
        Index('idx_companion_plants', 'plant_a_id', 'plant_b_id'),
        # Index for relationship type queries
        Index('idx_relationship_type', 'relationship_type'),
    )

    def __repr__(self):
        return f"<CompanionRelationship(plant_a_id={self.plant_a_id}, plant_b_id={self.plant_b_id}, type={self.relationship_type.value})>"
