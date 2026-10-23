import json
import random
import re
import sys
from uuid import uuid4


import chromadb
import ollama


MODEL = "llama3.1:8b"  


norm = lambda t: re.sub(r"[\s()]+", "", t.lower())




def make_quiz(files, n=3, topic=""):
    """files: list of (filename, text) tuples."""
    # 1. Split each file into overlapping 40-line chunks that remember file + line range
    chunks = []
    for name, text in files:
        lines = text.splitlines()
        for i in range(0, len(lines), 30):
            body = "\n".join(lines[i:i + 40])
            if body.strip():
                chunks.append((name, i + 1, min(i + 40, len(lines)), body))
    if not chunks:
        return []


    # 2. Index in ChromaDB (built-in all-MiniLM-L6-v2 embeddings, in memory)
    col = chromadb.EphemeralClient().create_collection(uuid4().hex)
    col.add(ids=[str(i) for i in range(len(chunks))],
            documents=[c[3] for c in chunks],
            metadatas=[{"file": c[0], "start": c[1], "end": c[2]} for c in chunks])


    # 3. Get most relevant chunks
    query = topic.strip() or "main logic, algorithms, error handling, data structures"
    top = col.query(query_texts=[query], n_results=min(max(3, n + 1), len(chunks)))
    docs, metas = top["documents"][0], top["metadatas"][0]


    # 4. Ask the model to do its JOB
    sources = "\n\n".join(f"[Source {i + 1}] {m['file']}, lines {m['start']}-{m['end']}\n{d}"
                          for i, (d, m) in enumerate(zip(docs, metas)))
    prompt = f"""You are a tough technical interviewer. Using ONLY the code below, write {n}
multiple-choice questions that test whether the author understands it.
Each question must give a concrete scenario and ask for the result.
Trace through the code step by step before choosing the correct answer. All four options must be
clearly different from each other. Never ask what a line "does" or its "purpose".
Wrong answers must be plausible mistakes a careless developer might believe. Only ask about things the code shows.


{sources}


Return JSON: {{"questions": [{{"question": "...", "reasoning": "short step-by-step trace through the code",
"correct": "the one right answer", "wrong": ["...", "...", "..."],
"explanation": "why the correct answer is right, based on the code",
"evidence": "one line of code copied exactly from the sources"}}]}}"""


    r = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}],
                    format="json", options={"temperature": 0.3})
    try:
        data = json.loads(r["message"]["content"])
    except json.JSONDecodeError:
        return []


    # 5. Shuffle answers in code, find the quote's real chunk and line number
    out = []
    items = data.get("questions", []) if isinstance(data, dict) else data
    strip = lambda o: re.sub(r"^[A-Da-d][.)]\s*", "", str(o)).strip()
    for q in items:
        try:
            right = strip(q["correct"])
            opts = [strip(w) for w in q["wrong"]][:3]
            assert len(opts) == 3 and right and right not in opts
            opts.append(right)
            random.shuffle(opts)
            ev = str(q.get("evidence", "")).strip()
            s = next((i for i, d in enumerate(docs) if ev and norm(ev) in norm(d)), None)
            m = metas[s if s is not None else 0]
            ln = next((i for i, l in enumerate(dict(files)[m["file"]].splitlines(), 1)
                       if ev and norm(ev) in norm(l)), None)
            out.append({
                "question": q["question"],
                "options": [f"{'ABCD'[i]}. {o}" for i, o in enumerate(opts)],
                "answer": "ABCD"[opts.index(right)],
                "explanation": q.get("explanation", ""),
                "citation": {"file": m["file"], "lines": str(ln) if ln else f"{m['start']}-{m['end']}",
                             "passage": ev, "verified": s is not None},
            })
        except (KeyError, ValueError, IndexError, TypeError, AttributeError, AssertionError):
            pass
    return out[:n]




if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python pipeline.py path/to/your_code.py")
    files = [(p, open(p, encoding="utf-8", errors="ignore").read()) for p in sys.argv[1:]]
    print(json.dumps(make_quiz(files), indent=2))
