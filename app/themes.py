"""
Theme definitions for UrVote boards.
Each theme provides consistent visual styling including colors, gradients, fonts, and UI elements.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ThemeColors:
    """Color palette for a theme"""
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    border: str

@dataclass
class ThemeGradients:
    """Gradient definitions for a theme"""
    primary: str
    secondary: str
    background: str
    button: str
    card: str

@dataclass
class ThemeTypography:
    """Typography settings for a theme"""
    font_family: str
    heading_weight: str
    body_weight: str
    button_weight: str

@dataclass
class ThemeUI:
    """UI element styling for a theme"""
    border_radius: str
    shadow: str
    button_style: str
    card_style: str
    input_style: str

@dataclass
class Theme:
    """Complete theme definition"""
    name: str
    description: str
    keywords: List[str]
    colors: ThemeColors
    gradients: ThemeGradients
    typography: ThemeTypography
    ui: ThemeUI
    css_classes: Dict[str, str]

# Theme Definitions
THEMES = {
    "chilled_vibe": Theme(
        name="Chilled Vibe",
        description="Cool, relaxed atmosphere with soft blues and smooth gradients",
        keywords=["chill", "chilled", "relaxed", "smooth", "cool", "calm", "ambient", "lo-fi", "peaceful"],
        colors=ThemeColors(
            primary="#3B82F6",      # Blue
            secondary="#10B981",    # Green
            accent="#06B6D4",       # Cyan
            background="#F8FAFC",   # Light gray-blue
            surface="#FFFFFF",      # White
            text_primary="#1E293B", # Dark slate
            text_secondary="#64748B", # Medium slate
            border="#E2E8F0"        # Light gray
        ),
        gradients=ThemeGradients(
            primary="from-blue-500 to-cyan-500",
            secondary="from-green-400 to-blue-400",
            background="from-blue-50 to-cyan-50",
            button="from-blue-500 to-blue-600",
            card="from-white to-blue-50"
        ),
        typography=ThemeTypography(
            font_family="Inter",
            heading_weight="font-semibold",
            body_weight="font-normal",
            button_weight="font-medium"
        ),
        ui=ThemeUI(
            border_radius="rounded-xl",
            shadow="shadow-lg",
            button_style="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600",
            card_style="bg-white/80 backdrop-blur-sm border border-blue-100",
            input_style="border-blue-200 focus:border-blue-400 focus:ring-blue-400"
        ),
        css_classes={
            "container": "bg-gradient-to-br from-blue-50 to-cyan-50",
            "card": "bg-white/80 backdrop-blur-sm border border-blue-100 rounded-xl shadow-lg",
            "button_primary": "bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-medium px-6 py-3 rounded-xl transition-all transform hover:scale-105",
            "button_secondary": "bg-white/90 text-blue-600 border border-blue-200 hover:bg-blue-50 font-medium px-6 py-3 rounded-xl transition-all",
            "text_heading": "text-slate-800 font-semibold",
            "text_body": "text-slate-600",
            "accent": "text-blue-600"
        }
    ),
    
    "high_energy": Theme(
        name="High Energy",
        description="Bold, dynamic styling with bright colors and sharp edges",
        keywords=["energy", "energetic", "high", "bold", "dynamic", "powerful", "intense", "vibrant", "loud", "party"],
        colors=ThemeColors(
            primary="#F59E0B",      # Amber
            secondary="#EF4444",    # Red
            accent="#8B5CF6",       # Purple
            background="#FEF3C7",   # Light amber
            surface="#FFFFFF",      # White
            text_primary="#1F2937", # Dark gray
            text_secondary="#6B7280", # Medium gray
            border="#FCD34D"        # Light amber
        ),
        gradients=ThemeGradients(
            primary="from-amber-500 to-orange-500",
            secondary="from-red-500 to-pink-500",
            background="from-amber-50 to-orange-50",
            button="from-amber-500 to-orange-600",
            card="from-white to-amber-50"
        ),
        typography=ThemeTypography(
            font_family="Inter",
            heading_weight="font-bold",
            body_weight="font-medium",
            button_weight="font-bold"
        ),
        ui=ThemeUI(
            border_radius="rounded-lg",
            shadow="shadow-xl",
            button_style="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600",
            card_style="bg-white/90 border border-amber-200",
            input_style="border-amber-200 focus:border-amber-500 focus:ring-amber-500"
        ),
        css_classes={
            "container": "bg-gradient-to-br from-amber-50 to-orange-50",
            "card": "bg-white/90 border border-amber-200 rounded-lg shadow-xl",
            "button_primary": "bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-bold px-6 py-3 rounded-lg transition-all transform hover:scale-105 shadow-lg",
            "button_secondary": "bg-white/90 text-amber-600 border border-amber-300 hover:bg-amber-50 font-bold px-6 py-3 rounded-lg transition-all",
            "text_heading": "text-gray-800 font-bold",
            "text_body": "text-gray-700 font-medium",
            "accent": "text-amber-600"
        }
    ),
    
    "professional": Theme(
        name="Professional",
        description="Clean, corporate styling with neutral colors and minimal design",
        keywords=["professional", "corporate", "business", "clean", "minimal", "formal", "elegant", "sophisticated", "modern", "corporate"],
        colors=ThemeColors(
            primary="#1F2937",      # Dark gray
            secondary="#374151",    # Medium gray
            accent="#3B82F6",       # Blue
            background="#F9FAFB",   # Light gray
            surface="#FFFFFF",      # White
            text_primary="#111827", # Very dark gray
            text_secondary="#4B5563", # Medium gray
            border="#D1D5DB"        # Light gray
        ),
        gradients=ThemeGradients(
            primary="from-gray-700 to-gray-800",
            secondary="from-blue-600 to-blue-700",
            background="from-gray-50 to-white",
            button="from-gray-700 to-gray-800",
            card="from-white to-gray-50"
        ),
        typography=ThemeTypography(
            font_family="Inter",
            heading_weight="font-semibold",
            body_weight="font-normal",
            button_weight="font-medium"
        ),
        ui=ThemeUI(
            border_radius="rounded-md",
            shadow="shadow-md",
            button_style="bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-800 hover:to-gray-900",
            card_style="bg-white border border-gray-200",
            input_style="border-gray-300 focus:border-blue-500 focus:ring-blue-500"
        ),
        css_classes={
            "container": "bg-gradient-to-br from-gray-50 to-white",
            "card": "bg-white border border-gray-200 rounded-md shadow-md",
            "button_primary": "bg-gradient-to-r from-gray-700 to-gray-800 hover:from-gray-800 hover:to-gray-900 text-white font-medium px-6 py-3 rounded-md transition-all",
            "button_secondary": "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50 font-medium px-6 py-3 rounded-md transition-all",
            "text_heading": "text-gray-900 font-semibold",
            "text_body": "text-gray-700",
            "accent": "text-blue-600"
        }
    ),
    
    "creative": Theme(
        name="Creative",
        description="Artistic, vibrant styling with bold colors and organic shapes",
        keywords=["creative", "artistic", "vibrant", "colorful", "fun", "playful", "imaginative", "expressive", "art", "design"],
        colors=ThemeColors(
            primary="#8B5CF6",      # Purple
            secondary="#EC4899",    # Pink
            accent="#10B981",       # Green
            background="#F3E8FF",   # Light purple
            surface="#FFFFFF",      # White
            text_primary="#1F2937", # Dark gray
            text_secondary="#6B7280", # Medium gray
            border="#DDD6FE"        # Light purple
        ),
        gradients=ThemeGradients(
            primary="from-purple-500 to-pink-500",
            secondary="from-green-400 to-blue-400",
            background="from-purple-50 to-pink-50",
            button="from-purple-500 to-pink-500",
            card="from-white to-purple-50"
        ),
        typography=ThemeTypography(
            font_family="Inter",
            heading_weight="font-bold",
            body_weight="font-normal",
            button_weight="font-semibold"
        ),
        ui=ThemeUI(
            border_radius="rounded-2xl",
            shadow="shadow-lg",
            button_style="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600",
            card_style="bg-white/90 border border-purple-200",
            input_style="border-purple-200 focus:border-purple-500 focus:ring-purple-500"
        ),
        css_classes={
            "container": "bg-gradient-to-br from-purple-50 to-pink-50",
            "card": "bg-white/90 border border-purple-200 rounded-2xl shadow-lg",
            "button_primary": "bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-2xl transition-all transform hover:scale-105",
            "button_secondary": "bg-white/90 text-purple-600 border border-purple-300 hover:bg-purple-50 font-semibold px-6 py-3 rounded-2xl transition-all",
            "text_heading": "text-gray-800 font-bold",
            "text_body": "text-gray-700",
            "accent": "text-purple-600"
        }
    ),
    
    "elegant": Theme(
        name="Elegant",
        description="Sophisticated, luxury styling with deep colors and refined elements",
        keywords=["elegant", "luxury", "sophisticated", "refined", "premium", "classy", "upscale", "high-end", "deluxe", "chic"],
        colors=ThemeColors(
            primary="#7C3AED",      # Deep purple
            secondary="#F59E0B",    # Gold
            accent="#10B981",       # Emerald
            background="#F5F3FF",   # Light purple
            surface="#FFFFFF",      # White
            text_primary="#1F2937", # Dark gray
            text_secondary="#6B7280", # Medium gray
            border="#DDD6FE"        # Light purple
        ),
        gradients=ThemeGradients(
            primary="from-purple-600 to-purple-700",
            secondary="from-amber-500 to-yellow-500",
            background="from-purple-50 to-indigo-50",
            button="from-purple-600 to-purple-700",
            card="from-white to-purple-50"
        ),
        typography=ThemeTypography(
            font_family="Inter",
            heading_weight="font-semibold",
            body_weight="font-normal",
            button_weight="font-medium"
        ),
        ui=ThemeUI(
            border_radius="rounded-xl",
            shadow="shadow-xl",
            button_style="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800",
            card_style="bg-white/95 border border-purple-200",
            input_style="border-purple-200 focus:border-purple-600 focus:ring-purple-600"
        ),
        css_classes={
            "container": "bg-gradient-to-br from-purple-50 to-indigo-50",
            "card": "bg-white/95 border border-purple-200 rounded-xl shadow-xl",
            "button_primary": "bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-medium px-6 py-3 rounded-xl transition-all",
            "button_secondary": "bg-white/95 text-purple-600 border border-purple-300 hover:bg-purple-50 font-medium px-6 py-3 rounded-xl transition-all",
            "text_heading": "text-gray-800 font-semibold",
            "text_body": "text-gray-700",
            "accent": "text-purple-600"
        }
    ),
    
    "nature": Theme(
        name="Nature",
        description="Organic, earthy styling with natural colors and flowing shapes",
        keywords=["nature", "natural", "organic", "earth", "green", "forest", "garden", "outdoor", "environmental", "eco-friendly"],
        colors=ThemeColors(
            primary="#059669",      # Emerald
            secondary="#D97706",    # Amber
            accent="#7C3AED",       # Purple
            background="#F0FDF4",   # Light green
            surface="#FFFFFF",      # White
            text_primary="#1F2937", # Dark gray
            text_secondary="#6B7280", # Medium gray
            border="#BBF7D0"        # Light green
        ),
        gradients=ThemeGradients(
            primary="from-emerald-500 to-green-500",
            secondary="from-amber-500 to-orange-500",
            background="from-green-50 to-emerald-50",
            button="from-emerald-500 to-green-500",
            card="from-white to-green-50"
        ),
        typography=ThemeTypography(
            font_family="Inter",
            heading_weight="font-semibold",
            body_weight="font-normal",
            button_weight="font-medium"
        ),
        ui=ThemeUI(
            border_radius="rounded-2xl",
            shadow="shadow-lg",
            button_style="bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600",
            card_style="bg-white/90 border border-green-200",
            input_style="border-green-200 focus:border-emerald-500 focus:ring-emerald-500"
        ),
        css_classes={
            "container": "bg-gradient-to-br from-green-50 to-emerald-50",
            "card": "bg-white/90 border border-green-200 rounded-2xl shadow-lg",
            "button_primary": "bg-gradient-to-r from-emerald-500 to-green-500 hover:from-emerald-600 hover:to-green-600 text-white font-medium px-6 py-3 rounded-2xl transition-all transform hover:scale-105",
            "button_secondary": "bg-white/90 text-emerald-600 border border-green-300 hover:bg-green-50 font-medium px-6 py-3 rounded-2xl transition-all",
            "text_heading": "text-gray-800 font-semibold",
            "text_body": "text-gray-700",
            "accent": "text-emerald-600"
        }
    )
}

def get_theme_by_name(theme_name: str) -> Theme:
    """Get a theme by its name"""
    return THEMES.get(theme_name.lower().replace(" ", "_"))

def get_theme_by_keywords(description: str) -> Theme:
    """Get the best matching theme based on description keywords"""
    description_lower = description.lower()
    best_match = None
    best_score = 0
    
    for theme in THEMES.values():
        score = 0
        for keyword in theme.keywords:
            if keyword in description_lower:
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = theme
    
    return best_match or THEMES["chilled_vibe"]  # Default fallback

def get_all_themes() -> List[Dict[str, Any]]:
    """Get all available themes for selection"""
    return [
        {
            "id": theme_id,
            "name": theme.name,
            "description": theme.description,
            "preview_colors": [theme.colors.primary, theme.colors.secondary, theme.colors.accent],
            "gradient": theme.gradients.primary
        }
        for theme_id, theme in THEMES.items()
    ]

def apply_theme_to_campaign(campaign_data: Dict[str, Any], theme: Theme) -> Dict[str, Any]:
    """Apply theme styling to campaign data"""
    campaign_data.update({
        "theme": theme.name,
        "theme_id": theme.name.lower().replace(" ", "_"),
        "colors": theme.colors,
        "gradients": theme.gradients,
        "typography": theme.typography,
        "ui": theme.ui,
        "css_classes": theme.css_classes
    })
    return campaign_data
