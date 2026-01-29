-- Seed Data: Plant Varieties
-- Date: 2026-01-29
-- Purpose: Populate plant_varieties table with common vegetables, herbs, and greens

-- Clear existing data (if any)
TRUNCATE plant_varieties CASCADE;

-- Vegetables (Outdoor & Hydroponic)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
-- Tomatoes
('Tomato', 'Solanum lycopersicum', 'Cherry', 5, 10, 60, 24, 36, 'full_sun', 'medium', 'Small, sweet tomatoes perfect for snacking', 'Support with stakes or cages. Prune suckers for better yield.'),
('Tomato', 'Solanum lycopersicum', 'Beefsteak', 5, 10, 85, 36, 48, 'full_sun', 'medium', 'Large, meaty tomatoes ideal for slicing', 'Requires strong support. Best flavor when vine-ripened.'),
('Tomato', 'Solanum lycopersicum', 'Roma', 5, 10, 75, 24, 36, 'full_sun', 'medium', 'Paste tomatoes, great for sauces', 'Determinate variety, compact growth habit.'),

-- Lettuce (Great for Hydroponics)
('Lettuce', 'Lactuca sativa', 'Butterhead', 4, 7, 45, 8, 12, 'partial_sun', 'high', 'Tender, buttery leaves with mild flavor', 'Thrives in cool weather. Bolt-resistant varieties available.'),
('Lettuce', 'Lactuca sativa', 'Romaine', 4, 7, 55, 8, 12, 'partial_sun', 'high', 'Crisp, upright leaves, heat tolerant', 'Excellent for hydroponics. Harvest outer leaves continuously.'),
('Lettuce', 'Lactuca sativa', 'Oak Leaf', 4, 7, 50, 8, 12, 'partial_sun', 'high', 'Loose leaf variety with oak-shaped leaves', 'Slow to bolt. Cut-and-come-again harvesting.'),

-- Herbs (Indoor & Outdoor)
('Basil', 'Ocimum basilicum', 'Sweet Basil', 5, 10, 60, 10, 12, 'full_sun', 'medium', 'Classic Italian basil, aromatic and flavorful', 'Pinch flowers to encourage leaf growth. Grows well indoors.'),
('Basil', 'Ocimum basilicum', 'Thai Basil', 5, 10, 60, 10, 12, 'full_sun', 'medium', 'Anise-flavored basil for Asian cuisine', 'More heat tolerant than sweet basil.'),
('Cilantro', 'Coriandrum sativum', 'Standard', 7, 14, 50, 6, 8, 'full_sun', 'medium', 'Popular herb for Mexican and Asian dishes', 'Bolts quickly in heat. Succession plant every 2-3 weeks.'),
('Parsley', 'Petroselinum crispum', 'Flat Leaf', 14, 21, 70, 8, 10, 'partial_sun', 'medium', 'Italian parsley, strong flavor', 'Slow to germinate. Biennial, overwinters in mild climates.'),
('Mint', 'Mentha spicata', 'Spearmint', 7, 14, 60, 12, 18, 'partial_shade', 'high', 'Refreshing herb for teas and cooking', 'Spreads aggressively. Best grown in containers.'),

-- Peppers
('Pepper', 'Capsicum annuum', 'Bell Pepper', 7, 14, 75, 18, 24, 'full_sun', 'medium', 'Sweet, crisp peppers in multiple colors', 'Benefits from calcium for blossom end rot prevention.'),
('Pepper', 'Capsicum annuum', 'Jalapeño', 7, 14, 70, 18, 24, 'full_sun', 'medium', 'Moderately spicy pepper, versatile', 'Allow to ripen red for sweeter, smokier flavor.'),

-- Leafy Greens (Excellent for Hydroponics)
('Spinach', 'Spinacia oleracea', 'Baby Leaf', 6, 10, 40, 4, 12, 'partial_sun', 'high', 'Tender baby spinach leaves', 'Cool season crop. Bolt-resistant in spring.'),
('Kale', 'Brassica oleracea', 'Lacinato', 5, 8, 60, 12, 18, 'full_sun', 'medium', 'Dinosaur kale, dark blue-green leaves', 'Frost improves flavor. Very cold hardy.'),
('Arugula', 'Eruca vesicaria', 'Rocket', 4, 7, 40, 4, 6, 'partial_sun', 'medium', 'Peppery salad green', 'Quick growing. Succession plant for continuous harvest.'),
('Swiss Chard', 'Beta vulgaris', 'Rainbow', 7, 14, 55, 6, 12, 'full_sun', 'medium', 'Colorful stems, nutritious greens', 'Heat tolerant. Harvest outer leaves continuously.'),

