# The Anti-Larp Machine
Upload your own code and find out whether you actually understand it. The app reads your code files, then quizzes you on them with multiple-choice questions, each tied to the exact line it came from. Built for the **Hacktoberfest MLH x MSJC CSC Mini Hackathon 2026**.

## Problem
Plenty of students ship code they can't explain, whether it came from a YouTube tutorial or AI, and then freeze when an interviewer asks about it. There's no quick way to test your own understanding of your own project.

## How It Works
1. Upload one or more code files.
2. Each file is split into overlapping 40-line chunks that remember their file and line range, then stored in an in-memory vector database.
3. The most relevant chunks are retrieved (or the ones matching a topic you type in).
4. A local open-weight model writes questions that ask what your code produces or what breaks if something changes.
5. The code shuffles the answer choices, finds the quoted snippet in your file, and shows its file and line number.
6. You answer, and get a score plus a verdict on whether you understand your own code.

## Open-Weight AI
- **Model:** [Llama 3.1 8B](https://ollama.com/library/llama3.1) by Meta, run locally through [Ollama](https://ollama.com). Used under the Llama 3.1 Community License (see the model page for the full terms). It is a small language model (8B parameters, under the 10B threshold).
- **Dependencies:** Streamlit, ChromaDB, Ollama Python client.

## Getting Started
Requires Python 3.10+ and [Ollama](https://ollama.com).

## What We Built (Features) 
- Line-aware code chunking that tracks file names and line ranges
- Retrieval over your code with ChromaDB, with an optional topic focus
- A prompt that asks the model to trace the code and ask about behavior, not trivia
- Answer shuffling in code, so the answer key doesn't depend on the model picking a letter
- Snippet checking that finds each quoted line in your file and reports its real line number
- The Streamlit interface and the scoring verdicts

## License
Released under the [MIT License](LICENSE).
