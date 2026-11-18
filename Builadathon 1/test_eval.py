import os
from dotenv import load_dotenv
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric

load_dotenv()

def test_governance_rag_pipeline():
    # Simulated query, actual LLM response, and retrieved context from ChromaDB
    user_query = "What is the budget burn threshold limit?"
    retrieved_context = ["Section 7.1: Milestone 3 budget burn rate shall not exceed 80.0% of allocated phase budget."]
    llm_output = "The budget burn limit for Milestone 3 is 80.0% according to Section 7.1."

    # Define DeepEval metrics
    faithfulness_metric = FaithfulnessMetric(threshold=0.7, model="gpt-4o-mini", include_reason=True)
    relevancy_metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o-mini", include_reason=True)

    test_case = LLMTestCase(
        input=user_query,
        actual_output=llm_output,
        retrieval_context=retrieved_context
    )

    # Assert test passes metrics evaluation
    assert_test(test_case, [faithfulness_metric, relevancy_metric])

if __name__ == "__main__":
    test_governance_rag_pipeline()
    print("DeepEval test passed successfully!")