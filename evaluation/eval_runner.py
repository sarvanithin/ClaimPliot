import json
import os
import time
from backend.models.claim import Claim
from backend.agent.engine import ClaimPilotAgent
from evaluation.metrics import AppealMetrics

def run_evaluation(test_cases_path: str = "evaluation/test_cases.json"):
    print("=== ClaimPilot Evaluation Harness ===")
    
    if not os.path.exists(test_cases_path):
        print(f"Test cases file not found at {test_cases_path}")
        return
        
    os.makedirs("evaluation/results", exist_ok=True)
        
    with open(test_cases_path, "r") as f:
        test_cases = json.load(f)
        
    agent = ClaimPilotAgent()
    metrics = AppealMetrics()
    
    results = []
    total_scores = {
        "classification_accuracy": 0,
        "appeal_completeness": 0,
        "citation_specificity": 0,
        "professional_tone": 0
    }
    
    start_time = time.time()
    
    for i, tc in enumerate(test_cases):
        print(f"Running Test Case {i+1}/{len(test_cases)}: {tc['name']}")
        
        # Mock claim execution
        claim_data = tc["claim"]
        claim = Claim(**claim_data)
        
        try:
            result = agent.process_claim(claim)
            
            # Score
            expected = tc["expected"]
            class_score = metrics.score_classification(expected["category"], result.analysis.denial_category)
            
            completeness_score = metrics.score_appeal_completeness(
                expected.get("appeal_should_contain", []), 
                result.appeal.full_text
            )
            
            citation_score = metrics.score_citation_specificity(
                expected.get("min_policy_references", 0),
                len(result.policies)
            )
            
            tone_score = metrics.score_professional_tone(result.appeal.full_text)
            
            tc_scores = {
                "classification_accuracy": class_score,
                "appeal_completeness": completeness_score,
                "citation_specificity": citation_score,
                "professional_tone": tone_score
            }
            
            overall = metrics.calculate_overall(tc_scores)
            
            for k, v in tc_scores.items():
                total_scores[k] += v
                
            results.append({
                "id": tc["id"],
                "name": tc["name"],
                "scores": tc_scores,
                "overall": overall
            })
            
        except Exception as e:
            print(f"Error processing {tc['id']}: {e}")
            results.append({"id": tc["id"], "error": str(e), "overall": 0.0})
            
    # Calculate Averages
    num_cases = len(test_cases)
    avg_scores = {k: v / num_cases for k, v in total_scores.items()}
    final_overall = metrics.calculate_overall(avg_scores)
    
    print("\n=== Evaluation Results ===")
    print(f"Total Test Cases: {num_cases}")
    print(f"Classification accuracy: {avg_scores['classification_accuracy'] * 100:.1f}%")
    print(f"Appeal completeness: {avg_scores['appeal_completeness'] * 100:.1f}%")
    print(f"Citation specificity: {avg_scores['citation_specificity'] * 100:.1f}%")
    print(f"Overall score: {final_overall * 100:.1f}%")
    print(f"Time elapsed: {time.time() - start_time:.2f}s")
    
    with open("evaluation/results/eval_run.json", "w") as f:
        json.dump({
            "averages": avg_scores,
            "overall": final_overall,
            "details": results
        }, f, indent=4)
        
if __name__ == "__main__":
    run_evaluation()