-- Cucumbers
('Cucumber', 'Cucumis sativus', 'Pickling', 4, 8, 55, 12, 36, 'full_sun', 'high', 'Small cucumbers perfect for pickles', 'Trellis for straight fruit and disease prevention.'),
('Cucumber', 'Cucumis sativus', 'Slicing', 4, 8, 60, 12, 36, 'full_sun', 'high', 'Long cucumbers for fresh eating', 'Keep well-watered to prevent bitterness.'),

-- Beans
('Bean', 'Phaseolus vulgaris', 'Green Bush', 6, 10, 55, 4, 18, 'full_sun', 'medium', 'Compact bush beans, no support needed', 'Nitrogen fixer. Harvest regularly for continuous production.'),
('Bean', 'Phaseolus vulgaris', 'Pole', 6, 10, 65, 6, 36, 'full_sun', 'medium', 'Climbing beans, higher yield', 'Requires trellis or pole support.'),

-- Radish (Quick Growing)
('Radish', 'Raphanus sativus', 'Cherry Belle', 4, 6, 25, 2, 6, 'full_sun', 'medium', 'Fast-growing red radishes', 'Succession plant every 10 days. Harvest promptly to avoid pithiness.'),

-- Microgreens (Perfect for Indoor/Hydroponic)
('Microgreens', 'Various', 'Broccoli', 2, 4, 10, 1, 2, 'partial_sun', 'high', 'Nutrient-dense baby broccoli greens', 'Harvest at 1-2 inches. No thinning required.'),
('Microgreens', 'Various', 'Sunflower', 2, 4, 12, 1, 2, 'partial_sun', 'high', 'Crunchy, nutty flavor microgreens', 'Pre-soak seeds for faster germination.'),
('Microgreens', 'Various', 'Pea Shoots', 3, 5, 14, 1, 2, 'partial_sun', 'high', 'Sweet, tender pea shoots', 'Harvest when 3-4 inches tall. Can regrow for second harvest.'),

-- Carrots
('Carrot', 'Daucus carota', 'Nantes', 10, 14, 70, 2, 12, 'full_sun', 'medium', 'Sweet, cylindrical carrots', 'Needs loose, deep soil. Thin to prevent crowding.'),

-- Strawberries (Indoor/Outdoor)
('Strawberry', 'Fragaria × ananassa', 'Everbearing', 14, 21, 120, 12, 24, 'full_sun', 'medium', 'Produces fruit spring through fall', 'Great for containers. Remove runners for larger berries.');

-- Add tags for filtering
UPDATE plant_varieties SET tags = ARRAY['vegetable', 'fruit'] WHERE common_name IN ('Tomato', 'Pepper', 'Cucumber');
UPDATE plant_varieties SET tags = ARRAY['leafy-green', 'salad'] WHERE common_name IN ('Lettuce', 'Spinach', 'Arugula');
UPDATE plant_varieties SET tags = ARRAY['herb', 'aromatic'] WHERE common_name IN ('Basil', 'Cilantro', 'Parsley', 'Mint');
UPDATE plant_varieties SET tags = ARRAY['leafy-green', 'nutritious'] WHERE common_name IN ('Kale', 'Swiss Chard');
UPDATE plant_varieties SET tags = ARRAY['legume', 'nitrogen-fixer'] WHERE common_name = 'Bean';
UPDATE plant_varieties SET tags = ARRAY['root-vegetable', 'quick-growing'] WHERE common_name = 'Radish';
UPDATE plant_varieties SET tags = ARRAY['microgreen', 'quick-growing', 'hydroponic'] WHERE common_name = 'Microgreens';
UPDATE plant_varieties SET tags = ARRAY['root-vegetable'] WHERE common_name = 'Carrot';
UPDATE plant_varieties SET tags = ARRAY['fruit', 'perennial'] WHERE common_name = 'Strawberry';

-- Verification
\echo 'Seed data inserted successfully!'
\echo ''
SELECT
    common_name,
    COUNT(*) as varieties,
    array_agg(variety_name ORDER BY variety_name) as names
FROM plant_varieties
GROUP BY common_name
ORDER BY common_name;

\echo ''
\echo 'Total plant varieties:'
SELECT COUNT(*) FROM plant_varieties;
