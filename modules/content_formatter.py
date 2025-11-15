"""
Content Formatter Module
Cleans, organizes, and formats content while preserving original format
"""
import json
import re
from html.parser import HTMLParser
from html import unescape
from typing import Optional


class HTMLFormatter(HTMLParser):
    """Format HTML with proper indentation"""
    
    def __init__(self):
        super().__init__()
        self.output = []
        self.indent_level = 0
        self.indent_size = 2
        self.in_script = False
        self.in_style = False
        
    def handle_starttag(self, tag, attrs):
        indent = " " * (self.indent_level * self.indent_size)
        
        # Self-closing tags
        self_closing = ['br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr']
        
        if tag in ['script', 'style']:
            self.in_script = (tag == 'script')
            self.in_style = (tag == 'style')
        
        # Build attribute string
        attr_str = ""
        if attrs:
            attr_parts = []
            for name, value in attrs:
                if value:
                    attr_parts.append(f'{name}="{value}"')
                else:
                    attr_parts.append(name)
            if attr_parts:
                attr_str = " " + " ".join(attr_parts)
        
        if tag in self_closing:
            self.output.append(f"{indent}<{tag}{attr_str} />")
        else:
            self.output.append(f"{indent}<{tag}{attr_str}>")
            if tag not in ['script', 'style', 'textarea']:
                self.indent_level += 1
    
    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.in_script = False
            self.in_style = False
        
        if tag not in ['br', 'hr', 'img', 'input', 'meta', 'link']:
            self.indent_level = max(0, self.indent_level - 1)
            indent = " " * (self.indent_level * self.indent_size)
            self.output.append(f"{indent}</{tag}>")
    
    def handle_data(self, data):
        if not data.strip():
            return
        
        indent = " " * (self.indent_level * self.indent_size)
        
        if self.in_script or self.in_style:
            # Preserve script/style content as-is but with indentation
            lines = data.split('\n')
            for line in lines:
                if line.strip():
                    self.output.append(f"{indent}{line}")
        else:
            # Regular text content
            lines = data.split('\n')
            for line in lines:
                if line.strip():
                    self.output.append(f"{indent}{line.strip()}")
    
    def get_formatted(self):
        return "\n".join(self.output)


