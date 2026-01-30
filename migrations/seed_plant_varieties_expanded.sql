-- Seed Data: Plant Varieties (Expanded Catalog)
-- Date: 2026-01-29
-- Purpose: Comprehensive plant varieties catalog (~100 varieties)
-- Covers: Vegetables, Fruits, Herbs, Grains, Cover Crops, and Specialty Plants

-- Clear existing data (if any)
TRUNCATE plant_varieties CASCADE;

-- =============================================================================
-- VEGETABLES (~40 varieties)
-- =============================================================================

-- Tomatoes (6 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Tomato', 'Solanum lycopersicum', 'Cherry', 5, 10, 60, 24, 36, 'full_sun', 'medium', 'Small, sweet tomatoes perfect for snacking', 'Support with stakes or cages. Prune suckers for better yield.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Tomato', 'Solanum lycopersicum', 'Beefsteak', 5, 10, 85, 36, 48, 'full_sun', 'medium', 'Large, meaty tomatoes ideal for slicing', 'Requires strong support. Best flavor when vine-ripened.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Tomato', 'Solanum lycopersicum', 'Roma', 5, 10, 75, 24, 36, 'full_sun', 'medium', 'Paste tomatoes, great for sauces', 'Determinate variety, compact growth habit.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Tomato', 'Solanum lycopersicum', 'Heirloom', 5, 10, 80, 30, 42, 'full_sun', 'medium', 'Open-pollinated varieties with unique flavors', 'Disease-prone; ensure good air circulation.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Tomato', 'Solanum lycopersicum', 'Grape', 5, 10, 65, 24, 36, 'full_sun', 'medium', 'Small oblong tomatoes, sweet and firm', 'High yield. Good for containers.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Tomato', 'Solanum lycopersicum', 'San Marzano', 5, 10, 80, 24, 36, 'full_sun', 'medium', 'Italian paste tomato, low moisture content', 'Excellent for canning and sauces.');

-- Peppers (6 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pepper', 'Capsicum annuum', 'Bell Pepper', 7, 14, 75, 18, 24, 'full_sun', 'medium', 'Sweet, crisp peppers in multiple colors', 'Benefits from calcium for blossom end rot prevention.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pepper', 'Capsicum annuum', 'Jalapeño', 7, 14, 70, 18, 24, 'full_sun', 'medium', 'Moderately spicy pepper, versatile', 'Allow to ripen red for sweeter, smokier flavor.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pepper', 'Capsicum annuum', 'Cayenne', 7, 14, 70, 18, 24, 'full_sun', 'medium', 'Hot pepper for drying and spice', 'Thin-walled, dries well. Handle with care.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pepper', 'Capsicum annuum', 'Poblano', 7, 14, 65, 18, 24, 'full_sun', 'medium', 'Mild pepper, excellent for roasting', 'Dark green to red. Good for stuffing.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pepper', 'Capsicum chinense', 'Habanero', 10, 21, 90, 18, 24, 'full_sun', 'medium', 'Very hot pepper with fruity notes', 'Requires long warm season. Handle with gloves.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pepper', 'Capsicum annuum', 'Shishito', 7, 14, 60, 18, 24, 'full_sun', 'medium', 'Mild Japanese pepper, occasionally hot', 'Harvest small and green. Great for grilling.');

-- Lettuce and Salad Greens (7 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Lettuce', 'Lactuca sativa', 'Butterhead', 4, 7, 45, 8, 12, 'partial_sun', 'high', 'Tender, buttery leaves with mild flavor', 'Thrives in cool weather. Bolt-resistant varieties available.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Lettuce', 'Lactuca sativa', 'Romaine', 4, 7, 55, 8, 12, 'partial_sun', 'high', 'Crisp, upright leaves, heat tolerant', 'Excellent for hydroponics. Harvest outer leaves continuously.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Lettuce', 'Lactuca sativa', 'Oak Leaf', 4, 7, 50, 8, 12, 'partial_sun', 'high', 'Loose leaf variety with oak-shaped leaves', 'Slow to bolt. Cut-and-come-again harvesting.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Lettuce', 'Lactuca sativa', 'Iceberg', 4, 7, 70, 12, 16, 'partial_sun', 'high', 'Crisp head lettuce, heat sensitive', 'Requires consistent moisture. Best in cool weather.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Spinach', 'Spinacia oleracea', 'Baby Leaf', 6, 10, 40, 4, 12, 'partial_sun', 'high', 'Tender baby spinach leaves', 'Cool season crop. Bolt-resistant in spring.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Kale', 'Brassica oleracea', 'Lacinato', 5, 8, 60, 12, 18, 'full_sun', 'medium', 'Dinosaur kale, dark blue-green leaves', 'Frost improves flavor. Very cold hardy.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Arugula', 'Eruca vesicaria', 'Rocket', 4, 7, 40, 4, 6, 'partial_sun', 'medium', 'Peppery salad green', 'Quick growing. Succession plant for continuous harvest.');

-- Brassicas (5 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Broccoli', 'Brassica oleracea var. italica', 'Calabrese', 5, 10, 60, 18, 24, 'full_sun', 'medium', 'Green sprouting broccoli', 'Harvest main head, side shoots continue to produce.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Cauliflower', 'Brassica oleracea var. botrytis', 'Snowball', 5, 10, 75, 18, 24, 'full_sun', 'medium', 'White compact heads', 'Tie leaves over head to blanch. Needs consistent moisture.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Cabbage', 'Brassica oleracea var. capitata', 'Green', 5, 10, 70, 15, 24, 'full_sun', 'medium', 'Dense round heads', 'Cool season crop. Crack-resistant varieties available.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Brussels Sprouts', 'Brassica oleracea var. gemmifera', 'Long Island', 5, 10, 90, 18, 30, 'full_sun', 'medium', 'Small cabbage-like buds on stalks', 'Frost improves flavor. Harvest bottom to top.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Kohlrabi', 'Brassica oleracea var. gongylodes', 'Vienna', 4, 7, 55, 6, 12, 'full_sun', 'medium', 'Bulbous stem vegetable, crisp and sweet', 'Harvest when bulb is 2-3 inches. Quick growing.');

-- Cucurbits (6 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Cucumber', 'Cucumis sativus', 'Pickling', 4, 8, 55, 12, 36, 'full_sun', 'high', 'Small cucumbers perfect for pickles', 'Trellis for straight fruit and disease prevention.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Cucumber', 'Cucumis sativus', 'Slicing', 4, 8, 60, 12, 36, 'full_sun', 'high', 'Long cucumbers for fresh eating', 'Keep well-watered to prevent bitterness.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Zucchini', 'Cucurbita pepo', 'Green', 6, 10, 50, 24, 36, 'full_sun', 'medium', 'Prolific summer squash', 'Harvest young at 6-8 inches. Very productive.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Summer Squash', 'Cucurbita pepo', 'Yellow Crookneck', 6, 10, 55, 24, 36, 'full_sun', 'medium', 'Curved neck yellow squash', 'Pick frequently to encourage production.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Butternut Squash', 'Cucurbita moschata', 'Waltham', 7, 12, 110, 36, 60, 'full_sun', 'medium', 'Winter squash with sweet orange flesh', 'Cure after harvest for better storage.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pumpkin', 'Cucurbita pepo', 'Sugar Pie', 7, 10, 100, 48, 72, 'full_sun', 'medium', 'Small sweet pumpkins for cooking', 'Needs space to sprawl. Good for pies.');

-- Beans and Legumes (4 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Bean', 'Phaseolus vulgaris', 'Green Bush', 6, 10, 55, 4, 18, 'full_sun', 'medium', 'Compact bush beans, no support needed', 'Nitrogen fixer. Harvest regularly for continuous production.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Bean', 'Phaseolus vulgaris', 'Pole', 6, 10, 65, 6, 36, 'full_sun', 'medium', 'Climbing beans, higher yield', 'Requires trellis or pole support.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pea', 'Pisum sativum', 'English', 7, 14, 60, 2, 24, 'full_sun', 'medium', 'Sweet garden peas for shelling', 'Cool season crop. Trellis recommended.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pea', 'Pisum sativum', 'Snow', 7, 14, 60, 2, 24, 'full_sun', 'medium', 'Flat edible pods', 'Harvest before peas swell. Excellent stir-fry vegetable.');

-- Root Vegetables (5 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Carrot', 'Daucus carota', 'Nantes', 10, 14, 70, 2, 12, 'full_sun', 'medium', 'Sweet, cylindrical carrots', 'Needs loose, deep soil. Thin to prevent crowding.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Carrot', 'Daucus carota', 'Danvers', 10, 14, 75, 2, 12, 'full_sun', 'medium', 'Tapered carrots, good for heavy soil', 'Tolerates heavier soils than other varieties.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Radish', 'Raphanus sativus', 'Cherry Belle', 4, 6, 25, 2, 6, 'full_sun', 'medium', 'Fast-growing red radishes', 'Succession plant every 10 days. Harvest promptly.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Beet', 'Beta vulgaris', 'Detroit Dark Red', 7, 14, 60, 3, 12, 'full_sun', 'medium', 'Deep red beets, sweet flavor', 'Both roots and greens are edible.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Turnip', 'Brassica rapa', 'Purple Top', 4, 7, 50, 4, 12, 'full_sun', 'medium', 'White turnip with purple shoulders', 'Cool season crop. Harvest at 2-3 inches.');

-- Alliums (3 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Onion', 'Allium cepa', 'Yellow Storage', 7, 14, 110, 4, 12, 'full_sun', 'medium', 'Long-storing yellow onions', 'Cure properly for maximum storage life.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Garlic', 'Allium sativum', 'Softneck', 7, 14, 240, 4, 12, 'full_sun', 'low', 'Mild garlic with flexible stems for braiding', 'Plant in fall for summer harvest.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Leek', 'Allium ampeloprasum', 'King Richard', 10, 14, 75, 6, 12, 'full_sun', 'medium', 'Mild onion flavor, long white stalks', 'Hill soil around stems to blanch.');

-- Specialty Vegetables (3 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Swiss Chard', 'Beta vulgaris', 'Rainbow', 7, 14, 55, 6, 12, 'full_sun', 'medium', 'Colorful stems, nutritious greens', 'Heat tolerant. Harvest outer leaves continuously.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Eggplant', 'Solanum melongena', 'Black Beauty', 7, 14, 80, 24, 36, 'full_sun', 'medium', 'Dark purple, large fruits', 'Needs warm soil and long season.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Okra', 'Abelmoschus esculentus', 'Clemson Spineless', 7, 14, 60, 12, 36, 'full_sun', 'medium', 'Heat-loving vegetable', 'Harvest pods young at 3-4 inches.');

-- =============================================================================
-- FRUITS (~20 varieties)
-- =============================================================================

-- Berries (8 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Strawberry', 'Fragaria × ananassa', 'Everbearing', 14, 21, 120, 12, 24, 'full_sun', 'medium', 'Produces fruit spring through fall', 'Great for containers. Remove runners for larger berries.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Strawberry', 'Fragaria × ananassa', 'June-bearing', 14, 21, 120, 12, 24, 'full_sun', 'medium', 'Single large crop in early summer', 'Higher yield than everbearing. Cold hardy.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Raspberry', 'Rubus idaeus', 'Heritage', NULL, NULL, 365, 24, 48, 'full_sun', 'medium', 'Everbearing red raspberry', 'Prune old canes after harvest. Spreads via suckers.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Blackberry', 'Rubus fruticosus', 'Thornless', NULL, NULL, 730, 36, 72, 'full_sun', 'medium', 'Thornless trailing blackberry', 'Train on trellis. Prune floricanes after fruiting.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Blueberry', 'Vaccinium corymbosum', 'Highbush', NULL, NULL, 730, 48, 72, 'partial_sun', 'high', 'Large sweet berries, acidic soil required', 'Needs pH 4.5-5.5. Plant multiple varieties for pollination.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Gooseberry', 'Ribes uva-crispa', 'Invicta', NULL, NULL, 730, 36, 60, 'partial_sun', 'medium', 'Tart green berries for preserves', 'Thorny. Tolerates partial shade.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Currant', 'Ribes rubrum', 'Red Lake', NULL, NULL, 730, 36, 60, 'partial_sun', 'medium', 'Tart red berries, high in vitamin C', 'Self-fertile. Good for jams and jellies.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Elderberry', 'Sambucus nigra', 'Black Lace', NULL, NULL, 730, 72, 96, 'full_sun', 'medium', 'Dark purple berries for syrup and wine', 'Ornamental foliage. Requires cooking before consumption.');

-- Tree Fruits (7 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Apple', 'Malus domestica', 'Honeycrisp', NULL, NULL, 1460, 180, 240, 'full_sun', 'medium', 'Crisp, sweet apples', 'Requires cross-pollination. Cold hardy.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Pear', 'Pyrus communis', 'Bartlett', NULL, NULL, 1460, 180, 240, 'full_sun', 'medium', 'Classic pear for fresh eating and canning', 'Self-fertile. Fire blight susceptible.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Cherry', 'Prunus avium', 'Bing', NULL, NULL, 1460, 240, 300, 'full_sun', 'medium', 'Sweet dark red cherries', 'Needs cross-pollination. Bird protection required.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Plum', 'Prunus domestica', 'Italian', NULL, NULL, 1095, 180, 240, 'full_sun', 'medium', 'Freestone plums for fresh eating', 'Self-fertile. Good for drying as prunes.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Peach', 'Prunus persica', 'Elberta', NULL, NULL, 1095, 180, 240, 'full_sun', 'medium', 'Classic freestone peach', 'Self-fertile. Thin fruit for larger size.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Apricot', 'Prunus armeniaca', 'Moorpark', NULL, NULL, 1095, 180, 240, 'full_sun', 'low', 'Sweet orange apricots', 'Self-fertile. Early blooming, frost sensitive.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Fig', 'Ficus carica', 'Brown Turkey', NULL, NULL, 730, 96, 120, 'full_sun', 'medium', 'Sweet purple figs', 'Self-fertile. Container-friendly in cold climates.');

-- Melons and Vining Fruits (5 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Watermelon', 'Citrullus lanatus', 'Sugar Baby', 7, 10, 85, 36, 72, 'full_sun', 'medium', 'Small round watermelons, 8-10 lbs', 'Needs heat and space. Thin to 2-3 fruits per vine.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Cantaloupe', 'Cucumis melo var. cantalupensis', 'Hales Best', 5, 8, 85, 24, 60, 'full_sun', 'medium', 'Sweet orange melons', 'Check for slip when ripe. Needs warm soil.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Honeydew', 'Cucumis melo', 'Honey Dew', 5, 8, 95, 24, 60, 'full_sun', 'medium', 'Sweet green flesh melons', 'Longer season than cantaloupe.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Grape', 'Vitis vinifera', 'Concord', NULL, NULL, 1095, 72, 96, 'full_sun', 'medium', 'Classic American table grape', 'Requires trellis. Prune heavily in dormant season.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Kiwi', 'Actinidia deliciosa', 'Hayward', NULL, NULL, 1460, 120, 180, 'full_sun', 'medium', 'Fuzzy brown kiwi fruit', 'Requires male and female vines. Hardy to zone 7.');

-- =============================================================================
-- HERBS (~15 varieties)
-- =============================================================================

-- Culinary Herbs (12 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Basil', 'Ocimum basilicum', 'Sweet Basil', 5, 10, 60, 10, 12, 'full_sun', 'medium', 'Classic Italian basil, aromatic and flavorful', 'Pinch flowers to encourage leaf growth.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Basil', 'Ocimum basilicum', 'Thai Basil', 5, 10, 60, 10, 12, 'full_sun', 'medium', 'Anise-flavored basil for Asian cuisine', 'More heat tolerant than sweet basil.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Cilantro', 'Coriandrum sativum', 'Standard', 7, 14, 50, 6, 8, 'full_sun', 'medium', 'Popular herb for Mexican and Asian dishes', 'Bolts quickly in heat. Succession plant.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Parsley', 'Petroselinum crispum', 'Flat Leaf', 14, 21, 70, 8, 10, 'partial_sun', 'medium', 'Italian parsley, strong flavor', 'Biennial, overwinters in mild climates.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Parsley', 'Petroselinum crispum', 'Curly Leaf', 14, 21, 70, 8, 10, 'partial_sun', 'medium', 'Decorative garnish parsley', 'Slower to bolt than flat leaf.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Mint', 'Mentha spicata', 'Spearmint', 7, 14, 60, 12, 18, 'partial_shade', 'high', 'Refreshing herb for teas and cooking', 'Spreads aggressively. Best in containers.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Oregano', 'Origanum vulgare', 'Greek', 7, 14, 80, 10, 12, 'full_sun', 'low', 'Pungent Mediterranean herb', 'Perennial. Drought tolerant once established.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Thyme', 'Thymus vulgaris', 'Common', 14, 21, 80, 8, 12, 'full_sun', 'low', 'Aromatic herb for cooking', 'Perennial. Low growing, good ground cover.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Rosemary', 'Rosmarinus officinalis', 'Tuscan Blue', NULL, NULL, 730, 24, 36, 'full_sun', 'low', 'Woody perennial herb', 'Drought tolerant. Not cold hardy below zone 7.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Sage', 'Salvia officinalis', 'Garden', 10, 21, 730, 18, 24, 'full_sun', 'low', 'Gray-green leaves, strong flavor', 'Perennial. Drought tolerant.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Chives', 'Allium schoenoprasum', 'Common', 10, 14, 60, 6, 8, 'full_sun', 'medium', 'Mild onion flavor, edible flowers', 'Perennial. Divide clumps every 3-4 years.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Dill', 'Anethum graveolens', 'Bouquet', 7, 14, 50, 12, 18, 'full_sun', 'medium', 'Feathery leaves for pickling', 'Direct sow, dislikes transplanting.');

-- Medicinal/Tea Herbs (3 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Chamomile', 'Matricaria chamomilla', 'German', 7, 14, 60, 6, 12, 'full_sun', 'medium', 'Daisy-like flowers for calming tea', 'Self-seeds readily. Annual.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Lavender', 'Lavandula angustifolia', 'Munstead', 14, 28, 730, 18, 24, 'full_sun', 'low', 'Fragrant purple flowers', 'Perennial. Drought tolerant. Good for pollinators.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Lemon Balm', 'Melissa officinalis', 'Common', 10, 14, 730, 12, 18, 'partial_sun', 'medium', 'Lemon-scented leaves for tea', 'Perennial. Can be invasive.');

-- =============================================================================
-- GRAINS & COVER CROPS (~10 varieties)
-- =============================================================================

-- Grains (5 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Wheat', 'Triticum aestivum', 'Hard Red Spring', 7, 14, 120, 1, 6, 'full_sun', 'medium', 'High-protein bread wheat', 'Cool season grain. Broadcast or drill.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Oats', 'Avena sativa', 'Common', 7, 14, 100, 1, 6, 'full_sun', 'medium', 'Cereal grain, good cover crop', 'Cold tolerant. Improves soil structure.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Barley', 'Hordeum vulgare', 'Hull-less', 7, 14, 90, 1, 6, 'full_sun', 'medium', 'Fast-growing grain', 'Earliest maturing grain. Drought tolerant.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Rye', 'Secale cereale', 'Winter', 7, 10, 180, 1, 6, 'full_sun', 'low', 'Hardy winter grain and cover crop', 'Plant in fall. Excellent weed suppressor.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Quinoa', 'Chenopodium quinoa', 'Rainbow', 4, 7, 95, 12, 18, 'full_sun', 'medium', 'High-protein pseudocereal', 'Drought tolerant. Rinse before cooking.');

-- Cover Crops / Green Manure (5 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Crimson Clover', 'Trifolium incarnatum', 'Dixie', 7, 14, 70, 2, 12, 'full_sun', 'medium', 'Annual nitrogen-fixing cover crop', 'Beautiful red blooms. Incorporate before seed set.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('White Clover', 'Trifolium repens', 'Dutch', 7, 14, 60, 4, 12, 'full_sun', 'medium', 'Perennial nitrogen fixer', 'Living mulch. Good for bee forage.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Hairy Vetch', 'Vicia villosa', 'Common', 10, 14, 180, 2, 12, 'full_sun', 'medium', 'Winter annual legume cover crop', 'Excellent nitrogen fixer. Plant in fall.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Buckwheat', 'Fagopyrum esculentum', 'Common', 5, 7, 70, 4, 12, 'full_sun', 'medium', 'Fast-growing summer cover crop', 'Smothers weeds. Good for bees. Not a true grain.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Field Peas', 'Pisum sativum var. arvense', 'Austrian Winter', 7, 14, 180, 2, 12, 'full_sun', 'medium', 'Cold-hardy cover crop', 'Nitrogen fixer. Plant in fall for spring biomass.');

-- =============================================================================
-- SPECIALTY & COMPANION PLANTS (~17 varieties)
-- =============================================================================

-- Flowers for Pollinators (8 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Sunflower', 'Helianthus annuus', 'Mammoth', 7, 14, 90, 24, 36, 'full_sun', 'medium', 'Giant sunflowers up to 12 feet tall', 'Seeds for eating or birdseed. Good for pollinators.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Marigold', 'Tagetes patula', 'French', 5, 7, 50, 10, 12, 'full_sun', 'medium', 'Orange flowers, pest deterrent', 'Companion plant. Deters nematodes.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Nasturtium', 'Tropaeolum majus', 'Jewel Mix', 7, 14, 50, 12, 18, 'full_sun', 'medium', 'Edible flowers and leaves, peppery', 'Trap crop for aphids. Climbing varieties available.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Calendula', 'Calendula officinalis', 'Pacific Beauty', 7, 14, 55, 12, 18, 'full_sun', 'medium', 'Medicinal orange flowers', 'Edible petals. Self-seeds readily.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Zinnia', 'Zinnia elegans', 'Cut and Come Again', 5, 7, 60, 12, 18, 'full_sun', 'medium', 'Colorful cutting flowers', 'Deadhead for continuous blooms. Attracts butterflies.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Cosmos', 'Cosmos bipinnatus', 'Sensation Mix', 7, 10, 70, 12, 18, 'full_sun', 'low', 'Tall airy flowers for pollinators', 'Self-seeds. Drought tolerant.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Borage', 'Borago officinalis', 'Common', 7, 14, 55, 12, 18, 'full_sun', 'medium', 'Blue star flowers, edible', 'Self-seeds. Attracts bees. Companion plant.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Phacelia', 'Phacelia tanacetifolia', 'Lacy Phacelia', 7, 14, 60, 6, 12, 'full_sun', 'medium', 'Purple flowers, excellent bee forage', 'Cover crop and pollinator attractant.');

-- Microgreens (5 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Microgreens', 'Various', 'Broccoli', 2, 4, 10, 1, 2, 'partial_sun', 'high', 'Nutrient-dense baby broccoli greens', 'Harvest at 1-2 inches.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Microgreens', 'Various', 'Sunflower', 2, 4, 12, 1, 2, 'partial_sun', 'high', 'Crunchy, nutty flavor microgreens', 'Pre-soak seeds for faster germination.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Microgreens', 'Various', 'Pea Shoots', 3, 5, 14, 1, 2, 'partial_sun', 'high', 'Sweet, tender pea shoots', 'Can regrow for second harvest.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Microgreens', 'Various', 'Radish', 2, 3, 8, 1, 2, 'partial_sun', 'high', 'Spicy microgreens', 'Fast growing, peppery flavor.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Microgreens', 'Various', 'Mustard', 2, 3, 8, 1, 2, 'partial_sun', 'high', 'Spicy Asian greens', 'Quick crop, strong flavor.');

-- Perennial Vegetables (4 varieties)
INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Asparagus', 'Asparagus officinalis', 'Jersey Knight', 14, 28, 730, 18, 48, 'full_sun', 'medium', 'Perennial spring vegetable', 'Plant crowns. Do not harvest first 2 years.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Rhubarb', 'Rheum rhabarbarum', 'Victoria', 14, 21, 730, 36, 48, 'full_sun', 'medium', 'Tart stalks for pies and jams', 'Perennial. Do not eat leaves (toxic).');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Artichoke', 'Cynara cardunculus var. scolymus', 'Green Globe', 14, 21, 180, 36, 48, 'full_sun', 'medium', 'Edible flower buds', 'Perennial in mild climates. Harvest before flowers open.');

INSERT INTO plant_varieties (common_name, scientific_name, variety_name, days_to_germination_min, days_to_germination_max, days_to_harvest, spacing_inches, row_spacing_inches, sun_requirement, water_requirement, description, growing_notes) VALUES
('Horseradish', 'Armoracia rusticana', 'Maliner Kren', NULL, NULL, 365, 18, 24, 'full_sun', 'medium', 'Pungent root for condiments', 'Perennial. Invasive, grow in contained area.');

-- =============================================================================
-- ADD TAGS FOR CATEGORIZATION
-- =============================================================================

-- Vegetables
UPDATE plant_varieties SET tags = 'vegetable,fruit,warm-season' WHERE common_name IN ('Tomato', 'Pepper', 'Eggplant');
UPDATE plant_varieties SET tags = 'vegetable,cucurbit,warm-season' WHERE common_name IN ('Cucumber', 'Zucchini', 'Summer Squash', 'Butternut Squash', 'Pumpkin', 'Watermelon', 'Cantaloupe', 'Honeydew');
UPDATE plant_varieties SET tags = 'leafy-green,salad,cool-season' WHERE common_name IN ('Lettuce', 'Spinach', 'Arugula', 'Swiss Chard', 'Kale');
UPDATE plant_varieties SET tags = 'brassica,cool-season,vegetable' WHERE common_name IN ('Broccoli', 'Cauliflower', 'Cabbage', 'Brussels Sprouts', 'Kohlrabi');
UPDATE plant_varieties SET tags = 'legume,nitrogen-fixer,vegetable' WHERE common_name IN ('Bean', 'Pea');
UPDATE plant_varieties SET tags = 'root-vegetable,vegetable' WHERE common_name IN ('Carrot', 'Beet', 'Radish', 'Turnip');
UPDATE plant_varieties SET tags = 'allium,vegetable' WHERE common_name IN ('Onion', 'Garlic', 'Leek');
UPDATE plant_varieties SET tags = 'vegetable,warm-season' WHERE common_name = 'Okra';

-- Fruits
UPDATE plant_varieties SET tags = 'fruit,berry,perennial' WHERE common_name IN ('Strawberry', 'Raspberry', 'Blackberry', 'Blueberry', 'Gooseberry', 'Currant', 'Elderberry');
UPDATE plant_varieties SET tags = 'fruit,tree,perennial' WHERE common_name IN ('Apple', 'Pear', 'Cherry', 'Plum', 'Peach', 'Apricot', 'Fig');
UPDATE plant_varieties SET tags = 'fruit,vine,perennial' WHERE common_name IN ('Grape', 'Kiwi');

-- Herbs
UPDATE plant_varieties SET tags = 'herb,aromatic,culinary' WHERE common_name IN ('Basil', 'Cilantro', 'Parsley', 'Oregano', 'Thyme', 'Rosemary', 'Sage', 'Dill');
UPDATE plant_varieties SET tags = 'herb,aromatic,perennial' WHERE common_name IN ('Mint', 'Chives', 'Lemon Balm');
UPDATE plant_varieties SET tags = 'herb,medicinal,tea' WHERE common_name IN ('Chamomile', 'Lavender');

-- Grains and Cover Crops
UPDATE plant_varieties SET tags = 'grain,cereal' WHERE common_name IN ('Wheat', 'Oats', 'Barley', 'Rye', 'Quinoa');
UPDATE plant_varieties SET tags = 'cover-crop,nitrogen-fixer' WHERE common_name IN ('Crimson Clover', 'White Clover', 'Hairy Vetch', 'Field Peas');
UPDATE plant_varieties SET tags = 'cover-crop,green-manure' WHERE common_name = 'Buckwheat';

-- Specialty
UPDATE plant_varieties SET tags = 'flower,pollinator,annual' WHERE common_name IN ('Sunflower', 'Marigold', 'Nasturtium', 'Calendula', 'Zinnia', 'Cosmos', 'Borage', 'Phacelia');
UPDATE plant_varieties SET tags = 'microgreen,quick-growing,hydroponic' WHERE common_name = 'Microgreens';
UPDATE plant_varieties SET tags = 'vegetable,perennial' WHERE common_name IN ('Asparagus', 'Rhubarb', 'Artichoke', 'Horseradish');

-- =============================================================================
-- VERIFICATION
-- =============================================================================

\echo 'Seed data inserted successfully!'
\echo ''
\echo 'Plant varieties by common name:'

SELECT
    common_name,
    COUNT(*) as varieties,
    string_agg(variety_name, ', ' ORDER BY variety_name) as names
FROM plant_varieties
GROUP BY common_name
ORDER BY common_name;

\echo ''
\echo 'Total plant varieties:'
SELECT COUNT(*) as total FROM plant_varieties;

\echo ''
\echo 'Sample entries (10 random):'
SELECT common_name, variety_name, days_to_harvest, tags
FROM plant_varieties
ORDER BY RANDOM()
LIMIT 10;
