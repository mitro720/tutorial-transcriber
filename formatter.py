from groq import Groq

class TextFormatter:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def format_transcript(self, transcript, visuals=None):
        """Formats a raw transcript into a structured Markdown reading guide, embedding visuals."""
        system_prompt = """
        You are an expert technical writer. You take raw transcripts from video tutorials and convert them into clean, 
        highly structured, and easily readable Markdown guides.

        Your tasks:
        1.  Strip filler words and conversational rambling.
        2.  Restructure the content into a logical, step-by-step flow.
        3.  Use clear headers (H1, H2, H3).
        4.  Use bullet points for lists and steps.
        5.  Place commands, code snippets, and terminal output in proper code blocks.
        6.  Add a "Key Takeaways" summary section at the very top.
        7.  **VISUAL EMBEDDING**: You will be provided with a list of captured visuals (screenshots) with timestamps. 
            Embed these images in the Markdown guide using `![description](captured_visuals/filename.png)` 
            at the most relevant point in the text based on the timestamp and context provided.

        Ensure the output is valid Markdown.
        """

        user_content = f"Raw Transcript:\n{transcript}\n\n"
        if visuals:
            user_content += "Captured Visuals (Embed these!):\n"
            user_content += json.dumps(visuals, indent=2)

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please format this into a Markdown guide and embed the visuals correctly:\n\n{user_content}"}
                ],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Error formatting transcript: {e}")
            return transcript
