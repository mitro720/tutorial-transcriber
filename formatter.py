from groq import Groq
import json

class TextFormatter:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def format_transcript(self, transcript, visuals=None):
        """Formats a raw transcript into a structured Markdown reading guide, embedding visuals."""
        system_prompt = f"""
        You are a professional technical writer and video editor. Your job is to transform a raw transcript into a high-quality Markdown tutorial.
        
        STRUCTURE:
        - Use clear H1, H2, and H3 headers.
        - Use bullet points and bold text to emphasize key takeaways.
        
        VISUAL INTEGRATION (CRITICAL):
        - You will be provided with a JSON list of 'Captured Moments' (screenshots).
        - Each moment has a 'timestamp', 'screenshot' path, and 'transcript_context'.
        - You MUST integrate these images into the tutorial.
        - Use standard Markdown image syntax: ![Action or Slide Description](captured_visuals/filename.png)
        - Do NOT skip any high-confidence moments.
        - Place the image IMMEDIATELY after the paragraph that matches its timestamp/context.
        
        If no visuals are provided, just format the text normally.
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
