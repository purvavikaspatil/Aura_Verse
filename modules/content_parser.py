"""
Content Parser Module
Handles parsing of various file types: HTML, PDF, MD, TXT, JSON, CSV
Extracts structured data from mixed unstructured content
"""
import json
import re
import html.parser
from html.parser import HTMLParser
from typing import Dict, List, Any, Optional
import csv
import io


class HTMLDataExtractor(HTMLParser):
    """Extract structured data from HTML content"""
    
    def __init__(self):
        super().__init__()
        self.data = {
            "headings": [],
            "paragraphs": [],
            "links": [],
            "images": [],
            "tables": [],
            "lists": [],
            "metadata": {}
        }
        self.current_tag = None
        self.current_attrs = {}
        self.in_table = False
        self.current_table = []
        self.current_row = []
        self.in_list = False
        self.current_list = []
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        self.current_attrs = dict(attrs)
        
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.in_heading = True
        elif tag == 'table':
            self.in_table = True
            self.current_table = []
        elif tag == 'tr':
            self.current_row = []
        elif tag == 'a':
            href = self.current_attrs.get('href', '')
            if href:
                self.data['links'].append({
                    "url": href,
                    "text": ""
                })
        elif tag == 'img':
            src = self.current_attrs.get('src', '')
            alt = self.current_attrs.get('alt', '')
            self.data['images'].append({
                "src": src,
                "alt": alt
            })
        elif tag in ['ul', 'ol']:
            self.in_list = True
            self.current_list = []
        elif tag == 'li':
            self.in_list_item = True
            
    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.in_heading = False
        elif tag == 'td' or tag == 'th':
            pass  # Cell content handled in handle_data
        elif tag == 'tr':
            if self.current_row:
                self.current_table.append(self.current_row)
                self.current_row = []
        elif tag == 'table':
            if self.current_table:
                self.data['tables'].append(self.current_table)
            self.in_table = False
            self.current_table = []
        elif tag == 'li':
            self.in_list_item = False
        elif tag in ['ul', 'ol']:
            if self.current_list:
                self.data['lists'].append(self.current_list)
            self.in_list = False
            self.current_list = []
            
    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
            
        if self.current_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.data['headings'].append({
                "level": int(self.current_tag[1]),
                "text": text
            })
        elif self.current_tag == 'p':
            self.data['paragraphs'].append(text)
        elif self.current_tag in ['td', 'th']:
            self.current_row.append(text)
        elif self.current_tag == 'li':
            self.current_list.append(text)
        elif self.current_tag == 'a':
            # Update last link's text
            if self.data['links']:
                self.data['links'][-1]['text'] = text
        elif self.current_tag == 'title':
            self.data['metadata']['title'] = text
        elif self.current_tag == 'meta':
            name = self.current_attrs.get('name', '')
            content = self.current_attrs.get('content', '')
            if name:
                self.data['metadata'][name] = content


def parse_html(content: str) -> Dict[str, Any]:
    """Parse HTML content and extract structured data"""
    try:
        parser = HTMLDataExtractor()
        parser.feed(content)
    except Exception as e:
        # If parsing fails, return basic structure
        print(f"HTML parsing warning: {e}")
        parser = HTMLDataExtractor()
        # Try to parse with error recovery
        try:
            parser.feed(content)
        except:
            pass
    
    # Convert to results format
    results = []
    
    # Helper function to ensure all values are JSON-safe
    def safe_value(val):
        """Convert value to JSON-safe type"""
        if val is None:
            return ""
        if isinstance(val, (int, float)):
            # Check for NaN or Infinity
            import math
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                return 0
        return str(val) if not isinstance(val, (str, int, float, bool)) else val
    
    # Add headings as records
    for heading in parser.data.get('headings', []):
        level = heading.get('level', 1)
        text = heading.get('text', '')
        results.append({
            "type": "heading",
            "level": int(level) if isinstance(level, (int, float)) and not (isinstance(level, float) and (level != level or abs(level) == float('inf'))) else 1,
            "text": safe_value(text)
        })
    
    # Add paragraphs
    for para in parser.data.get('paragraphs', []):
        results.append({
            "type": "paragraph",
            "text": safe_value(para)
        })
    
    # Add links
    for link in parser.data.get('links', []):
        results.append({
            "type": "link",
            "url": safe_value(link.get('url', '')),
            "text": safe_value(link.get('text', ''))
        })
    
    # Add images
    for img in parser.data.get('images', []):
        results.append({
            "type": "image",
            "src": safe_value(img.get('src', '')),
            "alt": safe_value(img.get('alt', ''))
        })
    
    # Add tables
    for idx, table in enumerate(parser.data.get('tables', [])):
        if table:
            # First row as headers
            headers = table[0] if table else []
            for row in table[1:]:
                row_dict = {}
                for i, cell in enumerate(row):
                    header = headers[i] if i < len(headers) else f"column_{i}"
                    row_dict[header] = safe_value(cell)
                results.append({
                    "type": "table_row",
                    "table_index": int(idx),
                    **row_dict
                })
    
    # Add lists
    for idx, list_items in enumerate(parser.data.get('lists', [])):
        for item in list_items:
            results.append({
                "type": "list_item",
                "list_index": int(idx),
                "text": safe_value(item)
            })
    
    # Add metadata
    if parser.data.get('metadata'):
        metadata_dict = {}
        for key, value in parser.data['metadata'].items():
            metadata_dict[str(key)] = safe_value(value)
        results.append({
            "type": "metadata",
            **metadata_dict
        })
    
    return {"results": results}


