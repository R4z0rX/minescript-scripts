"""
    @author RazrCraft
    @create date 2025-09-13 17:09:46
    @modify date 2025-09-15 19:41:59
    @desc Minecraft SNBT (Stringified Named Binary Tag) parser.
 """
import re
from typing import Union, Dict, List, Any


class SNBTParser:
    """
    Minecraft SNBT (Stringified Named Binary Tag) parser.
    
    Supports parsing SNBT strings into Python objects for data extraction.
    """
    
    def __init__(self):
        # Regex patterns for different NBT data types
        self.typed_number_pattern = re.compile(r'^(-?\d*\.?\d+)([bslfdBSLFD])$')
        self.unquoted_string_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    
    def parse(self, snbt_string: str) -> Union[Dict, List, Any]:
        """
        Parse an SNBT string into a Python object.
        
        Args:
            snbt_string (str): The SNBT string to parse
            
        Returns:
            Union[Dict, List, Any]: Parsed Python object
        """
        snbt_string = snbt_string.strip()
        if not snbt_string:
            return None
            
        return self._parse_value(snbt_string)
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse a single value (could be compound, list, or primitive)."""
        value_str = value_str.strip()
        
        if not value_str:
            return None
        
        # Compound tag (object)
        if value_str.startswith('{') and value_str.endswith('}'):
            return self._parse_compound(value_str[1:-1])
        
        # List tag (array)
        if value_str.startswith('[') and value_str.endswith(']'):
            return self._parse_list(value_str[1:-1])
        
        # Primitive values
        return self._parse_primitive(value_str)
    
    def _parse_compound(self, content: str) -> Dict[str, Any]:
        """Parse compound tag content (inside curly braces)."""
        if not content.strip():
            return {}
        
        result = {}
        pairs = self._split_key_value_pairs(content)
        
        for pair in pairs:
            if ':' not in pair:
                continue
            
            key, value = pair.split(':', 1)
            key = self._parse_key(key.strip())
            value = self._parse_value(value.strip())
            result[key] = value
        
        return result
    
    def _parse_list(self, content: str) -> List[Any]:
        """Parse list tag content (inside square brackets)."""
        if not content.strip():
            return []
        
        items = self._split_list_items(content)
        return [self._parse_value(item.strip()) for item in items if item.strip()]
    
    def _parse_primitive(self, value_str: str) -> Any:
        """Parse primitive values (strings, numbers, booleans)."""
        value_str = value_str.strip()
        
        # Boolean values
        if value_str.lower() == 'true':
            return True
        if value_str.lower() == 'false':
            return False
        
        # Quoted strings
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Typed numbers (e.g., 3s, 4.5f, 1L)
        match = self.typed_number_pattern.match(value_str)
        if match:
            number_str, type_suffix = match.groups()
            return self._convert_typed_number(number_str, type_suffix.lower())
        
        # Regular numbers
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
        
        # Unquoted strings (must be valid identifiers)
        if self.unquoted_string_pattern.match(value_str):
            return value_str
        
        # Default to string if nothing else matches
        return value_str
    
    def _parse_key(self, key_str: str) -> str:
        """Parse a key (remove quotes if present)."""
        key_str = key_str.strip()
        if (key_str.startswith('"') and key_str.endswith('"')) or \
           (key_str.startswith("'") and key_str.endswith("'")):
            return key_str[1:-1]
        return key_str
    
    def _convert_typed_number(self, number_str: str, type_suffix: str) -> Union[int, float]:
        """Convert typed numbers to appropriate Python types."""
        if type_suffix in ['b', 's', 'l']:  # byte, short, long
            return int(float(number_str))
        elif type_suffix in ['f', 'd']:  # float, double
            return float(number_str)
        return float(number_str) if '.' in number_str else int(number_str)
    
    def _split_key_value_pairs(self, content: str) -> List[str]:
        """Split compound content into key-value pairs, respecting nested structures."""
        pairs = []
        current_pair = ""
        brace_depth = 0
        bracket_depth = 0
        in_quotes = False
        quote_char = None
        
        for char in content:
            if not in_quotes:
                if char in ['"', "'"]:
                    in_quotes = True
                    quote_char = char
                elif char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1
                elif char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth -= 1
                elif char == ',' and brace_depth == 0 and bracket_depth == 0:
                    pairs.append(current_pair.strip())
                    current_pair = ""
                    continue
            else:
                if char == quote_char:
                    in_quotes = False
                    quote_char = None
            
            current_pair += char
        
        if current_pair.strip():
            pairs.append(current_pair.strip())
        
        return pairs
    
    def _split_list_items(self, content: str) -> List[str]:
        """Split list content into items, respecting nested structures."""
        items = []
        current_item = ""
        brace_depth = 0
        bracket_depth = 0
        in_quotes = False
        quote_char = None
        
        for char in content:
            if not in_quotes:
                if char in ['"', "'"]:
                    in_quotes = True
                    quote_char = char
                elif char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1
                elif char == '[':
                    bracket_depth += 1
                elif char == ']':
                    bracket_depth -= 1
                elif char == ',' and brace_depth == 0 and bracket_depth == 0:
                    items.append(current_item.strip())
                    current_item = ""
                    continue
            else:
                if char == quote_char:
                    in_quotes = False
                    quote_char = None
            
            current_item += char
        
        if current_item.strip():
            items.append(current_item.strip())
        
        return items
    
    def get(self, obj: dict, path: str, default=None) -> Any:
        """
        Get a value from nested SNBT data using dot notation.
        
        Args:
            obj: Parsed SNBT object (dictionary)
            path: Dot-separated path (e.g., "Inventory.0.id")
            default: Default value if path not found
            
        Returns:
            Any: Value at the specified path or default
        """
        if not isinstance(obj, dict):
            return default
        
        current = obj
        parts = path.split('.')
        
        for part in parts:
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    return default
            elif isinstance(current, list):
                try:
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return default
                except ValueError:
                    return default
            else:
                return default
        
        return current


# Global parser instance for convenience functions
_parser = SNBTParser()


def parse_snbt(snbt_string: str) -> Union[Dict, List, Any]:
    """Parse SNBT string into Python object."""
    return _parser.parse(snbt_string)


def get_nbt_value(obj: dict, path: str, default=None) -> Any:
    """Get value from parsed SNBT using dot notation."""
    return _parser.get(obj, path, default)


# Example usage
if __name__ == "__main__":
    # Example entity SNBT data
    entity_snbt = """{
        CustomName: '"Bob the Builder"',
        Health: 20.0f,
        Inventory: [
            {Slot: 0b, Count: 64b, id: "minecraft:stone"},
            {Slot: 1b, Count: 32b, id: "minecraft:dirt"}
        ],
        Attributes: {Speed: 0.7f, MaxHealth: 20.0f}
    }"""
    
    # Parse and extract values
    e_snbt = parse_snbt(entity_snbt)
    slot0 = get_nbt_value(e_snbt, "Inventory.0")
    s0_id = get_nbt_value(slot0, "id")
    s0_count = get_nbt_value(slot0, "count")
    health = get_nbt_value(e_snbt, "Health")
    name = get_nbt_value(e_snbt, "CustomName")
    speed = get_nbt_value(e_snbt, "Attributes.Speed")
    
    print(f"First inventory slot item: {slot0}")
    print(f"First inventory slot item id: {s0_id}")
    print(f"First inventory slot item count: {s0_count}")
    print(f"Entity health: {health}")
    print(f"Custom name: {name}")
    print(f"Speed: {speed}")
