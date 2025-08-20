import streamlit as st
from groq import Groq

client = Groq(api_key="ENTER_YOUR_API_KEY_HERE")

# Streamlit UI
st.title("AI Outfit Recommendation")
user_prompt = st.text_input("Describe the occasion and your preferences:")

if st.button("Get Recommendation") and user_prompt:
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are an AI-powered outfit recommendation assistant."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    st.write("AI Recommendation:")
    for chunk in completion:
        st.write(chunk.choices[0].delta.content or "")