def parse_markdown(content: str) -> Dict[str, Any]:
    """Parse Markdown content and extract structured data"""
    results = []
    lines = content.split('\n')
    
    current_section = None
    current_code_block = []
    in_code_block = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # Headings
        if line_stripped.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line_stripped.lstrip('#').strip()
            results.append({
                "type": "heading",
                "level": level,
                "text": text
            })
        # Code blocks
        elif line_stripped.startswith('```'):
            if in_code_block:
                results.append({
                    "type": "code_block",
                    "language": current_section or "text",
                    "content": "\n".join(current_code_block)
                })
                current_code_block = []
                in_code_block = False
                current_section = None
            else:
                in_code_block = True
                current_section = line_stripped[3:].strip() or "text"
        elif in_code_block:
            current_code_block.append(line)
        # Lists
        elif line_stripped.startswith('-') or line_stripped.startswith('*'):
            text = line_stripped[1:].strip()
            results.append({
                "type": "list_item",
                "text": text
            })
        # Links
        elif '[' in line and '](' in line:
            match = re.search(r'\[([^\]]+)\]\(([^\)]+)\)', line)
            if match:
                results.append({
                    "type": "link",
                    "text": match.group(1),
                    "url": match.group(2)
                })
        # Regular paragraphs
        elif line_stripped:
            results.append({
                "type": "paragraph",
                "text": line_stripped
            })
    
    return {"results": results}


def parse_csv_content(content: str) -> Dict[str, Any]:
    """Parse CSV content"""
    results = []
    try:
        csv_reader = csv.DictReader(io.StringIO(content))
        for row in csv_reader:
            results.append(row)
    except:
        # Try with semicolon delimiter
        try:
            csv_reader = csv.DictReader(io.StringIO(content), delimiter=';')
            for row in csv_reader:
                results.append(row)
        except:
            # Fallback to simple parsing
            lines = content.split('\n')
            if lines:
                headers = [h.strip() for h in lines[0].split(',')]
                for line in lines[1:]:
                    if line.strip():
                        values = [v.strip() for v in line.split(',')]
                        row = {}
                        for i, header in enumerate(headers):
                            row[header] = values[i] if i < len(values) else ""
                        results.append(row)
    
    return {"results": results}


def parse_key_value(content: str) -> List[Dict[str, Any]]:
    """Parse key-value pairs from text"""
    results = []
    # Pattern: key: value or key=value
    patterns = [
        r'([^:=\n]+):\s*([^\n]+)',
        r'([^:=\n]+)=\s*([^\n]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for key, value in matches:
            key = key.strip()
            value = value.strip()
            if key and value:
                results.append({
                    "key": key,
                    "value": value
                })
    
    return results


def parse_mixed_content(content: str, filename: str = "") -> Dict[str, Any]:
    """
    Parse mixed unstructured content.
    Detects and extracts: JSON, HTML, CSV, key-value pairs, raw text
    """
    all_results = []
    
    # Try to detect JSON first
    json_objects = []
    try:
        # Try parsing entire content as JSON
        data = json.loads(content)
        if isinstance(data, list):
            json_objects = data
        elif isinstance(data, dict):
            json_objects = [data]
    except:
        # Try to find JSON objects within the content
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.finditer(json_pattern, content, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match.group())
                json_objects.append(data)
            except:
                pass
    
    for obj in json_objects:
        all_results.append({
            "type": "json_object",
            **obj
        })
    
    # Detect and parse HTML
    if '<html' in content.lower() or '<body' in content.lower() or '<div' in content.lower():
        html_data = parse_html(content)
        all_results.extend(html_data.get("results", []))
    
    # Detect and parse CSV
    if ',' in content and '\n' in content:
        lines = content.split('\n')
        if len(lines) > 1 and ',' in lines[0]:
            # Likely CSV
            csv_data = parse_csv_content(content)
            all_results.extend(csv_data.get("results", []))
    
    # Parse key-value pairs
    kv_pairs = parse_key_value(content)
    for kv in kv_pairs:
        all_results.append({
            "type": "key_value",
            **kv
        })
    
    # If no structured data found, treat as raw text
    if not all_results:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip():
                all_results.append({
                    "type": "text_line",
                    "line_number": i + 1,
                    "content": line.strip()
                })
    
    return {"results": all_results}


def parse_file_content(content: str, filename: str = "") -> Dict[str, Any]:
    """
    Main parser function that determines file type and parses accordingly
    """
    filename_lower = filename.lower() if filename else ""
    
    # Determine file type
    if filename_lower.endswith('.html') or filename_lower.endswith('.htm'):
        return parse_html(content)
    elif filename_lower.endswith('.md') or filename_lower.endswith('.markdown'):
        return parse_markdown(content)
    elif filename_lower.endswith('.csv'):
        return parse_csv_content(content)
    elif filename_lower.endswith('.json'):
        try:
            data = json.loads(content)
            if isinstance(data, list):
                return {"results": data}
            elif isinstance(data, dict):
                return {"results": [data]}
        except:
            pass
    elif filename_lower.endswith('.pdf'):
        # PDF parsing would require PyPDF2 or pdfplumber
        # For now, return as text
        return {
            "results": [{
                "type": "pdf_content",
                "note": "PDF parsing requires additional libraries. Content treated as text.",
                "content": content[:1000]  # First 1000 chars
            }]
        }
    
    # For .txt or unknown types, try mixed content parsing
    return parse_mixed_content(content, filename)

