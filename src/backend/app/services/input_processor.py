"""
User Input Processing Service
Handles structured input and context extraction
"""
import re
from typing import Dict, List
from app.models.schemas import StructuredUserInput, ProcessedContext, SubjectType, GradeLevel
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserInputProcessor:
    """Processes and enriches user input with context analysis"""
    
    def __init__(self):
        # Keywords for subject classification
        self.subject_keywords = {
            SubjectType.MATH: [
                "calculate", "equation", "solve", "algebra", "geometry", "calculus",
                "mathematics", "number", "formula", "statistics", "probability"
            ],
            SubjectType.SCIENCE: [
                "chemistry", "physics", "biology", "experiment", "hypothesis",
                "molecule", "atom", "evolution", "gravity", "energy"
            ],
            SubjectType.CODE: [
                "code", "programming", "function", "variable", "algorithm",
                "python", "javascript", "debug", "software", "api"
            ],
            SubjectType.CREATIVE: [
                "story", "poem", "creative", "write", "imagine", "fiction",
                "character", "plot", "narrative", "artistic"
            ],
            SubjectType.ENGLISH: [
                "grammar", "essay", "literature", "writing", "reading",
                "vocabulary", "sentence", "paragraph", "analysis"
            ],
            SubjectType.HISTORY: [
                "history", "historical", "century", "war", "civilization",
                "ancient", "medieval", "revolution", "empire", "timeline"
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            GradeLevel.ELEMENTARY: [
                "simple", "basic", "easy", "elementary", "grade 1", "grade 2", 
                "grade 3", "grade 4", "grade 5", "kindergarten"
            ],
            GradeLevel.MIDDLE_SCHOOL: [
                "middle school", "grade 6", "grade 7", "grade 8", "intermediate"
            ],
            GradeLevel.HIGH_SCHOOL: [
                "high school", "grade 9", "grade 10", "grade 11", "grade 12",
                "secondary", "advanced"
            ],
            GradeLevel.COLLEGE: [
                "college", "university", "undergraduate", "academic", "advanced",
                "complex", "detailed", "comprehensive"
            ],
            GradeLevel.PROFESSIONAL: [
                "professional", "expert", "advanced", "industry", "research",
                "PhD", "doctorate", "specialized"
            ]
        }

    async def process_input(self, user_input: StructuredUserInput) -> ProcessedContext:
        """Process structured user input and extract context"""
        
        logger.info("Processing user input", question_length=len(user_input.question))
        
        # If subject not provided, try to classify
        subject = user_input.subject
        if subject == SubjectType.GENERAL:
            subject = self._classify_subject(user_input.question)
        
        # If grade level not provided, try to infer
        grade_level = user_input.grade_level
        if not grade_level:
            grade_level = self._infer_grade_level(
                user_input.question, 
                user_input.additional_context
            )
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(
            user_input.question, 
            grade_level, 
            subject
        )
        
        # Estimate token count
        estimated_tokens = self._estimate_token_count(
            user_input.question,
            user_input.additional_context
        )
        
        context = ProcessedContext(
            question=user_input.question,
            subject=subject,
            grade_level=grade_level,
            additional_context=user_input.additional_context,
            conversation_id=user_input.conversation_id,
            estimated_tokens=estimated_tokens,
            complexity_score=complexity_score
        )
        
        logger.info(
            "Input processed",
            subject=subject,
            grade_level=grade_level,
            complexity_score=complexity_score,
            estimated_tokens=estimated_tokens
        )
        
        return context

    def _classify_subject(self, question: str) -> SubjectType:
        """Classify question subject based on keywords"""
        question_lower = question.lower()
        subject_scores = {}
        
        for subject, keywords in self.subject_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                subject_scores[subject] = score
        
        if subject_scores:
            # Return subject with highest score
            return max(subject_scores, key=subject_scores.get)
        
        return SubjectType.GENERAL

    def _infer_grade_level(self, question: str, additional_context: str = None) -> GradeLevel:
        """Infer grade level from question content and context"""
        text = question.lower()
        if additional_context:
            text += " " + additional_context.lower()
        
        level_scores = {}
        for level, indicators in self.complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            if score > 0:
                level_scores[level] = score
        
        if level_scores:
            return max(level_scores, key=level_scores.get)
        
        # Default inference based on question complexity
        word_count = len(question.split())
        if word_count < 10:
            return GradeLevel.ELEMENTARY
        elif word_count < 20:
            return GradeLevel.MIDDLE_SCHOOL  
        elif word_count < 40:
            return GradeLevel.HIGH_SCHOOL
        else:
            return GradeLevel.COLLEGE

    def _calculate_complexity_score(self, question: str, grade_level: GradeLevel, subject: SubjectType) -> float:
        """Calculate complexity score 0-1"""
        base_score = {
            GradeLevel.ELEMENTARY: 0.2,
            GradeLevel.MIDDLE_SCHOOL: 0.4,
            GradeLevel.HIGH_SCHOOL: 0.6,
            GradeLevel.COLLEGE: 0.8,
            GradeLevel.PROFESSIONAL: 1.0
        }[grade_level]
        
        # Adjust for subject complexity
        subject_multiplier = {
            SubjectType.MATH: 1.1,
            SubjectType.SCIENCE: 1.1,
            SubjectType.CODE: 1.2,
            SubjectType.CREATIVE: 0.9,
            SubjectType.ENGLISH: 0.9,
            SubjectType.HISTORY: 0.8,
            SubjectType.GENERAL: 1.0
        }[subject]
        
        # Adjust for question length and complexity indicators
        word_count = len(question.split())
        length_factor = min(word_count / 50, 1.0)  # Cap at 1.0
        
        final_score = base_score * subject_multiplier * (0.7 + 0.3 * length_factor)
        return min(final_score, 1.0)  # Cap at 1.0

    def _estimate_token_count(self, question: str, additional_context: str = None) -> int:
        """Rough token count estimation (1 token ≈ 4 chars)"""
        total_chars = len(question)
        if additional_context:
            total_chars += len(additional_context)
        
        # Add system prompt overhead (estimated)
        system_prompt_overhead = 200
        
        return (total_chars // 4) + system_prompt_overhead