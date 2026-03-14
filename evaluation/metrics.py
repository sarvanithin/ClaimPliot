class AppealMetrics:
    @staticmethod
    def score_classification(expected_category: str, actual_category: str) -> float:
        return 1.0 if expected_category.lower() == actual_category.lower() else 0.0
        
    @staticmethod
    def _calculate_f1(expected: list[str], actual: str) -> float:
        if not expected:
            return 1.0
        actual_lower = actual.lower()
        matched = sum(1 for term in expected if term.lower() in actual_lower)
        precision = matched / max(len(actual.split()), 1)
        recall = matched / len(expected)
        
        # We simplify this by just measuring recall (presence of expected terms)
        return recall
        
    @staticmethod
    def score_appeal_completeness(expected_terms: list[str], output_text: str) -> float:
        return AppealMetrics._calculate_f1(expected_terms, output_text)
        
    @staticmethod
    def score_citation_specificity(min_references: int, actual_references: int) -> float:
        if min_references == 0:
            return 1.0
        return min(actual_references / min_references, 1.0)
        
    @staticmethod
    def score_professional_tone(output_text: str) -> float:
        # Simple heuristic: no all-caps sentences or aggressive exclamation points
        # In a real system, use an LLM-as-a-judge for this metric
        unprofessional_flags = ["!!!", "OUTRAGEOUS", "SUE", "STUPID"]
        for flag in unprofessional_flags:
            if flag in output_text.upper():
                return 0.0
        
        return 1.0

    @staticmethod
    def calculate_overall(scores: dict) -> float:
        weights = {
            "classification_accuracy": 0.3,
            "appeal_completeness": 0.3,
            "citation_specificity": 0.2,
            "professional_tone": 0.2
        }
        
        overall = 0.0
        for k, v in weights.items():
            overall += scores.get(k, 0.0) * v
            
        return overall