def format_html(content: str) -> str:
    """Format HTML with proper indentation and fix structural issues"""
    try:
        # Try using BeautifulSoup first (if available) to fix HTML structure
        try:
            from bs4 import BeautifulSoup, NavigableString
            soup = BeautifulSoup(content, 'html.parser')
            # BeautifulSoup automatically fixes:
            # - Missing closing tags
            # - Malformed attributes
            # - Improper nesting
            
            # Fix invalid HTML nesting: block elements cannot be inside <p> tags
            # Block-level elements that cannot be inside <p>
            block_elements = ['div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table', 
                            'form', 'fieldset', 'hr', 'pre', 'blockquote']
            
            # Find and fix <p> tags containing block elements
            p_tags_to_fix = []
            for p_tag in soup.find_all('p'):
                # Check if this <p> contains any block elements (directly or nested)
                has_block = False
                for block_elem in block_elements:
                    if p_tag.find(block_elem):
                        has_block = True
                        break
                if has_block:
                    p_tags_to_fix.append(p_tag)
            
            # Fix each problematic <p> tag
            for p_tag in p_tags_to_fix:
                # Get all children
                children = list(p_tag.children)
                
                # Separate text content and block elements
                text_parts = []
                block_elements_found = []
                
                for child in children:
                    if isinstance(child, NavigableString):
                        text_parts.append(child)
                    elif hasattr(child, 'name') and child.name in block_elements:
                        block_elements_found.append(child)
                    else:
                        text_parts.append(child)
                
                # If we found block elements, we need to close the <p> before them
                if block_elements_found:
                    # Keep only text content in the <p>
                    p_tag.clear()
                    for text_part in text_parts:
                        if isinstance(text_part, NavigableString) and text_part.strip():
                            p_tag.append(text_part)
                        elif hasattr(text_part, 'name'):
                            p_tag.append(text_part)
                    
                    # Insert block elements after the <p> tag
                    for block_elem in block_elements_found:
                        block_elem.extract()
                        p_tag.insert_after(block_elem)
                    
                    # If <p> is now empty, remove it
                    if not p_tag.get_text(strip=True):
                        p_tag.decompose()
            
            # Clean up excessive whitespace in text nodes BEFORE prettify
            for text_node in soup.find_all(text=True):
                if isinstance(text_node, NavigableString):
                    parent = text_node.parent
                    if parent and parent.name not in ['script', 'style', 'pre', 'code']:
                        original_text = str(text_node)
                        if original_text.strip():
                            # Normalize whitespace: replace multiple spaces/tabs/newlines with single space
                            cleaned_text = ' '.join(original_text.split())
                            if cleaned_text != original_text:
                                # Replace the text node
                                text_node.replace_with(cleaned_text)
            
            # Pretty print with proper indentation
            formatted = soup.prettify()
            
            # Post-process: clean up any remaining excessive whitespace in formatted output
            # This handles cases where prettify might preserve some whitespace
            import re
            lines = formatted.split('\n')
            cleaned_lines = []
            for line in lines:
                stripped = line.strip()
                # If line contains only text (no tags), it's a text content line
                if stripped and not stripped.startswith('<') and not stripped.endswith('>') and '<' not in stripped:
                    # This is pure text content, normalize whitespace
                    cleaned_text = ' '.join(stripped.split())
                    # Preserve indentation
                    indent = len(line) - len(line.lstrip())
                    cleaned_lines.append(' ' * indent + cleaned_text)
                else:
                    # This line contains tags, keep as is
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
        except ImportError:
            # BeautifulSoup not available, use basic formatter
            print("BeautifulSoup not available. Install with: pip install beautifulsoup4")
            pass
        except Exception as e:
            print(f"BeautifulSoup formatting warning: {e}")
            import traceback
            traceback.print_exc()
            # Fall through to basic formatter
        
        # Basic HTML formatter (fallback)
        formatter = HTMLFormatter()
        formatter.feed(content)
        return formatter.get_formatted()
    except Exception as e:
        print(f"HTML formatting error: {e}")
        # If parsing fails, do basic formatting
        # Remove extra whitespace but preserve structure
        lines = content.split('\n')
        formatted = []
        indent = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted.append("")
                continue
            
            # Adjust indent based on tags
            if stripped.startswith('</'):
                indent = max(0, indent - 1)
            elif stripped.startswith('<') and not stripped.startswith('</') and not stripped.endswith('/>'):
                # Opening tag
                formatted.append(" " * (indent * 2) + stripped)
                if not any(stripped.startswith(f'<{tag}') for tag in ['br', 'hr', 'img', 'input', 'meta', 'link']):
                    indent += 1
            else:
                formatted.append(" " * (indent * 2) + stripped)
                if stripped.startswith('</'):
                    indent = max(0, indent - 1)
        
        return "\n".join(formatted)


