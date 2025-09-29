"""
Model-Specific Prompt Generation Service
Creates optimized prompts tailored for each model and context
"""
from typing import Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from app.models.schemas import ProcessedContext, ThemeType, AudienceType
from app.core.logging import get_logger

logger = get_logger(__name__)


class ModelSpecificPromptGenerator:
    """Generates model-specific prompts optimized for each LLM"""
    
    def __init__(self):
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Model-specific prompt configurations
        self.model_prompts = {
            "claude-3-opus": {
                "base_personality": "You are Claude, an AI assistant created by Anthropic to be helpful, harmless, and honest.",
                "thinking_style": "You think step-by-step and provide thorough, well-reasoned explanations.",
                "strengths": "complex reasoning, detailed analysis, nuanced understanding"
            },
            "claude-3-sonnet": {
                "base_personality": "You are Claude, an AI assistant focused on providing clear, accurate, and helpful responses.",
                "thinking_style": "You balance thoroughness with conciseness, explaining your reasoning clearly.",
                "strengths": "balanced responses, code generation, practical problem-solving"
            },
            "claude-3-haiku": {
                "base_personality": "You are Claude, an AI assistant that provides clear, concise, and helpful responses.",
                "thinking_style": "You focus on direct, practical answers while remaining thorough when needed.",
                "strengths": "speed, clarity, straightforward explanations"
            },
            "gpt-4": {
                "base_personality": "You are GPT-4, a large language model created by OpenAI.",
                "thinking_style": "You provide comprehensive, well-structured responses with careful reasoning.",
                "strengths": "creative thinking, comprehensive analysis, versatile problem-solving"
            },
            "gpt-3.5-turbo": {
                "base_personality": "You are ChatGPT, an AI assistant created by OpenAI.",
                "thinking_style": "You provide helpful, clear responses focused on practical utility.",
                "strengths": "efficiency, general knowledge, accessible explanations"
            }
        }
        
        
        
        # Audience-specific adaptations
        self.audience_adaptations = {
            "small_kids": {
                "language_level": "Use very simple words and short sentences. Avoid complex vocabulary.",
                "tone": "Be friendly, patient, and encouraging. Use a warm, caring tone.",
                "examples": "Use examples from cartoons, toys, animals, and everyday kid activities.",
                "explanation_style": "Break down concepts into very small, simple steps with lots of encouragement."
            },
            "teenagers": {
                "language_level": "Use age-appropriate language that's not too formal or childish.",
                "tone": "Be respectful and engaging. Avoid being preachy or condescending.",
                "examples": "Use examples from school, hobbies, pop culture, and technology they relate to.",
                "explanation_style": "Be clear and direct. Acknowledge their growing independence and intelligence."
            },
            "adults": {
                "language_level": "Use clear, professional language appropriate for educated adults.",
                "tone": "Be respectful, informative, and helpful. Maintain a professional yet approachable tone.",
                "examples": "Use practical, real-world examples relevant to adult life and responsibilities.",
                "explanation_style": "Provide thorough explanations while respecting their time and intelligence."
            },
            "university_level": {
                "language_level": "Use academic language and terminology appropriate for higher education.",
                "tone": "Be scholarly yet accessible. Encourage critical thinking and deeper analysis.",
                "examples": "Use academic examples, research findings, and theoretical frameworks.",
                "explanation_style": "Provide in-depth analysis with academic rigor and intellectual challenge."
            },
            "professionals": {
                "language_level": "Use professional and technical language as appropriate to the field.",
                "tone": "Be expert-level, efficient, and results-oriented. Focus on practical application.",
                "examples": "Use industry-specific examples, case studies, and professional scenarios.",
                "explanation_style": "Provide expert-level insights with focus on practical implementation and results."
            },
            "seniors": {
                "language_level": "Use clear, respectful language. Avoid overly technical jargon without explanation.",
                "tone": "Be patient, respectful, and considerate. Never patronizing or condescending.",
                "examples": "Use examples from their era and experiences they can relate to.",
                "explanation_style": "Take time to explain clearly, acknowledge their wisdom and experience."
            }
        }

    async def create_model_specific_prompt(
        self, 
        model: str, 
        context: ProcessedContext,
        conversation_history: Optional[str] = None
    ) -> str:
        """Generate intelligent, targeted prompt that combines question analysis, theme expertise, and audience psychology"""
        
        logger.info(
            "Generating intelligent targeted prompt",
            model=model,
            theme=context.theme,
            audience=context.audience,
            question_subject=context.inferred_subject
        )
        
        # Analyze the question to understand what type of response is needed
        question_analysis = self._analyze_question_type(context.question)
        
        # Create dynamic expert persona that perfectly combines theme + audience
        expert_persona = self._create_expert_persona(context.theme, context.audience)
        
        # Build audience psychology profile
        audience_psychology = self._get_audience_psychology(context.audience)
        
        # Generate specific instructions for this question + audience combination
        response_instructions = self._generate_response_instructions(
            context.question, context.theme, context.audience, question_analysis
        )
        
        # Build the intelligent prompt
        system_prompt = self._build_intelligent_prompt(
            model=model,
            context=context,
            expert_persona=expert_persona,
            audience_psychology=audience_psychology,
            response_instructions=response_instructions,
            question_analysis=question_analysis,
            conversation_history=conversation_history
        )
        
        logger.info("Intelligent targeted prompt generated", 
                   model=model, 
                   prompt_length=len(system_prompt),
                   question_type=question_analysis["type"],
                   expert_role=expert_persona["role"])
        
        return system_prompt.strip()

    def _analyze_question_type(self, question: str) -> Dict[str, str]:
        """Analyze the question to understand what type of response is needed"""
        question_lower = question.lower()
        
        # Question type patterns
        if any(word in question_lower for word in ["what is", "what are", "define", "definition", "explain", "meaning"]):
            return {"type": "explanation", "approach": "define and explain clearly"}
        elif any(word in question_lower for word in ["how to", "how do", "how can", "steps", "process", "method"]):
            return {"type": "how_to", "approach": "provide step-by-step guidance"}
        elif any(word in question_lower for word in ["why", "reason", "because", "cause"]):
            return {"type": "reasoning", "approach": "explain underlying causes and logic"}
        elif any(word in question_lower for word in ["compare", "difference", "vs", "versus", "better"]):
            return {"type": "comparison", "approach": "analyze differences and similarities"}
        elif any(word in question_lower for word in ["solve", "fix", "debug", "problem", "issue", "error"]):
            return {"type": "problem_solving", "approach": "diagnose and provide solutions"}
        elif any(word in question_lower for word in ["example", "examples", "show me", "demonstrate"]):
            return {"type": "examples", "approach": "provide concrete examples and demonstrations"}
        elif any(word in question_lower for word in ["best", "recommend", "suggest", "should", "advice"]):
            return {"type": "recommendation", "approach": "provide expert recommendations with rationale"}
        elif any(word in question_lower for word in ["create", "make", "build", "write", "design"]):
            return {"type": "creation", "approach": "guide through creation process with examples"}
        else:
            return {"type": "general", "approach": "provide comprehensive, helpful response"}

    def _create_expert_persona(self, theme: ThemeType, audience: AudienceType) -> Dict[str, str]:
        """Create a specific expert persona that perfectly combines theme expertise with audience understanding"""
        
        # Theme expertise mapping
        theme_experts = {
            ThemeType.ACADEMIC_HELP: {
                "small_kids": "a patient elementary school teacher who makes learning fun and engaging",
                "teenagers": "a cool high school teacher who connects with students and makes subjects relatable", 
                "adults": "an experienced tutor who helps adult learners achieve their educational goals",
                "university_level": "a knowledgeable professor who guides university students through complex academic material",
                "professionals": "an academic consultant who helps working professionals with continued education",
                "seniors": "a respectful educator who appreciates the wisdom of mature learners"
            },
            ThemeType.CODING_PROGRAMMING: {
                "small_kids": "a friendly coding instructor who teaches programming through games and visual examples",
                "teenagers": "a tech-savvy mentor who shows how coding creates cool apps and games",
                "adults": "a senior software developer who helps career changers and professionals learn programming",
                "university_level": "a computer science professor with industry experience teaching best practices",
                "professionals": "a technical lead and architect who mentors other developers",
                "seniors": "a patient programming teacher who explains technology clearly and respectfully"
            },
            ThemeType.CREATIVE_WRITING: {
                "small_kids": "an imaginative storyteller who helps kids express their creativity through words",
                "teenagers": "a published young adult author who understands teen voices and interests",
                "adults": "an experienced writing coach who helps adults develop their storytelling skills",
                "university_level": "a literature professor and published author who teaches craft and technique",
                "professionals": "a professional writer and editor who helps with business and technical writing",
                "seniors": "a wise literary mentor who appreciates life experience in storytelling"
            },
            ThemeType.BUSINESS_PROFESSIONAL: {
                "small_kids": "a business owner who explains entrepreneurship through simple, fun examples",
                "teenagers": "a young entrepreneur who shows how business skills apply to real life",
                "adults": "an experienced business consultant with expertise across industries",
                "university_level": "a business school professor with practical industry experience",
                "professionals": "a C-level executive and business strategist with proven track record",
                "seniors": "a seasoned business advisor who values experience and long-term thinking"
            },
            ThemeType.RESEARCH_ANALYSIS: {
                "small_kids": "a curious researcher who makes investigation and discovery fun",
                "teenagers": "a science communicator who shows how research impacts their world",
                "adults": "a skilled researcher who helps with practical research needs",
                "university_level": "a research professor who teaches methodology and critical thinking",
                "professionals": "a senior analyst who provides actionable insights for decision-making",
                "seniors": "a respected researcher who values thorough, careful analysis"
            },
            ThemeType.TUTORING_EDUCATION: {
                "small_kids": "a caring elementary teacher who makes every child feel capable of learning",
                "teenagers": "an engaging high school tutor who builds confidence and skills",
                "adults": "a professional tutor who helps adults master new skills and knowledge",
                "university_level": "an academic tutor who supports university-level learning success",
                "professionals": "a corporate trainer who develops professional skills and competencies",
                "seniors": "a patient educator who honors adult learning preferences and experience"
            },
            ThemeType.PROBLEM_SOLVING: {
                "small_kids": "a patient problem-solving coach who helps kids think through challenges step-by-step",
                "teenagers": "a tech-savvy problem solver who helps teens tackle challenges with creative solutions",
                "adults": "an experienced consultant who helps adults systematically solve complex problems",
                "university_level": "a methodology expert who teaches structured problem-solving approaches",
                "professionals": "a strategic problem-solving specialist who optimizes business solutions",
                "seniors": "a wise advisor who combines experience with systematic problem-solving methods"
            },
            ThemeType.PERSONAL_LEARNING: {
                "small_kids": "an encouraging learning companion who makes discovery fun and exciting",
                "teenagers": "a motivational learning coach who helps teens explore their interests and potential",
                "adults": "a personal development mentor who supports lifelong learning goals",
                "university_level": "a learning strategist who optimizes study methods and academic growth",
                "professionals": "a professional development coach who accelerates career learning",
                "seniors": "a supportive learning guide who celebrates continued growth and curiosity"
            },
            ThemeType.GENERAL_QUESTIONS: {
                "small_kids": "a knowledgeable and patient teacher who makes any topic accessible and fun",
                "teenagers": "a well-informed mentor who connects knowledge to real-world relevance",
                "adults": "a knowledgeable guide who provides practical, useful information",
                "university_level": "an academic resource who provides thorough, well-researched answers",
                "professionals": "an expert consultant who delivers precise, actionable information",
                "seniors": "a respectful knowledge companion who values both facts and experience"
            }
        }

        # Professional role specializations for deeper expertise
        self.professional_roles = {
            "medical": {
                "expertise": "clinical knowledge, patient care, medical ethics, evidence-based practice",
                "terminology": "use precise medical terminology when appropriate",
                "ethics": "prioritize patient safety, confidentiality, and evidence-based recommendations",
                "approach": "systematic diagnostic thinking, differential diagnosis consideration"
            },
            "legal": {
                "expertise": "legal principles, case law, statutory interpretation, legal procedures",
                "terminology": "use accurate legal terminology and cite relevant precedents",
                "ethics": "emphasize legal compliance, professional responsibility, and ethical practice",
                "approach": "analytical reasoning, precedent analysis, risk assessment"
            },
            "engineering": {
                "expertise": "technical design, safety standards, optimization, problem-solving methodologies",
                "terminology": "use precise technical language and engineering principles",
                "ethics": "prioritize safety, sustainability, and professional engineering standards",
                "approach": "systematic design thinking, constraint analysis, iterative improvement"
            },
            "scientific": {
                "expertise": "research methodology, data analysis, peer review, scientific rigor",
                "terminology": "use accurate scientific terminology and cite relevant research",
                "ethics": "emphasize evidence-based conclusions, uncertainty acknowledgment, peer review",
                "approach": "hypothesis formation, experimental design, statistical analysis"
            },
            "educational": {
                "expertise": "learning theory, curriculum design, assessment, differentiated instruction",
                "terminology": "use pedagogical language and educational best practices",
                "ethics": "prioritize student welfare, inclusive education, professional development",
                "approach": "scaffolded learning, formative assessment, growth mindset"
            },
            "business": {
                "expertise": "strategic planning, market analysis, financial modeling, organizational behavior",
                "terminology": "use business terminology and frameworks appropriately",
                "ethics": "emphasize stakeholder value, sustainable practices, ethical leadership",
                "approach": "data-driven decision making, risk-reward analysis, strategic thinking"
            },
            "creative": {
                "expertise": "artistic principles, creative process, audience engagement, cultural context",
                "terminology": "use creative and artistic terminology appropriately",
                "ethics": "respect intellectual property, cultural sensitivity, authentic expression",
                "approach": "iterative creative process, audience consideration, aesthetic principles"
            }
        }

        # Get specific persona or fallback to general
        persona_desc = theme_experts.get(theme, {}).get(audience.value, 
                      f"an expert in {theme.value} who specializes in helping {audience.value}")
        
        return {
            "role": f"You are {persona_desc}",
            "expertise": f"You have deep expertise in {theme.value.replace('_', ' ')} and extensive experience working with {audience.value.replace('_', ' ')}",
            "approach": f"You understand how {audience.value.replace('_', ' ')} think, learn, and prefer to receive information"
        }

    def _get_audience_psychology(self, audience: AudienceType) -> Dict[str, str]:
        """Deep understanding of how this audience thinks, learns, and processes information"""
        
        psychology_profiles = {
            "small_kids": {
                "attention_span": "Short attention spans, need engaging, bite-sized information",
                "learning_style": "Learn through play, stories, and visual examples",
                "motivation": "Curiosity-driven, respond well to encouragement and praise",
                "communication": "Use simple words, avoid abstract concepts, be patient and supportive",
                "examples": "Use examples from their daily life: toys, cartoons, family, school, animals"
            },
            "teenagers": {
                "attention_span": "Can focus when interested, need relevant and engaging content", 
                "learning_style": "Learn through relevance to their life and social connections",
                "motivation": "Want to understand 'why it matters' and how it applies to them",
                "communication": "Be authentic, avoid talking down, acknowledge their intelligence",
                "examples": "Use examples from technology, social media, pop culture, future goals"
            },
            "adults": {
                "attention_span": "Good focus when content is relevant to their goals",
                "learning_style": "Practical, goal-oriented learning with real-world applications", 
                "motivation": "Want actionable information that helps solve problems or achieve goals",
                "communication": "Be direct, professional, and respectful of their time",
                "examples": "Use practical examples from work, family life, and real-world situations"
            },
            "university_level": {
                "attention_span": "Can handle complex, in-depth information",
                "learning_style": "Academic, analytical thinking with critical evaluation",
                "motivation": "Intellectual curiosity and academic achievement",
                "communication": "Use academic language, encourage critical thinking and analysis", 
                "examples": "Use scholarly examples, research findings, and theoretical frameworks"
            },
            "professionals": {
                "attention_span": "Focused but time-constrained, want efficient information",
                "learning_style": "Results-oriented, want actionable insights and best practices",
                "motivation": "Career advancement, problem-solving, professional effectiveness",
                "communication": "Be concise, expert-level, focus on implementation and results",
                "examples": "Use industry examples, case studies, and professional scenarios"
            },
            "seniors": {
                "attention_span": "Patient and thorough, appreciate detailed explanations",
                "learning_style": "Methodical, prefer step-by-step learning with context",
                "motivation": "Personal enrichment, staying current, helping others",
                "communication": "Be respectful, patient, and avoid condescending language",
                "examples": "Use examples they can relate to from their era and experience"
            }
        }
        
        return psychology_profiles.get(audience.value, psychology_profiles["adults"])

    def _get_formatting_instructions(self, question_analysis: Dict[str, str], audience: AudienceType) -> str:
        """Generate specific formatting instructions based on question type and audience"""

        formatting_instructions = []

        # Question-type specific formatting
        if question_analysis["type"] == "how_to":
            formatting_instructions.append("Use numbered steps or bullet points for clarity")
            formatting_instructions.append("Include clear action items and checkpoints")
        elif question_analysis["type"] == "comparison":
            formatting_instructions.append("Use comparison tables or side-by-side analysis when helpful")
            formatting_instructions.append("Clearly highlight key differences and similarities")
        elif question_analysis["type"] == "explanation":
            formatting_instructions.append("Use clear headings and subheadings to organize information")
            formatting_instructions.append("Include examples and analogies to illustrate concepts")
        elif question_analysis["type"] == "problem_solving":
            formatting_instructions.append("Structure response as: Problem → Analysis → Solutions → Implementation")
            formatting_instructions.append("Use bullet points for multiple solutions or approaches")

        # Audience-specific formatting preferences
        if audience in [AudienceType.SMALL_KIDS, AudienceType.TEENAGERS]:
            formatting_instructions.append("Use visual breaks, emojis, and engaging formatting")
            formatting_instructions.append("Keep paragraphs short and digestible")
        elif audience == AudienceType.UNIVERSITY_LEVEL:
            formatting_instructions.append("Use academic formatting with clear citations and references")
            formatting_instructions.append("Include detailed explanations with supporting evidence")
        elif audience == AudienceType.PROFESSIONALS:
            formatting_instructions.append("Use executive summary format when appropriate")
            formatting_instructions.append("Prioritize actionable insights and key takeaways")

        return " ".join(formatting_instructions)

    def _get_reasoning_pattern(self, question_analysis: Dict[str, str], theme: ThemeType) -> str:
        """Generate reasoning pattern instructions for enhanced cognitive approaches"""

        reasoning_instructions = []

        # Question-type specific reasoning patterns
        if question_analysis["type"] == "problem_solving":
            reasoning_instructions.append("Think through this step-by-step: identify the problem, analyze root causes, generate solutions, evaluate options")
        elif question_analysis["type"] == "reasoning":
            reasoning_instructions.append("Use logical reasoning: present the premise, explain the logic, draw conclusions, consider alternative perspectives")
        elif question_analysis["type"] == "comparison":
            reasoning_instructions.append("Analyze systematically: identify criteria for comparison, evaluate each option against criteria, synthesize findings")
        elif question_analysis["type"] == "explanation":
            reasoning_instructions.append("Build understanding progressively: start with fundamentals, add complexity gradually, connect to existing knowledge")

        # Theme-specific reasoning enhancements
        if theme == ThemeType.ACADEMIC_HELP:
            reasoning_instructions.append("Encourage critical thinking and help the learner discover insights rather than just providing answers")
        elif theme == ThemeType.CODING_PROGRAMMING:
            reasoning_instructions.append("Think algorithmically: break down the problem, consider edge cases, optimize for readability and performance")
        elif theme == ThemeType.RESEARCH_ANALYSIS:
            reasoning_instructions.append("Apply research methodology: consider sources, evaluate evidence quality, acknowledge limitations")

        return " ".join(reasoning_instructions)

    def _get_quality_safeguards(self, theme: ThemeType, audience: AudienceType) -> str:
        """Generate quality safeguards and verification instructions"""

        safeguard_instructions = []

        # Universal safeguards
        safeguard_instructions.append("Verify accuracy: double-check facts and ensure information is current and correct")
        safeguard_instructions.append("Acknowledge uncertainty: be clear about what you're confident about vs. what might need further verification")
        safeguard_instructions.append("Consider bias: reflect on potential biases in your response and present balanced perspectives")

        # Theme-specific safeguards
        if theme in [ThemeType.ACADEMIC_HELP, ThemeType.TUTORING_EDUCATION]:
            safeguard_instructions.append("Focus on learning: guide understanding rather than just providing answers")
        elif theme == ThemeType.CODING_PROGRAMMING:
            safeguard_instructions.append("Emphasize best practices: include security considerations, code maintainability, and testing approaches")
        elif theme == ThemeType.BUSINESS_PROFESSIONAL:
            safeguard_instructions.append("Consider stakeholder impact: address ethical implications and multiple perspectives")

        # Audience-specific safeguards
        if audience == AudienceType.SMALL_KIDS:
            safeguard_instructions.append("Ensure age-appropriateness: avoid complex or potentially concerning content")
        elif audience == AudienceType.PROFESSIONALS:
            safeguard_instructions.append("Emphasize professional responsibility: include relevant compliance and ethical considerations")

        return " ".join(safeguard_instructions)

    def _get_meta_cognitive_instructions(self, question_analysis: Dict[str, str]) -> str:
        """Generate meta-cognitive and self-reflection instructions"""

        meta_instructions = [
            "Self-assess your response: ensure it fully addresses the question and meets the audience's needs",
            "Check completeness: verify you've covered all important aspects of the topic",
            "Evaluate clarity: ensure your explanation is clear and appropriate for the target audience"
        ]

        # Question-specific meta-cognitive enhancements
        if question_analysis["type"] == "how_to":
            meta_instructions.append("Verify practicality: ensure your steps are actionable and realistic")
        elif question_analysis["type"] == "explanation":
            meta_instructions.append("Check understanding: consider if a novice would understand your explanation")
        elif question_analysis["type"] == "problem_solving":
            meta_instructions.append("Validate solutions: ensure your recommendations are feasible and effective")

        return " ".join(meta_instructions)

    def _detect_professional_domain(self, question: str, theme: ThemeType) -> Optional[str]:
        """Detect if the question relates to a specific professional domain"""
        question_lower = question.lower()

        # Medical domain indicators
        medical_keywords = ["medical", "health", "patient", "diagnosis", "treatment", "symptom", "clinical", "healthcare"]
        if any(keyword in question_lower for keyword in medical_keywords):
            return "medical"

        # Legal domain indicators
        legal_keywords = ["legal", "law", "court", "contract", "rights", "liability", "compliance", "regulation"]
        if any(keyword in question_lower for keyword in legal_keywords):
            return "legal"

        # Engineering domain indicators
        engineering_keywords = ["engineer", "design", "technical", "system", "architecture", "optimization", "performance"]
        if any(keyword in question_lower for keyword in engineering_keywords):
            return "engineering"

        # Scientific domain indicators
        scientific_keywords = ["research", "study", "experiment", "hypothesis", "data", "analysis", "scientific"]
        if any(keyword in question_lower for keyword in scientific_keywords) or theme == ThemeType.RESEARCH_ANALYSIS:
            return "scientific"

        # Educational domain indicators
        educational_keywords = ["teach", "learn", "student", "curriculum", "education", "pedagogy"]
        if any(keyword in question_lower for keyword in educational_keywords) or theme in [ThemeType.ACADEMIC_HELP, ThemeType.TUTORING_EDUCATION]:
            return "educational"

        # Business domain indicators
        business_keywords = ["business", "strategy", "market", "profit", "company", "management", "finance"]
        if any(keyword in question_lower for keyword in business_keywords) or theme == ThemeType.BUSINESS_PROFESSIONAL:
            return "business"

        # Creative domain indicators
        creative_keywords = ["creative", "art", "design", "write", "story", "artistic", "aesthetic"]
        if any(keyword in question_lower for keyword in creative_keywords) or theme == ThemeType.CREATIVE_WRITING:
            return "creative"

        return None

    def _generate_response_instructions(self, question: str, theme: ThemeType, audience: AudienceType, 
                                      question_analysis: Dict[str, str]) -> str:
        """Generate specific instructions for how to answer THIS question for THIS audience"""
        
        instructions = []
        
        # Question-specific approach
        if question_analysis["type"] == "explanation":
            instructions.append(f"Define key terms clearly for {audience.value}, then build understanding step by step")
        elif question_analysis["type"] == "how_to":
            instructions.append(f"Provide clear, actionable steps that {audience.value} can easily follow")
        elif question_analysis["type"] == "problem_solving":
            instructions.append(f"Help diagnose the issue and provide practical solutions suitable for {audience.value}")
        elif question_analysis["type"] == "comparison":
            instructions.append(f"Present clear comparisons with examples relevant to {audience.value}")
        
        # Audience-specific adaptations
        if audience == AudienceType.SMALL_KIDS:
            instructions.append("Use very simple language, fun analogies, and encouraging tone")
        elif audience == AudienceType.TEENAGERS:
            instructions.append("Be engaging and relatable, avoid being preachy, use relevant examples")
        elif audience == AudienceType.UNIVERSITY_LEVEL:
            instructions.append("Include academic rigor, encourage critical thinking, cite sources when relevant")
        elif audience == AudienceType.PROFESSIONALS:
            instructions.append("Focus on practical implementation, efficiency, and real-world application")
        
        # Theme-specific considerations
        if theme == ThemeType.CODING_PROGRAMMING:
            instructions.append("Include clean, well-commented code examples and explain best practices")
        elif theme == ThemeType.ACADEMIC_HELP:
            instructions.append("Encourage learning and understanding rather than just providing answers")
        elif theme == ThemeType.CREATIVE_WRITING:
            instructions.append("Inspire creativity while providing constructive, specific feedback")
        
        return " ".join(instructions)

    def _build_intelligent_prompt(self, model: str, context: ProcessedContext, expert_persona: Dict[str, str],
                                 audience_psychology: Dict[str, str], response_instructions: str,
                                 question_analysis: Dict[str, str], conversation_history: Optional[str]) -> str:
        """Build the final intelligent prompt that combines all elements with advanced prompt engineering"""

        # Get model personality
        model_config = self.model_prompts.get(model, self.model_prompts["claude-3-sonnet"])

        # Detect professional domain for specialized instructions
        professional_domain = self._detect_professional_domain(context.question, context.theme)

        # Get advanced instruction components
        formatting_instructions = self._get_formatting_instructions(question_analysis, context.audience)
        reasoning_pattern = self._get_reasoning_pattern(question_analysis, context.theme)
        quality_safeguards = self._get_quality_safeguards(context.theme, context.audience)
        meta_cognitive_instructions = self._get_meta_cognitive_instructions(question_analysis)

        prompt_parts = [
            # Enhanced model personality and expert role
            f"{model_config['base_personality']}\n",
            f"{expert_persona['role']}.\n",
            f"{expert_persona['expertise']}. {expert_persona['approach']}.\n"
        ]

        # Add professional domain expertise if detected
        if professional_domain and professional_domain in self.professional_roles:
            domain_info = self.professional_roles[professional_domain]
            prompt_parts.extend([
                f"\n**Professional Domain Expertise ({professional_domain.title()}):**",
                f"- Expertise areas: {domain_info['expertise']}",
                f"- Communication: {domain_info['terminology']}",
                f"- Professional ethics: {domain_info['ethics']}",
                f"- Approach: {domain_info['approach']}\n"
            ])

        prompt_parts.extend([
            # Enhanced question analysis and approach
            f"**Question Analysis:** You will receive a {question_analysis['type']} question. {question_analysis['approach']}.\n",

            # Enhanced audience psychology
            f"**Audience Profile ({context.audience.value.replace('_', ' ')}):**",
            f"- Attention & Focus: {audience_psychology['attention_span']}",
            f"- Learning Style: {audience_psychology['learning_style']}",
            f"- Motivation: {audience_psychology['motivation']}",
            f"- Effective Examples: {audience_psychology['examples']}\n",

            # Advanced response framework
            f"**Response Framework:**",
            f"- Content Instructions: {response_instructions}",
            f"- Formatting Guidelines: {formatting_instructions}",
            f"- Reasoning Approach: {reasoning_pattern}\n",

            # Quality assurance framework
            f"**Quality Assurance:**",
            f"- Verification: {quality_safeguards}",
            f"- Self-Assessment: {meta_cognitive_instructions}\n"
        ])

        # Add context if provided
        if context.context:
            prompt_parts.append(f"**Additional Context:** {context.context}\n")

        # Add conversation history if exists
        if conversation_history:
            prompt_parts.append(f"**Previous Conversation:**\n{conversation_history}\n")

        # Enhanced final instructions with chain-of-thought prompting
        prompt_parts.extend([
            f"**Final Instructions:**",
            f"Before responding, take a moment to:",
            f"1. Understand exactly what the {context.audience.value.replace('_', ' ')} audience needs",
            f"2. Consider the most effective way to explain this topic for their level",
            f"3. Choose examples and analogies they can relate to",
            f"4. Structure your response for maximum clarity and engagement",
            f"\nNow provide a comprehensive, accurate, and perfectly tailored response that addresses their question while following all the guidance above."
        ])

        return "\n".join(prompt_parts)

    def _get_builtin_template(self) -> str:
        """Built-in fallback template when files are not available"""
        return """{{ model_personality }}

**Your Task Context:**
- Theme: {{ theme }}
- Subject: {{ inferred_subject }}
- Complexity Level: {{ inferred_complexity }}
- Your strengths in this area: {{ model_strengths }}

**How to approach this {{ theme }} question:**
{{ theme_approach }}

**Response formatting:**
{{ theme_format }}

**Language and explanation style:**
{{ language_level }}
{{ explanation_style }}
{{ encouragement_style }}

**Important reminders:**
{{ theme_verification }}

{% if context %}
**Additional Context:**
{{ context }}
{% endif %}

{% if conversation_history %}
**Recent conversation context:**
{{ conversation_history }}
{% endif %}

{{ thinking_style }} Focus on providing the most helpful response for a {{ inferred_complexity }} level {{ theme }} question."""

    async def create_templates(self):
        """Create template files for each model (for initial setup)"""
        template_dir = Path(__file__).parent.parent / "templates"
        
        # Create generic template
        generic_dir = template_dir / "generic"
        generic_dir.mkdir(parents=True, exist_ok=True)
        
        generic_template = self._get_builtin_template()
        with open(generic_dir / "system_prompt.j2", "w") as f:
            f.write(generic_template)
        
        # Create model-specific templates (initially same as generic)
        for model in self.model_prompts.keys():
            model_dir = template_dir / model
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Start with generic template, can be customized later
            with open(model_dir / "system_prompt.j2", "w") as f:
                f.write(generic_template)
        
        logger.info("Template files created", template_dir=str(template_dir))