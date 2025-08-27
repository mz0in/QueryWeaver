"""Relevancy agent for determining relevancy of queries to database schema."""

import json
from litellm import completion
from api.config import Config
from .utils import BaseAgent, parse_response


RELEVANCY_PROMPT = """
You are an expert assistant tasked with determining whether the user's question can be translated into a database query, regardless of how it's phrased. You receive two inputs:

The user's question: {QUESTION_PLACEHOLDER}
The database description: {DB_PLACEHOLDER}

Please follow these instructions:

Understand the question's intent and potential for database querying.
• Ask yourself: "Can this question be answered by querying data from the database, even if it contains personal language or conversational elements?"
• Focus on the ACTIONABLE INTENT rather than the phrasing style.
• Questions with personal pronouns (I, my, me) are ALLOWED if they seek database information (e.g., "Show me the sales data", "I want to see customer records").
• Conversational or personality-filled questions are ALLOWED if they have a clear data request (e.g., "I'm curious about our revenue trends", "Can you help me understand our customer demographics?").
• Common tables and business concepts are considered "On-topic" even if not explicitly mentioned in the database description.
• Questions about database structure, data analysis, reports, and insights are ALWAYS on-topic.

Only reject questions that are:
• Completely unrelated to data, databases, or business information
• Asking about the AI system itself (not about data)
• Requesting personal information about individuals not in the database
• Offensive, illegal, or violating content guidelines

Determine if the question is:
• On-topic and appropriate:
– If the question can potentially be answered with database queries, regardless of personal language used, provide:
{{
"status": "On-topic",
"reason": "Brief explanation of why it can be translated to a database query."
"suggestions": []
}}

• Off-topic:
– If the question cannot be answered with any database query and is completely unrelated to data analysis, provide:
{{
"status": "Off-topic",
"reason": "Short reason explaining why it cannot be translated to a database query.",
"suggestions": [
"An alternative, high-level question about the schema..."
]
}}

• Inappropriate:
– If the question is offensive, illegal, or otherwise violates content guidelines, provide:
{{
"status": "Inappropriate",
"reason": "Short reason why it is inappropriate.",
"suggestions": [
"Suggested topics that would be more appropriate..."
]
}}

Remember: Prioritize the question's potential for database querying over its conversational style or personal language.
"""


class RelevancyAgent(BaseAgent):
    # pylint: disable=too-few-public-methods
    """Agent for determining relevancy of queries to database schema."""

    async def get_answer(self, user_question: str, database_desc: dict) -> dict:
        """Get relevancy assessment for user question against database description."""
        self.messages.append(
            {
                "role": "user",
                "content": RELEVANCY_PROMPT.format(
                    QUESTION_PLACEHOLDER=user_question,
                    DB_PLACEHOLDER=json.dumps(database_desc),
                ),
            }
        )
        completion_result = completion(
            model=Config.COMPLETION_MODEL,
            messages=self.messages,
            temperature=0,
        )

        answer = completion_result.choices[0].message.content
        self.messages.append({"role": "assistant", "content": answer})
        return parse_response(answer)
