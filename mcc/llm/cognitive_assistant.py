from mcc.core.mcc import MinimalCognitiveCore
from mcc.llm.simple_llm import SimpleLLM
from mcc.core.persistent_memory import PersistentMemory


class CognitiveAssistant:
    def __init__(self):
        self.mcc = MinimalCognitiveCore()
        self.llm = SimpleLLM()
        self.memory = PersistentMemory()

    def solve_from_text(self, text, problem_state):
        # 1. Interpret intent (soft)
        intent = self.llm.interpret_problem(text)

        # 2. Solve formally (hard authority)
        result = self.mcc.solve(problem_state)

        # 3. Handle failures explicitly
        if result.get('status') != 'completed':
            explanation = self.llm.explain_failure(result)
            return {
                'status': result.get('status'),
                'intent': intent,
                'details': result,
                'explanation': explanation
            }

        # 4. Explanation of current result
        explanation = self.llm.explain_result({
            'result': result
        })

        # 5. Memory-aware comparison (if baseline exists)
        history = self.memory.query_all()
        comparison = None

        if history:
            comparison = self.llm.compare_with_memory({
                'current': result,
                'memory': history
            })

        # 6. Research questions (read-only cognition)
        research_questions = self.llm.generate_research_questions({
            'current_result': result,
            'memory': history
        })

        return {
            'status': 'completed',
            'intent': intent,
            'result': result,
            'explanation': explanation,
            'comparison': comparison,
            'research_questions': research_questions
        }
