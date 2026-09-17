# Dwarf Tomato Autonomous Cultivation

**Reference:** Maree et al. (2025). "Autonomous Greenhouse Cultivation of Dwarf Tomato: Performance Evaluation of Intelligent Algorithms for Multiple-Sensor Feedback." *Sensors*.

## Overview
This documentation describes the underlying research architecture for the dwarf tomato polyhouse simulation. The paper outlines the Fourth Autonomous Greenhouse Challenge where autonomous control strategies using multi-sensor feedback were applied to dwarf tomatoes.

## Key Principles
1. **Dwarf Tomato Suitability:** High plant density, compact size, suitable for robotic harvesting.
2. **Multi-Sensor Feedback:** Requires fusing temperature, humidity, PAR, CO2, and substrate moisture.
3. **Crop State Measurement:** High difficulty. Computer vision is heavily motivated for estimating harvest readiness and canopy measurements.
4. **Autonomous Climate and Irrigation:** Optimizing yield vs water/energy costs.

## Implementation Details
Our implementation strictly models the deterministic growth response (light, temp, water) and establishes a framework for calibration using public datasets described in the literature.
