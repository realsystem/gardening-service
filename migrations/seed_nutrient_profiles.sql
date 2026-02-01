-- Seed Nutrient Optimization Profiles for Common Crops
-- Date: 2026-02-01
-- Purpose: Populate EC/pH ranges based on hydroponic research
-- References: Resh (2012), Jones (2016), Cornell CEA Program

-- ============================================================================
-- HIGH NUTRIENT DEMAND CROPS (Fruiting vegetables)
-- ============================================================================

-- Tomato - High demand fruiting crop
UPDATE plant_varieties SET
  seedling_ec_min = 0.8, seedling_ec_max = 1.2,
  vegetative_ec_min = 1.5, vegetative_ec_max = 2.0,
  flowering_ec_min = 2.0, flowering_ec_max = 2.5,
  fruiting_ec_min = 2.5, fruiting_ec_max = 3.0,
  optimal_ph_min = 5.5, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Tomato';

-- Cucumber - Moderate to high demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.8, seedling_ec_max = 1.2,
  vegetative_ec_min = 1.6, vegetative_ec_max = 2.2,
  fruiting_ec_min = 2.0, fruiting_ec_max = 2.5,
  optimal_ph_min = 5.5, optimal_ph_max = 6.0,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Cucumber';

-- Pepper - High demand fruiting crop
UPDATE plant_varieties SET
  seedling_ec_min = 0.8, seedling_ec_max = 1.2,
  vegetative_ec_min = 1.5, vegetative_ec_max = 2.0,
  flowering_ec_min = 1.8, flowering_ec_max = 2.3,
  fruiting_ec_min = 2.0, fruiting_ec_max = 2.5,
  optimal_ph_min = 5.8, optimal_ph_max = 6.3,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Pepper';

-- Eggplant - High demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.8, seedling_ec_max = 1.2,
  vegetative_ec_min = 1.8, vegetative_ec_max = 2.4,
  fruiting_ec_min = 2.5, fruiting_ec_max = 3.0,
  optimal_ph_min = 5.5, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Eggplant';

-- ============================================================================
-- LEAFY GREENS (Low to moderate nutrient demand)
-- ============================================================================

-- Lettuce - Low nutrient demand, sensitive to high EC
UPDATE plant_varieties SET
  seedling_ec_min = 0.4, seedling_ec_max = 0.8,
  vegetative_ec_min = 0.8, vegetative_ec_max = 1.2,
  optimal_ph_min = 5.5, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 10
WHERE common_name = 'Lettuce';

-- Spinach - Low to moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.4, seedling_ec_max = 0.8,
  vegetative_ec_min = 0.8, vegetative_ec_max = 1.4,
  optimal_ph_min = 6.0, optimal_ph_max = 7.0,
  solution_change_days_min = 7, solution_change_days_max = 10
WHERE common_name = 'Spinach';

-- Kale - Moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.2, vegetative_ec_max = 1.8,
  optimal_ph_min = 5.5, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 12
WHERE common_name = 'Kale';

-- Arugula - Low demand, fast growing
UPDATE plant_varieties SET
  seedling_ec_min = 0.4, seedling_ec_max = 0.8,
  vegetative_ec_min = 0.8, vegetative_ec_max = 1.2,
  optimal_ph_min = 6.0, optimal_ph_max = 7.0,
  solution_change_days_min = 5, solution_change_days_max = 10
WHERE common_name = 'Arugula';

-- Swiss Chard - Moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.2, vegetative_ec_max = 1.8,
  optimal_ph_min = 6.0, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 12
WHERE common_name = 'Swiss Chard';

-- ============================================================================
-- HERBS (Low to moderate nutrient demand)
-- ============================================================================

-- Basil - Moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.0, vegetative_ec_max = 1.6,
  optimal_ph_min = 5.5, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Basil';

-- Cilantro - Low demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.5, seedling_ec_max = 0.9,
  vegetative_ec_min = 0.8, vegetative_ec_max = 1.4,
  optimal_ph_min = 6.0, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 12
WHERE common_name = 'Cilantro';

-- Mint - Low to moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.5, seedling_ec_max = 0.9,
  vegetative_ec_min = 1.0, vegetative_ec_max = 1.6,
  optimal_ph_min = 6.0, optimal_ph_max = 7.0,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Mint';

-- Parsley - Moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.0, vegetative_ec_max = 1.8,
  optimal_ph_min = 5.5, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 12
WHERE common_name = 'Parsley';

-- Oregano - Low to moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.5, seedling_ec_max = 0.9,
  vegetative_ec_min = 0.8, vegetative_ec_max = 1.4,
  optimal_ph_min = 6.0, optimal_ph_max = 8.0,
  solution_change_days_min = 10, solution_change_days_max = 14
WHERE common_name = 'Oregano';

-- Thyme - Low demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.4, seedling_ec_max = 0.8,
  vegetative_ec_min = 0.8, vegetative_ec_max = 1.6,
  optimal_ph_min = 5.5, optimal_ph_max = 7.0,
  solution_change_days_min = 10, solution_change_days_max = 14
