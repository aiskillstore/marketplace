# -*- coding: utf-8 -*-
"""
Parsers for extracting configuration from HTML and slide data from JS
"""

import re
import json
from pathlib import Path


class ConfigParser:
    """
    Extracts ANIMATION_PRESETS and COMPONENT_DEFAULTS from presentation.html
    """
    
    def __init__(self, html_path: str):
        self.html_path = Path(html_path)
        self._animation_presets = None
        self._component_defaults = None
        self._css_variables = None
        self._parse()
    
    def _parse(self):
        """Parse the HTML file and extract configurations"""
        content = self.html_path.read_text(encoding='utf-8')
        
        # Extract ANIMATION_PRESETS
        self._animation_presets = self._extract_animation_presets(content)
        
        # Extract COMPONENT_DEFAULTS
        self._component_defaults = self._extract_component_defaults(content)
        
        # Extract CSS variables
        self._css_variables = self._extract_css_variables(content)
    
    def _extract_animation_presets(self, content: str) -> dict:
        """Extract ANIMATION_PRESETS from JavaScript"""
        # Pattern to match: const ANIMATION_PRESETS = { ... };
        pattern = r'const\s+ANIMATION_PRESETS\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\};'
        match = re.search(pattern, content)
        
        if not match:
            # Return default presets if not found
            return self._default_animation_presets()
        
        try:
            js_obj = '{' + match.group(1) + '}'
            return self._js_to_python(js_obj)
        except:
            return self._default_animation_presets()
    
    def _extract_component_defaults(self, content: str) -> dict:
        """Extract COMPONENT_DEFAULTS from JavaScript"""
        # Pattern to match: const COMPONENT_DEFAULTS = { ... };
        pattern = r'const\s+COMPONENT_DEFAULTS\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\};'
        match = re.search(pattern, content)
        
        if not match:
            return self._default_component_defaults()
        
        try:
            js_obj = '{' + match.group(1) + '}'
            return self._js_to_python(js_obj)
        except:
            return self._default_component_defaults()
    
    def _extract_css_variables(self, content: str) -> dict:
        """Extract CSS custom properties from :root"""
        variables = {}
        
        # Find :root block
        root_pattern = r':root\s*\{([^}]+)\}'
        match = re.search(root_pattern, content)
        
        if match:
            root_content = match.group(1)
            # Extract --variable-name: value pairs
            var_pattern = r'--([a-zA-Z0-9-]+)\s*:\s*([^;]+);'
            for var_match in re.finditer(var_pattern, root_content):
                name = var_match.group(1)
                value = var_match.group(2).strip()
                variables[name] = value
        
        return variables
    
    def _js_to_python(self, js_str: str) -> dict:
        """Convert JavaScript object literal to Python dict"""
        # Remove comments
        js_str = re.sub(r'//.*$', '', js_str, flags=re.MULTILINE)
        
        # Add quotes to unquoted keys
        js_str = re.sub(r'(\s)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', js_str)
        
        # Replace single quotes with double quotes
        js_str = js_str.replace("'", '"')
        
        # Remove trailing commas
        js_str = re.sub(r',(\s*[}\]])', r'\1', js_str)
        
        return json.loads(js_str)
    
    def _default_animation_presets(self) -> dict:
        """Default animation presets if parsing fails"""
        return {
            'fadeIn': {'transform': 'none', 'initialOpacity': 0},
            'slideUp': {'transform': 'translateY(30px)', 'initialOpacity': 0},
            'slideDown': {'transform': 'translateY(-30px)', 'initialOpacity': 0},
            'slideLeft': {'transform': 'translateX(30px)', 'initialOpacity': 0},
            'slideRight': {'transform': 'translateX(-30px)', 'initialOpacity': 0},
            'scaleIn': {'transform': 'scale(0.9)', 'initialOpacity': 0},
            'zoomIn': {'transform': 'scale(0.5)', 'initialOpacity': 0},
            'flipIn': {'transform': 'perspective(400px) rotateX(-10deg)', 'initialOpacity': 0}
        }
    
    def _default_component_defaults(self) -> dict:
        """Default component animation settings"""
        return {
            'comparison': {'preset': 'slideUp', 'duration': 600},
            'terminal': {'preset': 'scaleIn', 'duration': 500},
            'quote': {'preset': 'scaleIn', 'duration': 400},
            'assumptions': {'preset': 'fadeIn', 'duration': 500},
            'timeline': {'preset': 'fadeIn', 'duration': 500, 'stagger': 100},
            'stats': {'preset': 'slideUp', 'duration': 400},
            'valueCards': {'preset': 'slideUp', 'duration': 500, 'stagger': 150},
            'competitionBox': {'preset': 'slideUp', 'duration': 500},
            'strategyBox': {'preset': 'slideUp', 'duration': 500},
            'ending': {'preset': 'scaleIn', 'duration': 600}
        }
    
    @property
    def animation_presets(self) -> dict:
        return self._animation_presets
    
    @property
    def component_defaults(self) -> dict:
        return self._component_defaults
    
    @property
    def css_variables(self) -> dict:
        return self._css_variables


