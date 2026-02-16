class LLMInterface:
    def interpret_problem(self, text):
        raise NotImplementedError

    def explain_result(self, result):
        raise NotImplementedError

    def ask_for_missing_info(self, gaps):
        raise NotImplementedError
