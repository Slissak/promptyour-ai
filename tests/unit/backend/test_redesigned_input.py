"""
Test the redesigned user input processing system
"""
import asyncio

from app.models.schemas import UserInput, ThemeType
from app.services.input_processor_v2 import UserInputProcessor


class TestRedesignedInput:
    
    def __init__(self):
        self.processor = UserInputProcessor()
        
        # Test cases covering different scenarios
        self.test_cases = [
            {
                "name": "Academic Math Help",
                "input": UserInput(
                    question="How do I solve quadratic equations using the quadratic formula?",
                    theme=ThemeType.ACADEMIC_HELP,
                    context="I'm in high school algebra class and struggling with this topic"
                ),
                "expected_subject": "mathematics",
                "expected_complexity": "intermediate"
            },
            {
                "name": "Creative Writing Request",
                "input": UserInput(
                    question="Write a short story about a time traveler who meets their younger self",
                    theme=ThemeType.CREATIVE_WRITING,
                    context="Make it philosophical and thought-provoking, about 500 words"
                ),
                "expected_subject": "creative writing",
                "expected_complexity": "intermediate"
            },
            {
                "name": "Professional Programming",
                "input": UserInput(
                    question="How can I optimize this Python algorithm for large datasets?",
                    theme=ThemeType.CODING_PROGRAMMING,
                    context="Working on enterprise application, need production-ready solution with performance metrics"
                ),
                "expected_subject": "programming",
                "expected_complexity": "professional"
            },
            {
                "name": "Business Strategy",
                "input": UserInput(
                    question="What market entry strategy should we use for expanding to European markets?",
                    theme=ThemeType.BUSINESS_PROFESSIONAL,
                    context="Mid-size tech company, B2B SaaS product, limited budget for international expansion"
                ),
                "expected_subject": "business",
                "expected_complexity": "professional"
            },
            {
                "name": "Simple Personal Learning",
                "input": UserInput(
                    question="How do I make sourdough bread?",
                    theme=ThemeType.PERSONAL_LEARNING,
                    context="Complete beginner, never baked bread before"
                ),
                "expected_subject": "general knowledge",
                "expected_complexity": "beginner"
            },
            {
                "name": "Research Analysis",
                "input": UserInput(
                    question="Analyze the correlation between social media usage and teenage mental health",
                    theme=ThemeType.RESEARCH_ANALYSIS,
                    context="Need comprehensive literature review and statistical analysis for academic paper"
                ),
                "expected_subject": "research",
                "expected_complexity": "academic"
            },
            {
                "name": "General Question - Minimal Context",
                "input": UserInput(
                    question="What causes rain?",
                    theme=ThemeType.GENERAL_QUESTIONS,
                    context=None
                ),
                "expected_subject": "science",
                "expected_complexity": "beginner"
            }
        ]

    async def test_input_processing(self):
        """Test the redesigned input processor"""
        print("\n=== Testing Redesigned Input Processing ===")
        
        for test_case in self.test_cases:
            print(f"\n📋 Test: {test_case['name']}")
            print(f"   Question: {test_case['input'].question}")
            print(f"   Theme: {test_case['input'].theme.value}")
            print(f"   Context: {test_case['input'].context or 'None'}")
            
            # Process the input
            result = await self.processor.process_input(test_case["input"])
            
            # Display results
            print(f"\n📊 Results:")
            print(f"   ✓ Inferred Subject: {result.inferred_subject}")
            print(f"   ✓ Inferred Complexity: {result.inferred_complexity}")
            print(f"   ✓ Complexity Score: {result.complexity_score:.2f}")
            print(f"   ✓ Estimated Tokens: {result.estimated_tokens}")
            print(f"   ✓ Processing Confidence: {result.processing_confidence:.2f}")
            print(f"   ✓ Needs Clarification: {result.requires_clarification}")
            
            # Check against expectations
            expected_subject = test_case.get("expected_subject")
            expected_complexity = test_case.get("expected_complexity")
            
            if expected_subject and expected_subject in result.inferred_subject:
                print(f"   ✅ Subject matches expectation ({expected_subject})")
            elif expected_subject:
                print(f"   ⚠️  Subject different from expected ({expected_subject})")
            
            if expected_complexity and expected_complexity == result.inferred_complexity:
                print(f"   ✅ Complexity matches expectation ({expected_complexity})")
            elif expected_complexity:
                print(f"   ⚠️  Complexity different from expected ({expected_complexity})")
            
            print("-" * 60)

    async def test_theme_utilities(self):
        """Test utility methods for theme information"""
        print("\n=== Testing Theme Utilities ===")
        
        # Test get_available_themes
        themes = self.processor.get_available_themes()
        print(f"\n📋 Available Themes ({len(themes)}):")
        for theme in themes:
            print(f"   • {theme['label']} ({theme['value']})")
        
        # Test get_theme_info
        print(f"\n📊 Theme Information Examples:")
        for theme_type in [ThemeType.ACADEMIC_HELP, ThemeType.CODING_PROGRAMMING, ThemeType.CREATIVE_WRITING]:
            info = self.processor.get_theme_info(theme_type)
            print(f"\n   {theme_type.value.replace('_', ' ').title()}:")
            print(f"   • Primary Subjects: {info['primary_subjects']}")
            print(f"   • Complexity Hint: {info['complexity_hint']}")
            print(f"   • Typical Models: {info['typical_models']}")

    async def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n=== Testing Edge Cases ===")
        
        edge_cases = [
            {
                "name": "Very Short Question",
                "input": UserInput(
                    question="Help",
                    theme=ThemeType.GENERAL_QUESTIONS,
                    context=None
                )
            },
            {
                "name": "Very Long Complex Question",
                "input": UserInput(
                    question="I need to develop a comprehensive machine learning pipeline for real-time fraud detection in financial transactions, incorporating ensemble methods, feature engineering, model versioning, A/B testing framework, monitoring and alerting systems, with consideration for regulatory compliance, data privacy, scalability to handle millions of transactions per day, and integration with existing legacy banking infrastructure while maintaining sub-100ms response times and 99.99% uptime requirements.",
                    theme=ThemeType.CODING_PROGRAMMING,
                    context="Enterprise fintech company, strict regulatory environment, existing microservices architecture, team of 15 engineers, 6-month timeline, budget constraints for cloud resources"
                )
            },
            {
                "name": "Conflicting Theme and Content",
                "input": UserInput(
                    question="Write advanced machine learning algorithms for image recognition",
                    theme=ThemeType.CREATIVE_WRITING,  # Wrong theme
                    context="Need production-ready code with TensorFlow"
                )
            }
        ]
        
        for test_case in edge_cases:
            print(f"\n📋 Edge Case: {test_case['name']}")
            result = await self.processor.process_input(test_case["input"])
            
            print(f"   ✓ Subject: {result.inferred_subject}")
            print(f"   ✓ Complexity: {result.inferred_complexity} (score: {result.complexity_score:.2f})")
            print(f"   ✓ Confidence: {result.processing_confidence:.2f}")
            print(f"   ✓ Needs Clarification: {result.requires_clarification}")
            
            if result.requires_clarification:
                print(f"   ⚠️  System flagged this for clarification (low confidence)")

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Testing Redesigned User Input Processing")
        print("=" * 70)
        
        try:
            await self.test_input_processing()
            await self.test_theme_utilities()
            await self.test_edge_cases()
            
            print("\n" + "=" * 70)
            print("✅ ALL TESTS COMPLETED!")
            print("\nRedesigned Input Processing Features:")
            print("  ✓ Theme-based input structure")
            print("  ✓ Smart subject inference from theme + content")
            print("  ✓ Complexity detection with confidence scoring")
            print("  ✓ Token estimation for cost prediction")
            print("  ✓ Clarification flagging for ambiguous inputs")
            print("  ✓ Utility methods for UI integration")
            print("\nThe system now handles:")
            print("  • User question/request (main input)")
            print("  • Theme selection from dropdown")
            print("  • Additional context sentences")
            print("  • Automatic subject and complexity inference")
            print("  • Confidence-based quality control")
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test = TestRedesignedInput()
    asyncio.run(test.run_all_tests())