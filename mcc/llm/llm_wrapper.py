class LLMWrapper:
    def interpret_intent(self, user_text):
        """
        Convert raw user text into a structured ProblemState dictionary.
        This is a stub: it does NOT guess or infer values.
        """
        return {
            "goal": user_text,
            "knowns": {},
            "unknowns": ["unspecified_parameters"],
            "constraints": [],
            "assumptions": [],
            "criteria": {}
        }

    def formulate_questions(self, gaps):
        questions = []
        for gap in gaps:
            if gap["type"] == "missing_inputs":
                questions.append(
                    "Please provide values for: " + ", ".join(gap["items"])
                )
            elif gap["type"] == "missing_constraints":
                questions.append("Please specify applicable constraints.")
            elif gap["type"] == "missing_criteria":
                questions.append("Please specify evaluation objectives.")
            elif gap["type"] == "implicit_assumptions":
                questions.append("Please state your assumptions explicitly.")
        return questions

    def explain_result(self, result):
        if result.get("status") == "needs_information":
            return "Additional information is required before proceeding."

        explanation = []
        explanation.append("A provisional solution was selected.")

        if "score_breakdown" in result and result["score_breakdown"]:
            explanation.append("Objective trade-offs:")
            for k, v in result["score_breakdown"].items():
                explanation.append(f"- {k}: {v}")

        explanation.append(
            "Iterations performed: " + str(result.get("iterations"))
        )
        return "\n".join(explanation)
