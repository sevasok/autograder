"""
Test Case Generator - Simple version
"""

import random


class TestCaseGenerator:
    """Generates test cases based on configuration."""
    
    def __init__(self, seed=None):
        """Initialize generator with optional seed for reproducibility."""
        if seed is not None:
            random.seed(seed)
    
    def generate_num(self, lower=0, upper=100, decimal=None, exclude=None, total_tests=10):
        """Generate number test cases.
        
        Args:
            lower: Minimum value
            upper: Maximum value
            decimal: None for int, or number of decimal places for float
            exclude: List of numbers to exclude
            total_tests: Number of tests to generate
        """
        exclude = exclude or []
        results = []
        attempts = 0
        max_attempts = total_tests * 100
        
        while len(results) < total_tests and attempts < max_attempts:
            attempts += 1
            
            if decimal is None:
                value = random.randint(int(lower), int(upper))
            else:
                value = round(random.uniform(lower, upper), decimal)
            
            if value not in exclude and value not in results:
                results.append(value)
        
        return results
    
    def generate_string(self, lower_len=0, upper_len=10, char_range=(32, 126), 
                       exclude=None, case=None, total_tests=10):
        """Generate string test cases.
        
        Args:
            lower_len: Minimum string length
            upper_len: Maximum string length
            char_range: Tuple of (min_ascii, max_ascii) for characters
            exclude: List of strings/substrings to exclude
            case: None (no change), "upper" (all caps), "lower" (all lowercase), or "random" (random caps)
            total_tests: Number of tests to generate
        """
        exclude = exclude or []
        results = []
        attempts = 0
        max_attempts = total_tests * 100
        
        while len(results) < total_tests and attempts < max_attempts:
            attempts += 1
            
            length = random.randint(lower_len, upper_len)
            value = ''.join(chr(random.randint(char_range[0], char_range[1])) 
                          for _ in range(length))
            
            # Apply case transformation
            if case == "upper":
                value = value.upper()
            elif case == "lower":
                value = value.lower()
            elif case == "random":
                value = ''.join(c.upper() if random.random() < 0.5 else c.lower() for c in value)
            
            # Skip if excluded or contains excluded substring
            if value in exclude or any(excl in value for excl in exclude):
                continue
            
            if value not in results:
                results.append(value)
        
        return results
    
    def generate_bool_or_none(self, include_true=True, include_false=True, 
                             include_none=True, total_tests=10):
        """Generate bool/None test cases.
        
        Args:
            include_true: Whether to include True
            include_false: Whether to include False
            include_none: Whether to include None
            total_tests: Number of tests to generate
        """
        pool = []
        
        if include_true:
            pool.append(True)
        
        if include_false:
            pool.append(False)
        
        if include_none:
            pool.append(None)
        
        if not pool:
            return []
        
        return random.choices(pool, k=total_tests)
    
    def generate_array(self, elements, total_tests=10):
        """Generate array test cases.
        
        Args:
            elements: List of element configs, each with {"type": "num/string/bool_or_none/array/dict", ...params}
            total_tests: Number of arrays to generate
            
        Returns:
            List of arrays, each containing elements generated from configs
        """
        results = []
        
        for _ in range(total_tests):
            array = []
            for element_config in elements:
                element_type = element_config.get("type")
                
                if element_type == "num":
                    value = self.generate_num(**{k: v for k, v in element_config.items() if k != "type"}, total_tests=1)[0]
                elif element_type == "string":
                    value = self.generate_string(**{k: v for k, v in element_config.items() if k != "type"}, total_tests=1)[0]
                elif element_type == "bool_or_none":
                    value = self.generate_bool_or_none(**{k: v for k, v in element_config.items() if k != "type"}, total_tests=1)[0]
                elif element_type == "array":
                    value = self.generate_array(**{k: v for k, v in element_config.items() if k != "type"}, total_tests=1)[0]
                elif element_type == "dict":
                    value = self.generate_dict(**{k: v for k, v in element_config.items() if k != "type"}, total_tests=1)[0]
                else:
                    value = None
                
                array.append(value)
            
            results.append(array)
        
        return results
    
    def generate_dict(self, keys, values, total_tests=10):
        """Generate dictionary test cases.
        
        Args:
            keys: List of key configs, each with {"type": "num/string/bool_or_none", ...params}
            values: List of value configs, each with {"type": "num/string/bool_or_none/array/dict", ...params}
            total_tests: Number of dicts to generate
            
        Returns:
            List of dictionaries with generated keys and values
        """
        results = []
        
        for _ in range(total_tests):
            dict_obj = {}
            
            for key_config, value_config in zip(keys, values):
                # Generate key
                key_type = key_config.get("type")
                if key_type == "num":
                    key = self.generate_num(**{k: v for k, v in key_config.items() if k != "type"}, total_tests=1)[0]
                elif key_type == "string":
                    key = self.generate_string(**{k: v for k, v in key_config.items() if k != "type"}, total_tests=1)[0]
                elif key_type == "bool_or_none":
                    key = self.generate_bool_or_none(**{k: v for k, v in key_config.items() if k != "type"}, total_tests=1)[0]
                else:
                    key = None
                
                # Generate value
                value_type = value_config.get("type")
                if value_type == "num":
                    value = self.generate_num(**{k: v for k, v in value_config.items() if k != "type"}, total_tests=1)[0]
                elif value_type == "string":
                    value = self.generate_string(**{k: v for k, v in value_config.items() if k != "type"}, total_tests=1)[0]
                elif value_type == "bool_or_none":
                    value = self.generate_bool_or_none(**{k: v for k, v in value_config.items() if k != "type"}, total_tests=1)[0]
                elif value_type == "array":
                    value = self.generate_array(**{k: v for k, v in value_config.items() if k != "type"}, total_tests=1)[0]
                elif value_type == "dict":
                    value = self.generate_dict(**{k: v for k, v in value_config.items() if k != "type"}, total_tests=1)[0]
                else:
                    value = None
                
                dict_obj[key] = value
            
            results.append(dict_obj)
        
        return results



