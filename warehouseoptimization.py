import json
import math
from collections import defaultdict
import random

# A professional-grade, comprehensive warehouse optimization tool.
# This script reads product data, performs ABC analysis, calculates
# key logistics and financial metrics, and provides a detailed report
# and visual representation of the findings.

# =====================================================================
# Configuration & Global Constants
# =====================================================================
WALKING_SPEED_MPS = 1.2  # meters per second
LABOR_COST_PER_HOUR = 22.50  # USD per hour
HOURS_PER_YEAR = 2080  # 40 hours/week * 52 weeks/year

# ABC Analysis thresholds (can be adjusted)
A_CATEGORY_PERCENTAGE = 0.80
B_CATEGORY_PERCENTAGE = 0.95

# Average round-trip distance from dock to zone (in meters)
ZONE_A_DISTANCE_M = 5
ZONE_B_DISTANCE_M = 15
ZONE_C_DISTANCE_M = 30

# --- Financial and Inventory Configuration ---
# Example values for a hypothetical company
ANNUAL_HOLDING_COST_PERCENTAGE = 0.15  # 15% of cost per unit
COST_PER_ORDER = 50.00  # Cost to place one order
SERVICE_LEVEL = 0.95   # Desired service level (95%) for safety stock calculation
DEMAND_VARIABILITY_FACTOR = 0.2  # A simple factor to simulate demand fluctuations

# =====================================================================
# Data Validation Class
# =====================================================================

class DataValidator:
    """
    A class to perform detailed validation on product data.
    Ensures data integrity before analysis begins.
    """
    def __init__(self, data):
        self.data = data
        self.errors = []

    def validate_all(self):
        """Runs all validation checks."""
        self._check_overall_format()
        if not self.errors:
            self._check_product_fields()
        return self.errors

    def _check_overall_format(self):
        """Checks if the top-level data is a list."""
        if not isinstance(self.data, list):
            self.errors.append("Invalid data format: Expected a JSON list.")

    def _check_product_fields(self):
        """Iterates through products to validate each one."""
        required_keys = ['sku', 'product_name', 'frequency', 'category', 'dimensions_cm', 'weight_kg', 'unit_cost']
        for i, product in enumerate(self.data):
            if not isinstance(product, dict):
                self.errors.append(f"Product at index {i} is not a dictionary.")
                continue

            for key in required_keys:
                if key not in product:
                    self.errors.append(f"Product at index {i} is missing required key: '{key}'.")
            
            self._validate_numerical_fields(product, i)

    def _validate_numerical_fields(self, product, index):
        """Validates numerical values for specific keys."""
        frequency = product.get('frequency', -1)
        unit_cost = product.get('unit_cost', -1)
        weight = product.get('weight_kg', -1)
        dims = product.get('dimensions_cm', {})

        if not (isinstance(frequency, (int, float)) and frequency >= 0):
            self.errors.append(f"Invalid 'frequency' for SKU '{product.get('sku', 'N/A')}' at index {index}.")
        
        if not (isinstance(unit_cost, (int, float)) and unit_cost >= 0):
            self.errors.append(f"Invalid 'unit_cost' for SKU '{product.get('sku', 'N/A')}' at index {index}.")

        if not (isinstance(weight, (int, float)) and weight >= 0):
            self.errors.append(f"Invalid 'weight_kg' for SKU '{product.get('sku', 'N/A')}' at index {index}.")
        
        if not (isinstance(dims, dict) and all(k in dims for k in ['length', 'width', 'height'])):
            self.errors.append(f"Invalid 'dimensions_cm' for SKU '{product.get('sku', 'N/A')}' at index {index}.")

# =====================================================================
# Warehouse Optimization Core Logic
# =====================================================================

