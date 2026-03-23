from groq import Groq

class TextFormatter:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def format_transcript(self, transcript):
        """Formats a raw transcript into a structured Markdown reading guide."""
        system_prompt = """
        You are an expert technical writer. You take raw transcripts from video tutorials and convert them into clean, 
        highly structured, and easily readable Markdown guides.

        Your tasks:
        1.  Strip filler words (uh, um, right, like, you know) and conversational rambling.
        2.  Restructure the content into a logical, step-by-step flow.
        3.  Use clear headers (H1, H2, H3).
        4.  Use bullet points for lists and steps.
        5.  Place commands, code snippets, and terminal output in proper code blocks with the correct language tag.
        6.  Add a "Key Takeaways" summary section at the very top.
        7.  Ensure the output is valid Markdown.

        Maintain the technical accuracy and instructional value of the original content.
        Do not add information that wasn't in the transcript.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Please format the following raw transcript into a Markdown guide:\n\n{transcript}",
                    }
                ],
                model="llama-3.3-70b-versatile", # Replaced decommissioned llama3-70b-8192
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error formatting transcript: {e}")
            return transcript # Fallback to raw if logic fails
