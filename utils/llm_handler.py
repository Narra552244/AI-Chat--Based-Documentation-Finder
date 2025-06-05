from typing import List, Dict
import os
from openai import OpenAI

class LLMHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")

    def get_response(self, query: str, context: List[Dict]) -> str:
        """Get response from LLM using context."""
        try:
            # Prepare context string from relevant chunks
            context_str = "\n\n".join([
                f"From {c['file_info']['file_name']}:\n{c['chunk']}"
                for c in context if c['file_info']
            ])

            messages = [
                {"role": "system", "content": (
                    "You are a helpful assistant that answers questions based on the provided documentation. "
                    "Always provide accurate information based on the context given. "
                    "If you're not sure about something, say so. "
                    "Include relevant source file names in your response when appropriate."
                )},
                {"role": "user", "content": f"""
                Context:
                {context_str}

                Question: {query}
                """}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error getting LLM response: {str(e)}")

    def analyze_query_log(self, queries: List[Dict]) -> str:
        """Analyze query patterns and generate insights."""
        try:
            query_text = "\n".join([
                f"- Query: {q['query']}, Timestamp: {q['timestamp']}"
                for q in queries[-50:]  # Analyze last 50 queries
            ])

            messages = [
                {"role": "system", "content": (
                    "Analyze the provided query log and generate insights about: "
                    "1. Common themes in questions "
                    "2. Potential gaps in documentation "
                    "3. Recommendations for improvement"
                )},
                {"role": "user", "content": f"Query Log:\n{query_text}"}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error analyzing queries: {str(e)}") 