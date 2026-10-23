import json
import streamlit as st


from pipeline import make_quiz


st.set_page_config(page_title="Anti-LARP Machine",)


st.title("The Anti-LARP Machine.", text_alignment="center")
st.caption("Upload your own code. Find out if you actually get it...larp.",  text_alignment="center")


uploaded = st.file_uploader(
    "Upload your code", accept_multiple_files=True,
    type=["py", "js", "ts", "jsx", "tsx", "java", "c", "cpp", "cs", "go", "rs", "rb", "php", "txt"])
topic = st.text_input("Function or concept to focus on (optional)")
num_questions = st.slider("Number of questions", 1, 5, 3)


if uploaded and st.button("Start the interview"):
    for k in [k for k in st.session_state if k.startswith("q") and k[1:].isdigit()]:
        del st.session_state[k]
    st.session_state.submitted = False
    st.session_state.quiz = []
    try:
        with st.spinner("Reading your code and sharpening questions..."):
            files = [(f.name, f.getvalue().decode("utf-8", errors="ignore")) for f in uploaded]
            st.session_state.quiz = make_quiz(files, num_questions, topic)
        if not st.session_state.quiz:
            st.warning("No questions generated. The file may be empty, or the model returned unusable output. Try again.")
    except Exception as e:
        st.error(f"Something went wrong: {e}. Is Ollama running?")


quiz = st.session_state.get("quiz")


if quiz:
    st.divider()
    for i, q in enumerate(quiz):
        st.subheader(f"Q{i + 1}. {q['question']}")
        st.radio("Choose one:", q["options"], index=None, key=f"q{i}")


    if st.button("Check answers"):
        st.session_state.submitted = True


    if st.session_state.get("submitted"):
        st.divider()
        score = 0
        for i, q in enumerate(quiz):
            choice = st.session_state.get(f"q{i}")
            correct = choice is not None and choice[0] == q["answer"]
            score += correct
            if correct:
                st.success(f"Q{i + 1}: Correct")
            else:
                st.error(f"Q{i + 1}: Incorrect. Answer: {q['answer']}")
            st.write(q["explanation"])
            c = q["citation"]
            badge = "Verified in your code!" if c["verified"] else "Couldn't verify this snippet :("
            st.caption(f"{c['file']}, lines {c['lines']} ({badge})")
            if c["passage"].strip():
                st.code(c["passage"])
        pct = score / len(quiz)
        st.metric("Understanding of your own code", f"{score} / {len(quiz)}")
        if pct == 1:
            st.balloons()
            st.success("You wrote this. Probably. Hire this person.")
        elif pct >= 0.5:
            st.warning("you aight...")
        else:
            st.error("larp, go back to the lobby")


    st.download_button("Download questions (JSON)", json.dumps(quiz, indent=2), "questions.json")
