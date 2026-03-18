import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize(text):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize clearly"},
            {"role": "user", "content": text}
        ]
    )

    return response.choices[0].message.content


def translate(text, language):

    prompt = f"Translate this text to {language}: {text}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Professional translator"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content