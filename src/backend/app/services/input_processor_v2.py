"""
Redesigned User Input Processing Service
Processes user question + theme + context into enriched context for model selection
"""
import re
from typing import Dict, List, Tuple, Optional
from app.models.schemas import UserInput, ProcessedContext, ThemeType, AudienceType, ResponseStyle
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserInputProcessor:
    """Processes user input: question + theme + context into enriched context"""
    
    def __init__(self):
        # Theme to subject mapping
        self.theme_subject_mapping = {
            ThemeType.ACADEMIC_HELP: {
                "primary_subjects": ["mathematics", "science", "literature", "history"],
                "complexity_hint": "academic",
                "typical_models": ["claude-3-sonnet", "gpt-4"]
            },
            ThemeType.CREATIVE_WRITING: {
                "primary_subjects": ["creative writing", "storytelling", "poetry"],
                "complexity_hint": "creative",
                "typical_models": ["gpt-4", "claude-3-opus"]
            },
            ThemeType.CODING_PROGRAMMING: {
                "primary_subjects": ["programming", "software development", "algorithms"],
                "complexity_hint": "technical",
                "typical_models": ["claude-3-sonnet", "gpt-4"]
            },
            ThemeType.BUSINESS_PROFESSIONAL: {
                "primary_subjects": ["business", "management", "strategy", "finance"],
                "complexity_hint": "professional",
                "typical_models": ["gpt-4", "claude-3-opus"]
            },
            ThemeType.PERSONAL_LEARNING: {
                "primary_subjects": ["general knowledge", "skills", "hobbies"],
                "complexity_hint": "beginner_to_intermediate",
                "typical_models": ["claude-3-sonnet", "claude-3-haiku"]
            },
            ThemeType.RESEARCH_ANALYSIS: {
                "primary_subjects": ["research", "data analysis", "academic research"],
                "complexity_hint": "advanced",
                "typical_models": ["claude-3-opus", "gpt-4"]
            },
            ThemeType.PROBLEM_SOLVING: {
                "primary_subjects": ["logic", "mathematics", "troubleshooting"],
                "complexity_hint": "analytical",
                "typical_models": ["claude-3-sonnet", "gpt-4"]
            },
            ThemeType.TUTORING_EDUCATION: {
                "primary_subjects": ["education", "teaching", "explanation"],
                "complexity_hint": "educational",
                "typical_models": ["claude-3-sonnet", "gpt-4"]
            },
            ThemeType.GENERAL_QUESTIONS: {
                "primary_subjects": ["general knowledge", "everyday questions"],
                "complexity_hint": "general",
                "typical_models": ["claude-3-haiku", "gpt-3.5-turbo"]
            }
        }
        
        # Subject detection keywords (refined)
        self.subject_keywords = {
            "mathematics": [
                "math", "calculate", "equation", "algebra", "geometry", "calculus",
                "statistics", "probability", "number", "formula", "solve"
            ],
            "science": [
                "chemistry", "physics", "biology", "experiment", "hypothesis",
                "molecule", "atom", "evolution", "gravity", "energy", "scientific"
            ],
            "programming": [
                "code", "programming", "function", "variable", "algorithm", "python",
                "javascript", "java", "debug", "software", "api", "development"
            ],
            "creative writing": [
                "story", "poem", "creative", "write", "fiction", "character",
                "plot", "narrative", "artistic", "novel", "screenplay"
            ],
            "literature": [
                "literature", "book", "author", "novel", "poem", "literary",
                "analysis", "shakespeare", "poetry", "prose"
            ],
            "business": [
                "business", "management", "strategy", "marketing", "finance",
                "company", "profit", "revenue", "customers", "market"
            ],
            "history": [
                "history", "historical", "century", "war", "civilization",
                "ancient", "medieval", "revolution", "empire", "timeline"
            ],
            "general knowledge": [
                "explain", "what is", "how does", "why", "general", "basic",
                "simple", "everyday", "common", "typical"
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            "beginner": [
                "simple", "basic", "easy", "beginner", "start", "introduction",
                "elementary", "first time", "new to", "learning"
            ],
            "intermediate": [
                "intermediate", "some experience", "familiar with", "know basics",
                "next level", "improve", "better understanding"
            ],
            "advanced": [
                "advanced", "expert", "professional", "complex", "detailed",
                "comprehensive", "in-depth", "sophisticated", "specialized"
            ],
            "academic": [
                "academic", "research", "university", "college", "scholarly",
                "thesis", "paper", "study", "analysis", "theoretical"
            ],
            "professional": [
                "professional", "work", "industry", "business", "corporate",
                "production", "enterprise", "commercial", "real-world"
            ]
        }

    async def process_input(self, user_input: UserInput) -> ProcessedContext:
        """Process user input into enriched context for model selection"""
        
        logger.info(
            "Processing user input",
            theme=user_input.theme,
            question_length=len(user_input.question),
            has_context=bool(user_input.context)
        )
        
        # Combine question and context for analysis
        full_text = user_input.question
        if user_input.context:
            full_text += " " + user_input.context
        
        # 1. Infer subject based on theme + content analysis
        inferred_subject, subject_confidence = self._infer_subject(user_input.theme, full_text)
        
        # 2. Infer complexity level
        inferred_complexity, complexity_confidence = self._infer_complexity(user_input.theme, full_text)
        
        # 3. Calculate numerical complexity score
        complexity_score = self._calculate_complexity_score(
            theme=user_input.theme,
            complexity_level=inferred_complexity,
            text_length=len(full_text),
            subject=inferred_subject
        )
        
        # 4. Estimate token usage
        estimated_tokens = self._estimate_tokens(full_text)
        
        # 5. Calculate overall processing confidence
        processing_confidence = (subject_confidence + complexity_confidence) / 2
        
        # 6. Determine if clarification is needed
        requires_clarification = processing_confidence < 0.6 or complexity_score < 0.1
        
        # Apply defaults for optional fields if not provided
        theme = user_input.theme or ThemeType.GENERAL_QUESTIONS
        audience = user_input.audience or AudienceType.ADULTS
        response_style = user_input.response_style or ResponseStyle.STRUCTURED_DETAILED

        context = ProcessedContext(
            question=user_input.question,
            theme=theme,
            audience=audience,
            response_style=response_style,
            context=user_input.context,
            conversation_id=user_input.conversation_id,
            inferred_subject=inferred_subject,
            inferred_complexity=inferred_complexity,
            complexity_score=complexity_score,
            estimated_tokens=estimated_tokens,
            processing_confidence=processing_confidence,
            requires_clarification=requires_clarification
        )
        
        logger.info(
            "Input processed",
            theme=user_input.theme,
            inferred_subject=inferred_subject,
            inferred_complexity=inferred_complexity,
            complexity_score=complexity_score,
            processing_confidence=processing_confidence
        )
        
        return context

    def _infer_subject(self, theme: Optional[ThemeType], full_text: str) -> Tuple[str, float]:
        """Infer specific subject from theme and text content"""

        # Start with theme-based subject hints (if theme is provided)
        primary_subjects = []
        if theme and theme in self.theme_subject_mapping:
            theme_info = self.theme_subject_mapping[theme]
            primary_subjects = theme_info["primary_subjects"]
        
        # Analyze text for specific subject keywords
        text_lower = full_text.lower()
        subject_scores = {}
        
        for subject, keywords in self.subject_keywords.items():
            # Score based on keyword matches
            keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
            
            # Boost score if subject is in theme's primary subjects
            theme_boost = 2 if subject in primary_subjects else 1
            
            if keyword_matches > 0:
                subject_scores[subject] = keyword_matches * theme_boost
        
        # If we found keyword matches, use highest scoring subject
        if subject_scores:
            best_subject = max(subject_scores, key=subject_scores.get)
            max_score = subject_scores[best_subject]
            
            # Calculate confidence based on score strength
            confidence = min(max_score / 5.0, 1.0)  # Normalize to 0-1
            
            return best_subject, confidence

        # Fallback to theme's primary subject (or general knowledge if no theme)
        if primary_subjects:
            primary_subject = primary_subjects[0]
            return primary_subject, 0.5  # Medium confidence for theme-only inference
        else:
            return "general knowledge", 0.3  # Low confidence when no theme provided

    def _infer_complexity(self, theme: Optional[ThemeType], full_text: str) -> Tuple[str, float]:
        """Infer complexity level from theme and text indicators"""

        # Get theme complexity hint (if theme is provided)
        theme_complexity_hint = "general"
        if theme and theme in self.theme_subject_mapping:
            theme_info = self.theme_subject_mapping[theme]
            theme_complexity_hint = theme_info["complexity_hint"]
        
        # Analyze text for complexity indicators
        text_lower = full_text.lower()
        complexity_scores = {}
        
        for complexity_level, indicators in self.complexity_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in text_lower)
            if matches > 0:
                complexity_scores[complexity_level] = matches
        
        # If explicit complexity indicators found, use them
        if complexity_scores:
            best_complexity = max(complexity_scores, key=complexity_scores.get)
            confidence = min(complexity_scores[best_complexity] / 3.0, 1.0)
            return best_complexity, confidence
        
        # Fallback: infer from question characteristics
        inferred_complexity = self._infer_complexity_from_characteristics(full_text, theme_complexity_hint)
        
        return inferred_complexity, 0.4  # Lower confidence for inference

    def _infer_complexity_from_characteristics(self, text: str, theme_hint: str) -> str:
        """Infer complexity from text characteristics and theme"""
        
        word_count = len(text.split())
        
        # Check for sophisticated vocabulary
        sophisticated_words = [
            "sophisticated", "comprehensive", "analyze", "synthesize", "evaluate",
            "methodology", "paradigm", "framework", "implementation", "optimization"
        ]
        
        has_sophisticated_vocab = any(word in text.lower() for word in sophisticated_words)
        
        # Decision logic
        if theme_hint == "professional" or has_sophisticated_vocab:
            return "professional"
        elif theme_hint == "advanced" or word_count > 50:
            return "advanced"  
        elif theme_hint == "academic":
            return "academic"
        elif word_count > 20:
            return "intermediate"
        else:
            return "beginner"

    def _calculate_complexity_score(self, theme: Optional[ThemeType], complexity_level: str, text_length: int, subject: str) -> float:
        """Calculate numerical complexity score 0-1"""
        
        # Base score from complexity level
        complexity_base_scores = {
            "beginner": 0.2,
            "intermediate": 0.4,
            "advanced": 0.7,
            "academic": 0.8,
            "professional": 0.9
        }
        
        base_score = complexity_base_scores.get(complexity_level, 0.5)
        
        # Subject multiplier (some subjects inherently more complex)
        subject_multipliers = {
            "mathematics": 1.1,
            "science": 1.1,
            "programming": 1.2,
            "research": 1.2,
            "creative writing": 0.9,
            "general knowledge": 0.8,
            "business": 1.0
        }
        
        subject_multiplier = subject_multipliers.get(subject, 1.0)
        
        # Length factor (longer questions tend to be more complex)
        length_factor = min(text_length / 200, 1.2)  # Cap at 1.2x
        
        # Combine factors
        final_score = base_score * subject_multiplier * length_factor
        
        return min(final_score, 1.0)  # Cap at 1.0

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for the complete prompt"""
        
        # Base text tokens (rough: 1 token ≈ 4 characters)
        text_tokens = len(text) // 4
        
        # System prompt overhead (varies by complexity)
        system_prompt_tokens = 300  # More sophisticated prompts now
        
        # Safety margin for model-specific formatting
        safety_margin = 50
        
        return text_tokens + system_prompt_tokens + safety_margin

    def get_theme_info(self, theme: ThemeType) -> Dict:
        """Get information about a theme for UI/debugging"""
        return self.theme_subject_mapping.get(theme, {})

    def get_available_themes(self) -> List[Dict[str, str]]:
        """Get all available themes for dropdown UI"""
        return [
            {"value": theme.value, "label": theme.value.replace("_", " ").title()}
            for theme in ThemeType
        ]