# Example usage
if __name__ == "__main__":
    generator = TestCaseGenerator(seed=42)
    
    # Generate integers
    print("Integers:", generator.generate_num(lower=1, upper=100, exclude=[13, 42], total_tests=10))
    
    # Generate floats
    print("Floats:", generator.generate_num(lower=0.0, upper=10.0, decimal=2, total_tests=10))
    
    # Generate strings
    print("Strings:", generator.generate_string(lower_len=3, upper_len=10, char_range=(97, 122), 
                                                 exclude=["bad"], total_tests=10))
    
    # Generate strings with random caps
    print("Random caps:", generator.generate_string(lower_len=5, upper_len=8, char_range=(97, 122),
                                                     case="random", total_tests=5))
    
    # Generate bool/None
    print("Bool/None:", generator.generate_bool_or_none(total_tests=10))
    
    # Generate arrays
    print("\nArrays (mixed types):", generator.generate_array(
        elements=[
            {"type": "num", "lower": 0, "upper": 100},
            {"type": "string", "lower_len": 3, "upper_len": 8, "char_range": (97, 122)},
            {"type": "bool_or_none"}
        ],
        total_tests=3
    ))
    
    # Generate nested arrays
    print("\nNested arrays:", generator.generate_array(
        elements=[
            {"type": "array", "elements": [
                {"type": "num", "lower": 0, "upper": 10},
                {"type": "num", "lower": 0, "upper": 10}
            ]},
            {"type": "num", "lower": 50, "upper": 100}
        ],
        total_tests=3
    ))
    
    # Generate dictionaries
    print("\nDictionaries:", generator.generate_dict(
        keys=[
            {"type": "string", "lower_len": 3, "upper_len": 5, "char_range": (97, 122)},
            {"type": "num", "lower": 1, "upper": 100}
        ],
        values=[
            {"type": "string", "lower_len": 5, "upper_len": 10, "char_range": (97, 122)},
            {"type": "bool_or_none"}
        ],
        total_tests=3
    ))
    
    # Generate dict with array values
    print("\nDict with arrays:", generator.generate_dict(
        keys=[
            {"type": "string", "lower_len": 3, "upper_len": 5, "char_range": (97, 122)}
        ],
        values=[
            {"type": "array", "elements": [
                {"type": "num", "lower": 0, "upper": 100},
                {"type": "num", "lower": 0, "upper": 100}
            ]}
        ],
        total_tests=3
    ))