class WarehouseOptimizer:
    """
    Main class for running the warehouse optimization analysis.
    Coordinates data loading, analysis, and reporting.
    """

    def __init__(self, data_filepath):
        """
        Initializes the optimizer with the path to the product data.
        
        Args:
            data_filepath (str): Path to the JSON file.
        """
        self.data_filepath = data_filepath
        self.products = []
        self.categories = {}
        self.metrics = {}
        self.report_data = {}

    def load_data(self):
        """
        Loads product data from the specified JSON file and validates it.
        """
        print("Initializing Warehouse Optimizer...")
        try:
            with open(self.data_filepath, 'r') as file:
                data = json.load(file)
                validator = DataValidator(data)
                errors = validator.validate_all()
                if errors:
                    print("Data validation failed. Please correct the following errors:")
                    for error in errors:
                        print(f"  - {error}")
                    self.products = []
                else:
                    self.products = data
                    print("Data loaded and validated successfully.")
        except FileNotFoundError:
            print(f"Error: The file '{self.data_filepath}' was not found.")
            self.products = []
        except json.JSONDecodeError:
            print(f"Error: The file '{self.data_filepath}' contains invalid JSON.")
            self.products = []

    def run_abc_analysis(self):
        """
        Executes the ABC analysis on the product data.
        Sorts products by frequency and categorizes them into A, B, and C based on Pareto's Principle.
        """
        if not self.products:
            return

        total_frequency = sum(p['frequency'] for p in self.products)
        if total_frequency == 0:
            print("Total frequency is zero. Analysis cannot be performed.")
            return

        sorted_products = sorted(self.products, key=lambda p: p['frequency'], reverse=True)
        
        category_a, category_b, category_c = [], [], []
        current_percentage = 0.0

        for p in sorted_products:
            item_percentage = p['frequency'] / total_frequency
            current_percentage += item_percentage
            
            if current_percentage <= A_CATEGORY_PERCENTAGE:
                category_a.append(p)
            elif current_percentage <= B_CATEGORY_PERCENTAGE:
                category_b.append(p)
            else:
                category_c.append(p)

        self.categories = {
            "categoryA": category_a,
            "categoryB": category_b,
            "categoryC": category_c
        }

    def _calculate_distance_metrics(self):
        """
        Calculates logistics metrics based on warehouse distances.
        """
        # Original Metrics (assuming products are randomly or sequentially arranged)
        original_distance = sum((i + 1) * 2 * p['frequency'] for i, p in enumerate(self.products))
        
        # Optimized Metrics (based on ABC zones)
        optimized_distance = (sum(p['frequency'] * ZONE_A_DISTANCE_M for p in self.categories['categoryA']) +
                              sum(p['frequency'] * ZONE_B_DISTANCE_M for p in self.categories['categoryB']) +
                              sum(p['frequency'] * ZONE_C_DISTANCE_M for p in self.categories['categoryC']))

        distance_saved = original_distance - optimized_distance
        efficiency_improvement = 0
        if original_distance > 0:
            efficiency_improvement = (distance_saved / original_distance) * 100

        self.metrics.update({
            "original_distance": original_distance,
            "optimized_distance": optimized_distance,
            "distance_saved": distance_saved,
            "efficiency_improvement": efficiency_improvement,
        })
        
    def _calculate_financial_metrics(self):
        """
        Calculates financial and inventory metrics.
        """
        original_time_hours = self.metrics['original_distance'] / (WALKING_SPEED_MPS * 3600)
        optimized_time_hours = self.metrics['optimized_distance'] / (WALKING_SPEED_MPS * 3600)
        
        original_cost = original_time_hours * LABOR_COST_PER_HOUR
        optimized_cost = optimized_time_hours * LABOR_COST_PER_HOUR
        
        cost_saved = original_cost - optimized_cost
        time_saved_hours = original_time_hours - optimized_time_hours
        
        self.metrics.update({
            "original_time_hours": original_time_hours,
            "optimized_time_hours": optimized_time_hours,
            "original_cost": original_cost,
            "optimized_cost": optimized_cost,
            "cost_saved": cost_saved,
            "time_saved_hours": time_saved_hours
        })
    
    def _calculate_inventory_metrics(self):
        """
        Calculates inventory management metrics like EOQ and safety stock.
        """
        inventory_metrics = {}
        for p in self.products:
            # Economic Order Quantity (EOQ) Calculation
            D = p['frequency']  # Annual Demand
            S = COST_PER_ORDER  # Cost to place one order
            H = p['unit_cost'] * ANNUAL_HOLDING_COST_PERCENTAGE # Holding cost per unit
            
            if H > 0:
                eoq = math.sqrt((2 * D * S) / H)
            else:
                eoq = 0
            
            # Simple Safety Stock Calculation
            # Demand std dev is simulated as a percentage of demand
            demand_std_dev_daily = (p['frequency'] / 365) * DEMAND_VARIABILITY_FACTOR
            service_level_z_score = 1.645 # For 95% service level
            lead_time_days = 7 # Example lead time
            safety_stock = service_level_z_score * demand_std_dev_daily * math.sqrt(lead_time_days)
            
            inventory_metrics[p['sku']] = {
                "eoq": math.ceil(eoq),
                "safety_stock": math.ceil(safety_stock)
            }
        
        self.report_data['inventory_metrics'] = inventory_metrics

    def calculate_all_metrics(self):
        """
        A single entry point to calculate all metrics for the report.
        """
        if not self.products:
            return
            
        self._calculate_distance_metrics()
        self._calculate_financial_metrics()
        self._calculate_inventory_metrics()
        
    def _get_visual_product_list(self, product_list):
        """
        Helper function to prepare products for terminal visualization.
        """
        max_name_len = 20
        return [{
            'name': p['product_name'][:max_name_len].ljust(max_name_len),
            'icon': '🟩' if p in self.categories.get('categoryA', []) else '🟨' if p in self.categories.get('categoryB', []) else '🟥'
        } for p in product_list]

    def _create_results_data_for_json(self):
        """
        Organizes all analysis results into a single dictionary for JSON export.
        """
        original_layout_products = sorted(self.products, key=lambda p: p['sku'])
        
        optimized_products_by_category = {
            "A": self.categories.get('categoryA', []),
            "B": self.categories.get('categoryB', []),
            "C": self.categories.get('categoryC', []),
        }

        return {
            "metrics": self.metrics,
            "abc_analysis": {
                "categoryA": self.categories.get('categoryA', []),
                "categoryB": self.categories.get('categoryB', []),
                "categoryC": self.categories.get('categoryC', [])
            },
            "inventory_metrics": self.report_data['inventory_metrics'],
            "layouts": {
                "original": original_layout_products,
                "optimized": optimized_products_by_category
            }
        }

    def save_results_to_file(self, filepath="warehouse_analysis_results.json"):
        """
        Saves all analysis results to a JSON file.
        
        Args:
            filepath (str): The path to the output file.
        """
        results_data = self._create_results_data_for_json()
        try:
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=4)
            print(f"\nAnalysis complete. Results saved to '{filepath}'.")
        except IOError as e:
            print(f"Error saving file: {e}")

    def run(self):
        """
        Main execution method that runs the entire optimization process.
        """
        self.load_data()
        if not self.products:
            return

        print("Data loaded successfully. Starting analysis...")
        self.run_abc_analysis()
        self.calculate_all_metrics()
        
        self.save_results_to_file()
        
if __name__ == "__main__":
    optimizer = WarehouseOptimizer("real_world_product_data.json")
    optimizer.run()