WHERE common_name = 'Thyme';

-- ============================================================================
-- BRASSICAS (Moderate nutrient demand)
-- ============================================================================

-- Broccoli - Moderate to high demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.8, seedling_ec_max = 1.2,
  vegetative_ec_min = 1.5, vegetative_ec_max = 2.0,
  flowering_ec_min = 2.0, flowering_ec_max = 2.5,
  optimal_ph_min = 6.0, optimal_ph_max = 6.8,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Broccoli';

-- Cauliflower - Moderate to high demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.8, seedling_ec_max = 1.2,
  vegetative_ec_min = 1.5, vegetative_ec_max = 2.0,
  flowering_ec_min = 2.0, flowering_ec_max = 2.5,
  optimal_ph_min = 6.0, optimal_ph_max = 6.8,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Cauliflower';

-- Cabbage - Moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.8, seedling_ec_max = 1.2,
  vegetative_ec_min = 1.5, vegetative_ec_max = 2.0,
  optimal_ph_min = 6.0, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Cabbage';

-- ============================================================================
-- CUCURBITS (Moderate to high demand)
-- ============================================================================

-- Zucchini / Summer Squash - Moderate to high demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.8, seedling_ec_max = 1.2,
  vegetative_ec_min = 1.4, vegetative_ec_max = 2.0,
  fruiting_ec_min = 1.8, fruiting_ec_max = 2.4,
  optimal_ph_min = 5.8, optimal_ph_max = 6.3,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name IN ('Zucchini', 'Summer Squash');

-- Melon - Moderate to high demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.8, seedling_ec_max = 1.2,
  vegetative_ec_min = 1.4, vegetative_ec_max = 2.0,
  fruiting_ec_min = 2.0, fruiting_ec_max = 2.5,
  optimal_ph_min = 5.5, optimal_ph_max = 6.0,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Melon';

-- ============================================================================
-- SPECIALTY CROPS
-- ============================================================================

-- Strawberry - Moderate demand, sensitive to high EC
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.0, vegetative_ec_max = 1.4,
  flowering_ec_min = 1.2, flowering_ec_max = 1.6,
  fruiting_ec_min = 1.4, fruiting_ec_max = 1.8,
  optimal_ph_min = 5.5, optimal_ph_max = 6.2,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Strawberry';

-- Microgreens - Very low demand, fast growing
UPDATE plant_varieties SET
  seedling_ec_min = 0.4, seedling_ec_max = 0.6,
  vegetative_ec_min = 0.6, vegetative_ec_max = 1.0,
  optimal_ph_min = 5.5, optimal_ph_max = 6.5,
  solution_change_days_min = 3, solution_change_days_max = 7
WHERE common_name = 'Microgreens';

-- Bean - Moderate demand (nitrogen fixers need less N)
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.2, vegetative_ec_max = 1.8,
  fruiting_ec_min = 1.5, fruiting_ec_max = 2.0,
  optimal_ph_min = 6.0, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Bean';

-- Pea - Moderate demand (nitrogen fixers)
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.0, vegetative_ec_max = 1.6,
  fruiting_ec_min = 1.4, fruiting_ec_max = 2.0,
  optimal_ph_min = 6.0, optimal_ph_max = 7.0,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Pea';

-- ============================================================================
-- ROOT VEGETABLES
-- ============================================================================

-- Carrot - Low to moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.5, seedling_ec_max = 0.9,
  vegetative_ec_min = 1.0, vegetative_ec_max = 1.6,
  optimal_ph_min = 6.0, optimal_ph_max = 6.8,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Carrot';

-- Radish - Low demand, fast growing
UPDATE plant_varieties SET
  seedling_ec_min = 0.4, seedling_ec_max = 0.8,
  vegetative_ec_min = 0.8, vegetative_ec_max = 1.4,
  optimal_ph_min = 6.0, optimal_ph_max = 7.0,
  solution_change_days_min = 5, solution_change_days_max = 10
WHERE common_name = 'Radish';

-- Beet - Moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.2, vegetative_ec_max = 1.8,
  optimal_ph_min = 6.0, optimal_ph_max = 6.8,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Beet';

-- ============================================================================
-- ALLIUMS
-- ============================================================================

-- Onion - Moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.2, vegetative_ec_max = 1.8,
  optimal_ph_min = 6.0, optimal_ph_max = 6.7,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Onion';

-- Garlic - Moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.6, seedling_ec_max = 1.0,
  vegetative_ec_min = 1.2, vegetative_ec_max = 1.8,
  optimal_ph_min = 6.0, optimal_ph_max = 6.5,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Garlic';

-- Chives - Low to moderate demand
UPDATE plant_varieties SET
  seedling_ec_min = 0.5, seedling_ec_max = 0.9,
  vegetative_ec_min = 1.0, vegetative_ec_max = 1.6,
  optimal_ph_min = 6.0, optimal_ph_max = 7.0,
  solution_change_days_min = 7, solution_change_days_max = 14
WHERE common_name = 'Chives';