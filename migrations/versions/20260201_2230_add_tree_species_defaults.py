"""Add tree species default dimensions to plant_varieties

Revision ID: u7v8w9x0y1z2
Revises: t1u2v3w4x5y6
Create Date: 2026-02-01 22:30:00.000000

Phase 4: Tree Modeling Refactor - Add tree-specific fields to plant_varieties
to enable automatic calculation of tree dimensions from species.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'u7v8w9x0y1z2'
down_revision = 't1u2v3w4x5y6'
branch_labels = None
depends_on = None


def upgrade():
    """Add tree-specific dimension fields to plant_varieties"""

    # Add tree dimension fields
    op.add_column('plant_varieties',
        sa.Column('is_tree', sa.Boolean(), server_default='false', nullable=False))

    op.add_column('plant_varieties',
        sa.Column('typical_height_ft', sa.Float(), nullable=True))

    op.add_column('plant_varieties',
        sa.Column('typical_canopy_radius_ft', sa.Float(), nullable=True))

    op.add_column('plant_varieties',
        sa.Column('growth_rate', sa.String(20), nullable=True))

    # Seed common tree species
    # Data sources: USDA Forest Service, The Arbor Day Foundation
    op.execute("""
        INSERT INTO plant_varieties (
            common_name,
            scientific_name,
            variety_name,
            is_tree,
            typical_height_ft,
            typical_canopy_radius_ft,
            growth_rate,
            description,
            growing_notes,
            sun_requirement,
            water_requirement,
            tags
        ) VALUES
        -- Shade Trees (large, mature specimens)
        ('Oak', 'Quercus spp.', 'Mature', true, 60, 30, 'slow',
         'Large deciduous shade tree with broad canopy. Provides excellent shade.',
         'Slow-growing but long-lived. Deep roots, needs space. Fall acorns attract wildlife.',
         'full_sun', 'low', 'shade,deciduous,native,wildlife'),

        ('Maple', 'Acer spp.', 'Mature', true, 50, 25, 'moderate',
         'Popular deciduous shade tree with brilliant fall color.',
         'Moderate growth rate. Shallow roots may limit undergrowth. Fall foliage spectacular.',
         'full_sun', 'medium', 'shade,deciduous,fall_color'),

        ('Elm', 'Ulmus spp.', 'Mature', true, 70, 35, 'moderate',
         'Large vase-shaped shade tree with graceful arching branches.',
         'Disease-resistant varieties available. Excellent street tree.',
         'full_sun', 'medium', 'shade,deciduous,urban'),

        -- Ornamental Trees (medium size)
        ('Dogwood', 'Cornus florida', 'Standard', true, 25, 15, 'slow',
         'Small ornamental tree with showy spring flowers.',
         'Prefers partial shade in hot climates. Spring blooms, fall berries.',
         'partial_sun', 'medium', 'ornamental,deciduous,flowering'),

        ('Redbud', 'Cercis canadensis', 'Standard', true, 20, 12, 'moderate',
         'Small flowering tree with pink-purple blooms in early spring.',
         'Blooms before leaves emerge. Heart-shaped leaves. Native understory tree.',
         'partial_sun', 'medium', 'ornamental,deciduous,flowering,native'),

        ('Crabapple', 'Malus spp.', 'Ornamental', true, 20, 15, 'moderate',
         'Small flowering tree with spring blooms and small fruit.',
         'Disease-resistant varieties available. Attracts pollinators.',
         'full_sun', 'medium', 'ornamental,deciduous,flowering,fruiting'),

        -- Evergreens (medium to large)
        ('Pine', 'Pinus spp.', 'Mature', true, 50, 20, 'moderate',
         'Evergreen conifer providing year-round screening and shade.',
         'Needled evergreen. Provides winter interest. Drought tolerant once established.',
         'full_sun', 'low', 'evergreen,screening,conifer'),

        ('Spruce', 'Picea spp.', 'Mature', true, 60, 15, 'slow',
         'Pyramidal evergreen conifer with dense branching.',
         'Classic Christmas tree shape. Prefers cool climates.',
         'full_sun', 'medium', 'evergreen,screening,conifer'),

        ('Cedar', 'Cedrus spp.', 'Mature', true, 55, 25, 'moderate',
         'Large evergreen conifer with aromatic wood.',
         'Attractive horizontal branching. Drought tolerant.',
         'full_sun', 'low', 'evergreen,screening,conifer'),

        -- Fruit Trees (small to medium)
        ('Apple', 'Malus domestica', 'Standard', true, 20, 15, 'moderate',
         'Fruit tree producing edible apples. Requires cross-pollination.',
         'Choose varieties suited to your climate zone. Needs full sun for best fruit.',
         'full_sun', 'medium', 'fruiting,deciduous,edible'),

        ('Cherry', 'Prunus avium', 'Standard', true, 25, 15, 'moderate',
         'Fruit tree with spring blossoms and edible cherries.',
         'Beautiful spring flowers. Birds love the fruit. Sweet or sour varieties.',
         'full_sun', 'medium', 'fruiting,deciduous,edible,flowering'),

        ('Peach', 'Prunus persica', 'Standard', true, 15, 15, 'fast',
         'Small fruit tree producing sweet peaches.',
         'Fast-growing but shorter-lived. Needs winter chill hours.',
         'full_sun', 'medium', 'fruiting,deciduous,edible'),

        -- Fast-growing shade/privacy
        ('Willow', 'Salix spp.', 'Mature', true, 40, 30, 'fast',
         'Fast-growing deciduous tree with graceful weeping habit.',
         'Very fast growth. Loves water. Keep away from pipes/foundations.',
         'full_sun', 'high', 'shade,deciduous,fast_growing'),

        ('Poplar', 'Populus spp.', 'Mature', true, 50, 20, 'fast',
         'Fast-growing columnar tree for quick screening.',
         'Very fast growth. Short-lived. Good for windbreaks.',
         'full_sun', 'medium', 'screening,deciduous,fast_growing')

        ON CONFLICT DO NOTHING
    """)


def downgrade():
    """Remove tree species and dimension fields"""

    # Remove tree species
    op.execute("""
        DELETE FROM plant_varieties
        WHERE is_tree = true
    """)

    # Drop tree dimension columns
    op.drop_column('plant_varieties', 'growth_rate')
    op.drop_column('plant_varieties', 'typical_canopy_radius_ft')
    op.drop_column('plant_varieties', 'typical_height_ft')
    op.drop_column('plant_varieties', 'is_tree')
