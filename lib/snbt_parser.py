"""
    @author RazrCraft
    @create date 2025-09-13 16:57:05
    @modify date 2025-09-15 19:41:59
    @desc Minecraft SNBT (Stringified Named Binary Tag) parser and manipulator.
 """
import re
import json
from typing import Union, Dict, List, Any


class SNBTParser:
    """
    Minecraft SNBT (Stringified Named Binary Tag) parser and manipulator.
    
    Supports parsing SNBT strings into Python objects and converting back to SNBT format.
    Handles Minecraft-specific data types like typed numbers (3s, 4.5f, 1L, etc.).
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
    
    def to_snbt(self, obj: Any, pretty: bool = False, indent: int = 0) -> str:
        """
        Convert a Python object back to SNBT format.
        
        Args:
            obj: Python object to convert
            pretty: Whether to format with indentation
            indent: Current indentation level (for internal use)
            
        Returns:
            str: SNBT string representation
        """
        if obj is None:
            return ""
        
        if isinstance(obj, bool):
            return "true" if obj else "false"
        
        if isinstance(obj, (int, float)):
            return str(obj)
        
        if isinstance(obj, str):
            # Use quotes if the string contains special characters
            if self.unquoted_string_pattern.match(obj) and obj not in ['true', 'false']:
                return obj
            else:
                return f'"{obj}"'
        
        if isinstance(obj, dict):
            return self._dict_to_snbt(obj, pretty, indent)
        
        if isinstance(obj, list):
            return self._list_to_snbt(obj, pretty, indent)
        
        return str(obj)
    
    def _dict_to_snbt(self, obj: dict, pretty: bool, indent: int) -> str:
        """Convert dictionary to SNBT compound tag."""
        if not obj:
            return "{}"
        
        items = []
        for key, value in obj.items():
            key_str = key if self.unquoted_string_pattern.match(key) else f'"{key}"'
            value_str = self.to_snbt(value, pretty, indent + 1)
            items.append(f"{key_str}:{value_str}")
        
        if pretty:
            indent_str = "  " * indent
            inner_indent_str = "  " * (indent + 1)
            content = f",\n{inner_indent_str}".join(items)
            return f"{{\n{inner_indent_str}{content}\n{indent_str}}}"
        else:
            return "{" + ",".join(items) + "}"
    
    def _list_to_snbt(self, obj: list, pretty: bool, indent: int) -> str:
        """Convert list to SNBT list tag."""
        if not obj:
            return "[]"
        
        items = [self.to_snbt(item, pretty, indent + 1) for item in obj]
        
        if pretty:
            indent_str = "  " * indent
            inner_indent_str = "  " * (indent + 1)
            content = f",\n{inner_indent_str}".join(items)
            return f"[\n{inner_indent_str}{content}\n{indent_str}]"
        else:
            return "[" + ",".join(items) + "]"
    
    def get(self, obj: dict, path: str, default=None) -> Any:
        """
        Get a value from nested SNBT data using dot notation.
        
        Args:
            obj: Parsed SNBT object (dictionary)
            path: Dot-separated path (e.g., "player.Inventory.0.Count")
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
    
    def set(self, obj: dict, path: str, value: Any) -> None:
        """
        Set a value in nested SNBT data using dot notation.
        
        Args:
            obj: Parsed SNBT object (dictionary)
            path: Dot-separated path (e.g., "player.Health")
            value: Value to set
        """
        if not isinstance(obj, dict):
            return
        
        parts = path.split('.')
        current = obj
        
        for part in parts[:-1]:
            if isinstance(current, dict):
                if part not in current:
                    current[part] = {}
                current = current[part]
            else:
                return
        
        if isinstance(current, dict):
            current[parts[-1]] = value


# Global parser instance for convenience functions
_parser = SNBTParser()


# Example usage and utility functions
def parse_snbt(snbt_string: str) -> Union[Dict, List, Any]:
    """Quick function to parse SNBT string."""
    return _parser.parse(snbt_string)


def to_snbt(obj: Any, pretty: bool = False) -> str:
    """Quick function to convert object to SNBT string."""
    return _parser.to_snbt(obj, pretty)


def get_nbt_value(obj: dict, path: str, default=None) -> Any:
    """Quick function to get value from parsed SNBT using dot notation."""
    return _parser.get(obj, path, default)


def set_nbt_value(obj: dict, path: str, value: Any) -> None:
    """Quick function to set value in parsed SNBT using dot notation."""
    _parser.set(obj, path, value)


# Example usage
if __name__ == "__main__":
    # Example entity SNBT data
    entity_snbt = """{
        CustomName: '"Bob the Builder"',
        Health: 20.0f,
        Pos: [100.5d, 64.0d, 200.0d],
        Motion: [0.0d, 0.0d, 0.0d],
        Inventory: [
            {Slot: 0b, Count: 64b, id: "minecraft:stone"},
            {Slot: 1b, Count: 32b, id: "minecraft:dirt"}
        ],
        Tags: ["custom_mob", "builder"],
        Attributes: {
            Speed: 0.7f,
            MaxHealth: 20.0f
        }
    }"""
    
    # Parse the SNBT
    data = _parser.parse(entity_snbt)
    
    print("Parsed data:")
    print(json.dumps(data, indent=2, default=str))
    
    # Get specific values
    print(f"\nCustom Name: {_parser.get(data, 'CustomName')}")
    print(f"Health: {_parser.get(data, 'Health')}")
    print(f"First inventory item: {_parser.get(data, 'Inventory.0.id')}")
    print(f"Speed attribute: {_parser.get(data, 'Attributes.Speed')}")
    
    # Modify data
    _parser.set(data, 'Health', 15.0)
    _parser.set(data, 'CustomName', '"Bob the Destroyer"')
    
    # Convert back to SNBT
    print("\nModified SNBT:")
    print(_parser.to_snbt(data, pretty=True))