def repair_json_with_parser(content: str) -> str:
    """
    More robust JSON repair using character-by-character parsing.
    Handles missing commas, brackets, and other structural issues.
    """
    import re
    
    # First, apply basic fixes
    content = content.strip()
    if content.startswith('\ufeff'):
        content = content[1:]
    
    # Fix typos
    content = re.sub(r'\btru\b', 'true', content)
    content = re.sub(r'\bfals\b', 'false', content)
    content = re.sub(r'\bundefined\b', 'null', content)
    content = re.sub(r'\bNaN\b', 'null', content)
    
    # Remove comments
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Fix single quotes
    content = re.sub(r"'(\w+)'\s*:", r'"\1":', content)
    content = re.sub(r":\s*'([^',}\]]*)'\s*([,}\]])", r': "\1"\2', content)
    
    # Character-by-character repair
    result = []
    i = 0
    in_string = False
    escape_next = False
    stack = []  # Track opening brackets/braces
    
    while i < len(content):
        char = content[i]
        
        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue
        
        if char == '\\':
            escape_next = True
            result.append(char)
            i += 1
            continue
        
        if char == '"':
            in_string = not in_string
            result.append(char)
            i += 1
            continue
        
        if in_string:
            result.append(char)
            i += 1
            continue
        
        # Outside string - handle structure
        if char == '{':
            stack.append('{')
            result.append(char)
        elif char == '[':
            stack.append('[')
            result.append(char)
        elif char == '}':
            if stack and stack[-1] == '{':
                stack.pop()
            result.append(char)
        elif char == ']':
            if stack and stack[-1] == '[':
                stack.pop()
            result.append(char)
        elif char in [' ', '\t', '\n', '\r']:
            result.append(char)
        else:
            result.append(char)
        
        i += 1
    
    # Add missing closing brackets
    while stack:
        closing = '}' if stack.pop() == '{' else ']'
        result.append(closing)
    
    content = ''.join(result)
    
    # Now fix missing commas - look for patterns like: value"key or value{key
    # Pattern: closing quote, number, bool, null, }, ] followed by quote (new key) without comma
    patterns = [
        (r'(")\s*\n\s*(")', r'\1,\n  \2'),  # "value" to "key" (new property)
        (r'(")\s+(")', r'\1, \2'),  # "value" "key" on same line
        (r'(null|true|false)\s*\n\s*(")', r'\1,\n  \2'),  # value to "key"
        (r'(\d+)\s*\n\s*(")', r'\1,\n  \2'),  # number to "key"
        (r'(")\s*\n\s*(\{)', r'\1,\n  \2'),  # "value" to {
        (r'(")\s*\n\s*(\[)', r'\1,\n  \2'),  # "value" to [
        (r'(\})\s*\n\s*(")', r'\1,\n  \2'),  # } to "key"
        (r'(\])\s*\n\s*(")', r'\1,\n  \2'),  # ] to "key"
        (r'(")\s*"([a-zA-Z_])', r'\1, "\2'),  # "value""key" -> "value", "key"
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Remove trailing commas
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    return content


def repair_and_format_json(content: str) -> str:
    """
    Repair malformed JSON and format it properly.
    Fixes: missing brackets, commas, invalid values, broken structure.
    Uses character-by-character parsing for accurate repair.
    """
    import re
    
    # Step 1: Try to parse as-is first (might be valid)
    try:
        data = json.loads(content.strip())
        return json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError:
        pass  # Continue to repair logic
    
    # Step 2: Apply basic fixes
    original_content = content
    content = content.strip()
    if content.startswith('\ufeff'):
        content = content[1:]
    
    # Fix typos FIRST (before other processing)
    content = re.sub(r'\btru\b', 'true', content)
    content = re.sub(r'\bfals\b', 'false', content)
    content = re.sub(r'\bundefined\b', 'null', content)
    content = re.sub(r'\bNaN\b', 'null', content)
    
    # Remove comments
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Fix single quotes
    content = re.sub(r"'(\w+)'\s*:", r'"\1":', content)
    content = re.sub(r":\s*'([^',}\]]*)'\s*([,}\]])", r': "\1"\2', content)
    
    # Step 3: Character-by-character repair with state tracking
    result = []
    i = 0
    in_string = False
    escape_next = False
    stack = []  # Track opening brackets/braces: '{' or '['
    last_char = None
    last_was_value = False  # Track if we just finished a value
    
    while i < len(content):
        char = content[i]
        
        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue
        
        if char == '\\':
            escape_next = True
            result.append(char)
            i += 1
            continue
        
        if char == '"':
            in_string = not in_string
            result.append(char)
            if not in_string:
                last_was_value = True
            i += 1
            continue
        
        if in_string:
            result.append(char)
            i += 1
            continue
        
        # Outside string - handle structure
        if char == '{':
            # Add comma if needed before opening brace
            if last_was_value and result and result[-1] not in [',', ':', '[', '{']:
                result.append(',')
            stack.append('{')
            result.append(char)
            last_was_value = False
        elif char == '[':
            # Add comma if needed before opening bracket
            if last_was_value and result and result[-1] not in [',', ':', '[', '{']:
                result.append(',')
            stack.append('[')
            result.append(char)
            last_was_value = False
        elif char == '}':
            if stack and stack[-1] == '{':
                stack.pop()
            result.append(char)
            last_was_value = False
        elif char == ']':
            if stack and stack[-1] == '[':
                stack.pop()
            result.append(char)
            last_was_value = False
        elif char == ',':
            result.append(char)
            last_was_value = False
        elif char == ':':
            result.append(char)
            last_was_value = False
        elif char in [' ', '\t', '\n', '\r']:
            result.append(char)
        else:
            # Regular character - check if we need comma before it
            if (last_was_value and char not in [',', '}', ']', ' ', '\t', '\n', '\r'] and
                result and result[-1] not in [',', ':', '[', '{', ' ', '\n']):
                # Check if this looks like start of a new key
                if char == '"' or (char.isalnum() and i + 1 < len(content) and 
                                   content[i:i+10].strip().startswith('"')):
                    result.append(',')
            result.append(char)
            # Check if this completes a value (number, bool, null)
            if char.isdigit() or char in ['t', 'f', 'n']:
                # Check if we have a complete value
                remaining = content[i:].strip()
                if (remaining.startswith('true') or remaining.startswith('false') or 
                    remaining.startswith('null') or re.match(r'^\d+', remaining)):
                    last_was_value = True
        
        i += 1
    
    # Add missing closing brackets
    while stack:
        closing = '}' if stack.pop() == '{' else ']'
        result.append(closing)
    
    content = ''.join(result)
    
    # Step 4: More aggressive comma fixing using regex patterns
    # Fix: "value" followed by "key": (new property) - handle newlines and same line
    content = re.sub(r'(")\s*\n\s*(")', r'\1,\n  \2', content)  # "value" to "key" (newline)
    content = re.sub(r'(")\s+(")', r'\1, \2', content)  # "value" "key" (same line, no comma)
    
    # Fix: "key":"value " followed by "key" (missing comma after value with trailing space)
    content = re.sub(r'(":\s*"[^"]*")\s+(")', r'\1, \2', content)
    
    # Fix: number/bool/null followed by "key":
    content = re.sub(r'(null|true|false|\d+)\s*\n\s*(")', r'\1,\n  \2', content)
    content = re.sub(r'(null|true|false|\d+)\s+(")', r'\1, \2', content)
    
    # Fix: } or ] followed by "key":
    content = re.sub(r'(\})\s*\n\s*(")', r'\1,\n  \2', content)
    content = re.sub(r'(\])\s*\n\s*(")', r'\1,\n  \2', content)
    
    # Fix: "value" followed by { or [
    content = re.sub(r'(")\s*\n\s*(\{)', r'\1,\n  \2', content)
    content = re.sub(r'(")\s*\n\s*(\[)', r'\1,\n  \2', content)
    
    # Step 4b: Line-by-line analysis for more complex cases
    lines = content.split('\n')
    repaired_lines = []
    in_array = False
    array_depth = 0
    brace_depth = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        original_line = line
        
        # Track nesting depth
        brace_depth += stripped.count('{') - stripped.count('}')
        array_depth += stripped.count('[') - stripped.count(']')
        
        if array_depth > 0:
            in_array = True
        else:
            in_array = False
        
        # Skip standalone comma lines
        if stripped in [',', ',,']:
            # If next line is a property and we're in array, close array first
            if i + 1 < len(lines):
                next_stripped = lines[i + 1].strip()
                if next_stripped.startswith('"') and ':' in next_stripped and in_array:
                    repaired_lines.append('],')
                    in_array = False
                    array_depth = 0
            continue
        
        repaired_lines.append(original_line)
        
        # Check next line for missing commas
        if i + 1 < len(lines):
            next_stripped = lines[i + 1].strip()
            
            # Skip if next is just a comma
            if next_stripped == ',':
                if i + 2 < len(lines):
                    next_stripped = lines[i + 2].strip()
                else:
                    continue
            
            # Case 1: Array item "item" followed by property "key": (exit array)
            if (in_array and stripped.startswith('"') and stripped.endswith('"') and 
                ':' not in stripped and next_stripped.startswith('"') and ':' in next_stripped):
                repaired_lines[-1] = original_line.rstrip() + '],'
                in_array = False
                array_depth = 0
            
            # Case 2: "key": "value " followed by "key" (missing comma in object)
            elif (stripped.endswith('"') and ':' in stripped and 
                  not stripped.endswith('",') and next_stripped.startswith('"') and ':' in next_stripped):
                repaired_lines[-1] = original_line.rstrip() + ','
            
            # Case 3: "value" (standalone) followed by "key": (in object, not array)
            elif (not in_array and stripped.startswith('"') and stripped.endswith('"') and 
                  ':' not in stripped and next_stripped.startswith('"') and ':' in next_stripped):
                repaired_lines[-1] = original_line.rstrip() + ','
    
    content = '\n'.join(repaired_lines)
    
    # Step 5: Remove trailing commas
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    # Step 6: Remove standalone comma lines
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip() not in [',', ',,']:
            cleaned_lines.append(line)
    content = '\n'.join(cleaned_lines)
    
    # Step 7: Balance brackets
    open_braces = content.count('{')
    close_braces = content.count('}')
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    
    if open_braces > close_braces:
        content = content.rstrip() + '\n' + '}' * (open_braces - close_braces)
    if open_brackets > close_brackets:
        content = content.rstrip() + '\n' + ']' * (open_brackets - close_brackets)
    
    # Step 8: Try to parse
    try:
        data = json.loads(content)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except json.JSONDecodeError as e:
        # Final attempt: try to extract valid JSON structure
        try:
            start_idx = content.find('{')
            if start_idx == -1:
                start_idx = content.find('[')
            
            if start_idx >= 0:
                partial = content[start_idx:]
                # Balance brackets
                brace_diff = partial.count('{') - partial.count('}')
                bracket_diff = partial.count('[') - partial.count(']')
                if brace_diff > 0:
                    partial += '\n' + '}' * brace_diff
                if bracket_diff > 0:
                    partial += '\n' + ']' * bracket_diff
                
                data = json.loads(partial)
                return json.dumps(data, indent=2, ensure_ascii=False)
        except:
            pass
        
        # Return repaired content even if not fully valid
        return content.strip()


def format_json(content: str) -> str:
    """Format JSON with proper indentation and repair malformed JSON"""
    return repair_and_format_json(content)


def format_markdown(content: str) -> str:
    """Format Markdown with consistent spacing"""
    lines = content.split('\n')
    formatted = []
    prev_empty = False
    
    for line in lines:
        stripped = line.strip()
        
        # Add spacing around headers
        if stripped.startswith('#'):
            if formatted and not prev_empty:
                formatted.append("")
            formatted.append(line.rstrip())
            prev_empty = True
        # Add spacing around code blocks
        elif stripped.startswith('```'):
            if not prev_empty:
                formatted.append("")
            formatted.append(line.rstrip())
            prev_empty = True
        # Regular content
        elif stripped:
            formatted.append(line.rstrip())
            prev_empty = False
        # Empty lines - limit to max 2 consecutive
        else:
            if not prev_empty or (formatted and formatted[-1] != ""):
                formatted.append("")
            prev_empty = True
    
    return "\n".join(formatted)


def format_xml(content: str) -> str:
    """Format XML with proper indentation"""
    try:
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(content)
        return dom.toprettyxml(indent="  ")
    except:
        # Basic XML formatting
        lines = content.split('\n')
        formatted = []
        indent = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            if stripped.startswith('</'):
                indent = max(0, indent - 1)
                formatted.append(" " * (indent * 2) + stripped)
            elif stripped.startswith('<') and not stripped.endswith('/>'):
                formatted.append(" " * (indent * 2) + stripped)
                indent += 1
            else:
                formatted.append(" " * (indent * 2) + stripped)
        
        return "\n".join(formatted)


def format_csv(content: str) -> str:
    """Format CSV with consistent spacing"""
    lines = content.split('\n')
    formatted = []
    
    for line in lines:
        if not line.strip():
            formatted.append("")
            continue
        
        # Split by comma, but handle quoted values
        parts = []
        current = ""
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
                current += char
            elif char == ',' and not in_quotes:
                parts.append(current.strip())
                current = ""
            else:
                current += char
        
        if current:
            parts.append(current.strip())
        
        # Join with consistent spacing
        formatted.append(", ".join(parts))
    
    return "\n".join(formatted)


def format_text(content: str) -> str:
    """Format plain text with consistent spacing"""
    lines = content.split('\n')
    formatted = []
    prev_empty = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped:
            # Remove trailing whitespace
            formatted.append(line.rstrip())
            prev_empty = False
        else:
            # Limit consecutive empty lines to 2
            if not prev_empty or (formatted and formatted[-1] != ""):
                formatted.append("")
            prev_empty = True
    
    return "\n".join(formatted)


def format_content(content: str, filename: str = "") -> str:
    """
    Format content based on file type while preserving format
    Returns raw formatted content (not JSON)
    """
    if not filename:
        # Try to detect format from content
        content_lower = content.lower().strip()
        
        if content_lower.startswith('{') or content_lower.startswith('['):
            # Always try to format/repair JSON (format_json handles both valid and malformed)
            return format_json(content)
        
        if '<html' in content_lower or '<body' in content_lower or '<div' in content_lower:
            return format_html(content)
        
        if content_lower.startswith('<?xml'):
            return format_xml(content)
    
    filename_lower = filename.lower() if filename else ""
    
    # Format based on file extension
    if filename_lower.endswith('.html') or filename_lower.endswith('.htm'):
        return format_html(content)
    elif filename_lower.endswith('.json'):
        return format_json(content)
    elif filename_lower.endswith('.md') or filename_lower.endswith('.markdown'):
        return format_markdown(content)
    elif filename_lower.endswith('.xml'):
        return format_xml(content)
    elif filename_lower.endswith('.csv'):
        return format_csv(content)
    elif filename_lower.endswith('.txt') or filename_lower.endswith('.text'):
        return format_text(content)
    else:
        # Default: try to detect and format, otherwise just clean text
        content_lower = content.lower().strip()
        
        if content_lower.startswith('{') or content_lower.startswith('['):
            # Always try to format/repair JSON (format_json handles both valid and malformed)
            return format_json(content)
        
        if '<html' in content_lower or '<body' in content_lower:
            return format_html(content)
        
        if content_lower.startswith('<?xml'):
            return format_xml(content)
        
        # Default: clean text formatting
        return format_text(content)

