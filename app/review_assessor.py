# app/review_assessor.py

import logging
from langchain.prompts import PromptTemplate
from openai import OpenAIError
from app.llm_client import LLMClient

class ReviewAssessor:
    PROMPT_TEMPLATE = '''
Please evaluate the quality of the following code review:

{review}

Evaluation criteria:
- How clearly and precisely does the review point out errors? (Score from 0 to 10)
- How useful are the suggestions for improving the code? (Score from 0 to 10)
- How comprehensive is the review in covering potential issues in the code? (Score from 0 to 10)

Return the result in the following format:
{{
    "clarity": <score>,
    "usefulness": <score>,
    "coverage": <score>,
    "overall": <overall score from 0 to 10>,
    "comments": "<comments on improving the review>"
}}
'''

    def __init__(self):
        self.llm = LLMClient.get_instance().get_llm()
        self.prompt = PromptTemplate(
            input_variables=['review'],
            template=self.PROMPT_TEMPLATE
        )

    def judge_review(self, review_text):
        chain = self.prompt | self.llm
        try:
            assessment = chain.invoke({'review': review_text})
            return assessment.content if hasattr(assessment, 'content') else ""
        except OpenAIError as e:
            logging.error(f"Error during review quality assessment: {e}")
            return ""

    def is_review_low_quality(self, assessment):
        overall_score = assessment.get("overall")
        if overall_score is None:
            logging.warning("Overall score missing in assessment result.")
            return True
        try:
            return float(overall_score) < 5
        except (ValueError, TypeError):
            logging.warning("Invalid overall score in assessment result.")
            return True