class DataParser:
    """
    Parses SLIDES array from slides-data.js
    """
    
    def __init__(self, js_path: str):
        self.js_path = Path(js_path)
        self._slides = None
        self._parse()
    
    def _parse(self):
        """Parse the JavaScript file and extract SLIDES array"""
        content = self.js_path.read_text(encoding='utf-8')
        
        # Extract SLIDES array
        self._slides = self._extract_slides(content)
    
    def _extract_slides(self, content: str) -> list:
        """Extract SLIDES array from JavaScript"""
        # Pattern to match: const SLIDES = [ ... ];
        # Need to handle nested structures carefully
        
        # Find the start of SLIDES array
        match = re.search(r'const\s+SLIDES\s*=\s*\[', content)
        if not match:
            print("Warning: Could not find SLIDES array, using fallback data")
            return self._fallback_slides()
        
        start_idx = match.end() - 1  # Include the opening bracket
        
        # Find matching closing bracket
        bracket_count = 0
        end_idx = start_idx
        for i in range(start_idx, len(content)):
            if content[i] == '[':
                bracket_count += 1
            elif content[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    end_idx = i + 1
                    break
        
        js_array = content[start_idx:end_idx]
        
        try:
            return self._js_array_to_python(js_array)
        except Exception as e:
            print(f"Warning: Failed to parse SLIDES: {e}, using fallback data")
            return self._fallback_slides()
    
    def _js_array_to_python(self, js_str: str) -> list:
        """Convert JavaScript array literal to Python list"""
        # Remove multi-line comments first (they're safe to remove)
        js_str = re.sub(r'/\*[\s\S]*?\*/', '', js_str)
        
        # Remove single-line comments BUT preserve URLs (http://, https://)
        # Strategy: only remove // comments that are NOT preceded by : (which indicates URL protocol)
        # Pattern: // at start of line or preceded by whitespace (not colon)
        js_str = re.sub(r'(?<![:\"\'])//.*$', '', js_str, flags=re.MULTILINE)
        
        # Add quotes to unquoted keys (object property names)
        js_str = re.sub(r'(\{|\,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', js_str)
        
        # Replace single quotes with double quotes (careful with content)
        js_str = js_str.replace("'", '"')
        
        # Remove trailing commas before ] or }
        js_str = re.sub(r',(\s*[}\]])', r'\1', js_str)
        
        return json.loads(js_str)
    
    def _fallback_slides(self) -> list:
        """Fallback slide data if parsing fails"""
        return [
            {
                "badge": {"icon": "\u2726", "text": "AI STRATEGY 2026"},
                "title": {"text": "\u8303\u5f0f\u8f6c\u79fb", "gradient": True},
                "subtitle": "\u4ece\u300c\u77f3\u6cb9\u65f6\u4ee3\u300d\u5230\u300c\u667a\u80fd\u6d8c\u73b0\u300d\u7684\u6218\u7565\u91cd\u6784",
                "clickHint": "\u70b9\u51fb\u5f00\u542f\u63a2\u7d22",
                "elements": [
                    {
                        "step": 1,
                        "type": "comparison",
                        "left": {
                            "icon": "\u2b21",
                            "title": "19\u4e16\u7eaa\uff1a\u77f3\u6cb9\u9769\u547d",
                            "items": ["\u9a6c\u8f66 \u2192 \u6c7d\u8f66", "\u4eba\u529b \u2192 \u673a\u68b0\u529b", "\u5c40\u90e8\u80fd\u6e90 \u2192 \u5168\u7403\u7535\u7f51"]
                        },
                        "right": {
                            "icon": "\u2726",
                            "title": "21\u4e16\u7eaa\uff1aAI\u9769\u547d",
                            "items": ["\u4eba\u529b\u601d\u8003 \u2192 AI\u534f\u540c", "\u5c40\u90e8\u667a\u80fd \u2192 \u6cdb\u5728\u667a\u80fd", "\u56fa\u5b9a\u6d41\u7a0b \u2192 \u81ea\u9002\u5e94\u7cfb\u7edf"]
                        }
                    },
                    {
                        "step": 2,
                        "type": "terminal",
                        "content": [
                            {"type": "prompt", "text": "AI_STRATEGY > "},
                            {"type": "text", "text": "Paradigm_Shift = "},
                            {"type": "highlight", "text": "REDEFINE_ASSUMPTIONS"},
                            {"type": "text", "text": " + "},
                            {"type": "highlight", "text": "REINVENT_WORKFLOW"},
                            {"type": "cursor"}
                        ]
                    },
                    {
                        "step": 3,
                        "type": "quote",
                        "text": "\u201c\u4e0d\u662f\u5728\u65e7\u8d5b\u9053\u4e0a\u8dd1\u5f97\u66f4\u5feb\uff0c\u800c\u662f\u5207\u6362\u5230\u5b8c\u5168\u4e0d\u540c\u7684\u7ef4\u5ea6\u3002\u201d",
                        "author": {"icon": "\u2726", "text": "Paradigm Shift"}
                    }
                ]
            },
            {
                "badge": {"icon": "\u2727", "text": "BREAKING LIMITS"},
                "title": {"text": "AI\uff1a\u6253\u7834\u4e0d\u53ef\u80fd\u8fb9\u754c"},
                "clickHint": "\u70b9\u51fb\u89e3\u6784\u4f20\u7edf\u5047\u8bbe",
                "elements": [
                    {
                        "step": 1,
                        "type": "assumptions",
                        "revealStep": 2,
                        "items": [
                            {"old": "\u2715 \u521b\u610f\u662f\u4eba\u7c7b\u6700\u540e\u7684\u5821\u5792", "new": "\u2192 \u591a\u6a21\u6001\u751f\u6210 (AIGC) \u7206\u53d1"},
                            {"old": "\u2715 \u590d\u6742\u51b3\u7b56\u5fc5\u987b\u4f9d\u8d56\u76f4\u89c9", "new": "\u2192 \u6570\u636e\u9a71\u52a8\u7684\u63a8\u7406\u4e0e\u89c4\u5212"},
                            {"old": "\u2715 \u4e2a\u6027\u5316\u670d\u52a1 = \u9ad8\u4eba\u529b\u6210\u672c", "new": "\u2192 \u89c4\u6a21\u5316\u7684\u300c\u5343\u4eba\u5343\u9762\u300d"},
                            {"old": "\u2715 \u77e5\u8bc6\u83b7\u53d6\u5b58\u5728\u5929\u7136\u58c1\u5792", "new": "\u2192 \u8bed\u4e49\u641c\u7d22\u4e0e\u5b9e\u65f6\u77e5\u8bc6\u5408\u6210"}
                        ]
                    },
                    {
                        "step": 3,
                        "type": "quote",
                        "text": "\u300c\u5f53\u5047\u8bbe\u88ab\u6253\u7834\uff0c\u8fb9\u754c\u5373\u6210\u4e3a\u65b0\u7684\u8d77\u8dd1\u7ebf\u300d",
                        "gradient": True,
                        "author": {"icon": "\u2726", "text": "The New Reality"}
                    }
                ]
            },
            {
                "badge": {"icon": "\u25c8", "text": "PRODUCT EVOLUTION"},
                "title": {"text": "2026\uff1aAI\u4ea7\u54c1\u6f14\u8fdb\u8def\u5f84"},
                "clickHint": "\u70b9\u51fb\u67e5\u770b\u8fdb\u5316\u9636\u6bb5",
                "elements": [
                    {
                        "step": 1,
                        "type": "timeline",
                        "items": [
                            {"activeStep": 1, "badge": "Phase 1", "icon": "\u25cb", "title": "\u5bf9\u8bdd\u5373\u4ea7\u54c1", "desc": "Prompt Engineering", "case": "\u4ea4\u4e92\u91cd\u6784\uff1aNewIdea"},
                            {"activeStep": 2, "badge": "Phase 2", "icon": "\u25d0", "title": "\u77e5\u8bc6\u5373\u4ea7\u54c1", "desc": "RAG & Knowledge Base", "case": "\u4e13\u4e1a\u6df1\u6316\uff1aDeepSeek+PubMed"},
                            {"activeStep": 3, "badge": "Phase 3", "icon": "\u25d1", "title": "\u6d41\u7a0b\u5373\u4ea7\u54c1", "desc": "AI Agents Workflow", "case": "\u6548\u7387\u95ed\u73af\uff1aMonica / Pollo"},
                            {"activeStep": 4, "badge": "Phase 4", "badgeCurrent": True, "icon": "\u25cf", "iconFilled": True, "title": "\u80fd\u529b\u5373\u4ea7\u54c1", "desc": "Autonomous Skills", "case": "\u7ec8\u6781\u5f62\u6001\uff1aClaude Code"}
                        ]
                    },
                    {
                        "step": 5,
                        "type": "stats",
                        "items": [
                            {"icon": "\u26a1", "value": "AGILE", "label": "\u4ee5\u5468\u4e3a\u5355\u4f4d\u7684\u8fdb\u5316"},
                            {"icon": "\u221e", "value": "FLYWHEEL", "label": "\u6570\u636e\u9a71\u52a8\u7684\u81ea\u589e\u957f"},
                            {"icon": "\u25c8", "value": "NATIVE", "label": "\u539f\u751fAI\u601d\u7ef4\u91cd\u6784"}
                        ]
                    },
                    {
                        "step": 6,
                        "type": "quote",
                        "text": "\u201c\u901a\u91cf\u89e3\u51b3\u6982\u7387\u95ee\u9898\uff0c\u89c4\u6a21\u5316\u81ea\u52a8\u4e00\u5207\u3002\u201d",
                        "gradient": True,
                        "author": {"text": "\u52b3\u535a \u00b7 2026 \u6218\u7565\u5171\u8bc6"}
                    }
                ]
            },
            {
                "badge": {"icon": "\u2726", "text": "HUMAN VALUE"},
                "title": {"text": "\u56de\u5f52\uff1aAI\u65f6\u4ee3\u7684\u4eba\u7c7b\u951a\u70b9"},
                "clickHint": "\u70b9\u51fb\u63a2\u5bfb\u6838\u5fc3\u4ef7\u503c",
                "elements": [
                    {
                        "step": 1,
                        "type": "valueCards",
                        "items": [
                            {"activeStep": 1, "icon": "\u2726", "title": "\u610f\u4e49\u53d1\u73b0\u8005", "desc": "\u5b9a\u4e49\u300c\u4e3a\u4ec0\u4e48\u300d\u00b7 \u7f16\u7ec7\u53d9\u4e8b \u00b7 \u5efa\u7acb\u6df1\u5c42\u94fe\u63a5"},
                            {"activeStep": 2, "icon": "\u25c8", "title": "\u8d23\u4efb\u627f\u62c5\u8005", "desc": "\u4f26\u7406\u88c1\u51b3 \u00b7 \u98ce\u9669\u628a\u63a7 \u00b7 \u6700\u7ec8\u51b3\u7b56\u80cc\u4e66"},
                            {"activeStep": 3, "icon": "\u25c7", "title": "\u4f53\u9a8c\u627f\u8f7d\u8005", "desc": "\u60c5\u611f\u5171\u632f \u00b7 \u5ba1\u7f8e\u76f4\u89c9 \u00b7 \u521b\u9020\u72ec\u7279\u8bb0\u5fc6"}
                        ]
                    },
                    {
                        "step": 4,
                        "type": "competitionBox",
                        "title": "\u5f53\u751f\u4ea7\u529b\u4e0d\u518d\u662f\u74f6\u9888\uff0c\u7ade\u4e89\u7684\u6838\u5fc3\u5c06\u8f6c\u5411\uff1a",
                        "items": ["\u54c1\u724c\u53d9\u4e8b (Brand Story)", "\u60c5\u611f\u8fde\u63a5 (Empathy)", "\u793e\u7fa4\u5171\u8bc6 (Community)"],
                        "conclusion": "\u610f\u4e49 (Meaning) > \u6548\u7387 (Efficiency)"
                    },
                    {
                        "step": 5,
                        "type": "strategyBox",
                        "title": "\u89e3\u87ba\u65cb 2026 \u6838\u5fc3\u6218\u7565",
                        "items": [
                            {"type": "wrong", "text": "\u4e0d\u505a\u300c\u66f4\u597d\u7684\u9a6c\u8f66\u300d(\u65e7\u6a21\u5f0f\u4f18\u5316)"},
                            {"type": "wrong", "text": "\u4e5f\u4e0d\u4ec5\u662f\u300c\u9020\u6c7d\u8f66\u300d(\u5de5\u5177\u63d0\u4f9b\u5546)"},
                            {"type": "right", "text": "\u6211\u4eec\u5b9a\u4e49\u300c\u5982\u4f55\u9a7e\u9a76\u300d(\u8d4b\u80fd\u4e0e\u6559\u80b2)"}
                        ],
                        "final": {"arrow": "\u279e", "text": "\u300c\u6559\u4f60\u7528 AI \u91cd\u65b0\u5b9a\u4e49\u79d1\u7814\u300d"}
                    },
                    {
                        "step": 6,
                        "type": "ending",
                        "icon": "\u2726",
                        "message": "\u4ece\u8303\u5f0f\u8f6c\u79fb\u5230\u4ef7\u503c\u56de\u5f52",
                        "thanks": "THANKS FOR WATCHING"
                    }
                ]
            }
        ]
    
    @property
    def slides(self) -> list:
        return self._slides
    
    def get_slide(self, index: int) -> dict:
        """Get a single slide by index"""
        if 0 <= index < len(self._slides):
            return self._slides[index]
        return None
    
    def get_max_step(self, slide_index: int) -> int:
        """Get the maximum step number for a slide"""
        slide = self.get_slide(slide_index)
        if not slide:
            return 0
        
        max_step = 0
        for element in slide.get('elements', []):
            step = element.get('step', 0)
            if step > max_step:
                max_step = step
            
            # Check for activeStep in items (timeline, valueCards)
            for item in element.get('items', []):
                active_step = item.get('activeStep', 0)
                if active_step > max_step:
                    max_step = active_step
            
            # Check revealStep
            reveal_step = element.get('revealStep', 0)
            if reveal_step > max_step:
                max_step = reveal_step
        
        return max_step
