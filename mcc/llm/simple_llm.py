import subprocess
import json

MODEL_NAME = 'llama3:8b'


class SimpleLLM:
    def _run(self, prompt: str) -> str:
        process = subprocess.Popen(
            ['ollama', 'run', MODEL_NAME],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        stdout, stderr = process.communicate(prompt)

        if stdout and stdout.strip():
            return stdout.strip()

        if stderr and stderr.strip():
            return f'[LLM error] {stderr.strip()}'

        return ''


    # -------------------------------
    # 1. INTENT INTERPRETATION
    # -------------------------------
    def interpret_problem(self, text: str) -> dict:
        prompt = f'''
You are an engineering assistant.

TASK:
Interpret the user's intent.

RULES:
- Do NOT generate parameters
- Do NOT invent assumptions
- Do NOT solve anything
- Only summarize intent and objectives

User request:
{text}
'''
        return {
            'intent_summary': self._run(prompt)
        }


    # -------------------------------
    # 2. RESULT EXPLANATION
    # -------------------------------
    def explain_result(self, payload: dict) -> str:
        prompt = f'''
You are an engineering assistant.

TASK:
Explain the CURRENT result.

RULES:
- Use ONLY the provided data
- Do NOT invent numbers
- Do NOT recompute results
- Do NOT suggest actions

Payload:
{json.dumps(payload, indent=2)}
'''
        return self._run(prompt)


    # -------------------------------
    # 3. MEMORY-AWARE COMPARISON
    # -------------------------------
    def compare_with_memory(self, payload: dict) -> str:
        prompt = f'''
You are an engineering assistant.

TASK:
Compare the CURRENT result with the BASELINE result.

RULES:
- Explicitly contrast current vs baseline
- Use ONLY provided values
- Do NOT invent improvements
- Do NOT suggest changes

Payload:
{json.dumps(payload, indent=2)}
'''
        return self._run(prompt)


    # -------------------------------
    # 4. FAILURE EXPLANATION
    # -------------------------------
    def explain_failure(self, failure_payload: dict) -> str:
        prompt = f'''
You are an engineering assistant.

TASK:
Explain why the system could not proceed.

RULES:
- Be explicit and factual
- Do NOT guess missing values
- Do NOT suggest fixes automatically

Failure details:
{json.dumps(failure_payload, indent=2)}
'''
        return self._run(prompt)


    # -------------------------------
    # 5. RESEARCH QUESTIONS (READ-ONLY)
    # -------------------------------
    def generate_research_questions(self, context: dict) -> dict:
        prompt = f'''
You are a research companion for an engineering system.

TASK:
Ask 3 to 5 research questions that could guide future exploration.

RULES:
- QUESTIONS ONLY
- No numbers
- No parameters
- No actions
- Base questions ONLY on the given context

Context:
{json.dumps(context, indent=2)}
'''
        text = self._run(prompt)

        questions = [
            line.strip('- ').strip()
            for line in text.splitlines()
            if line.strip().endswith('?')
        ]

        return {
            'research_questions': questions
        }
