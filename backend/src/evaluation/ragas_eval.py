import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

# --- Patch: stub out the missing langchain_community.chat_models.vertexai module ---
# ragas unconditionally imports ChatVertexAI even when not using Google Vertex AI.
# Newer langchain-community versions removed this submodule, breaking the import.
# Since we never use VertexAI (we use Ollama), we inject a harmless placeholder.
import types

if "langchain_community.chat_models.vertexai" not in sys.modules:
    fake_module = types.ModuleType("langchain_community.chat_models.vertexai")

    class ChatVertexAI:
        """Placeholder - not used, only exists to satisfy ragas's unconditional import."""
        pass

    fake_module.ChatVertexAI = ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = fake_module
# --- End patch ---

import pandas as pd
from datasets import Dataset

from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_ollama import ChatOllama, OllamaEmbeddings

from retrieval.vector_store import query_store
from generation.llm import generate_answer_raw
from utils.config import OLLAMA_MODEL, OLLAMA_EMBED_MODEL
from evaluation.eval_dataset import EVAL_QUESTIONS


# Set to a smaller number (e.g. 5) for a quick test run, or None to run the full eval set
LIMIT_QUESTIONS = 3


def run_pipeline_for_eval(top_k: int = 3):
    """
    Run every eval question through the actual RAG pipeline,
    collecting question, generated answer, retrieved contexts, and ground truth.
    """
    records = []

    questions_to_run = EVAL_QUESTIONS[:LIMIT_QUESTIONS] if LIMIT_QUESTIONS else EVAL_QUESTIONS

    for item in questions_to_run:
        question = item["question"]
        role = item["role"]
        ground_truth = item["ground_truth"]

        print(f"Running: {question}  (role: {role})")

        retrieved_chunks = query_store(question, user_role=role, top_k=top_k)
        contexts = [chunk["text"] for chunk in retrieved_chunks]

        result = generate_answer_raw(question, retrieved_chunks)
        answer = result["answer"]

        # RAGAS (current versions) expects these specific column names
        records.append({
            "user_input": question,
            "response": answer,
            "retrieved_contexts": contexts if contexts else ["No context retrieved."],
            "reference": ground_truth,
        })

    return records


def run_ragas_evaluation():
    records = run_pipeline_for_eval()
    dataset = Dataset.from_list(records)

    # Point RAGAS at your local Ollama model instead of OpenAI
    judge_llm = ChatOllama(model=OLLAMA_MODEL, request_timeout=300.0)
    judge_embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)

    # Force sequential execution (max_workers=1) with a generous timeout,
    # since local Ollama can't handle RAGAS's default high concurrency well.
    run_config = RunConfig(
        timeout=300,      # seconds per individual call
        max_workers=1,    # run one at a time - critical for local LLMs
        max_retries=2,
    )

    print(f"\nEvaluating {len(records)} questions.")
    print("Running RAGAS evaluation sequentially (this will take a while with a local model)...\n")

    results = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=judge_llm,
        embeddings=judge_embeddings,
        run_config=run_config,
    )

    df = results.to_pandas()

    output_path = Path(__file__).resolve().parent.parent.parent / "eval_results.csv"
    df.to_csv(output_path, index=False)

    print("\n=== Columns returned by RAGAS ===")
    print(df.columns.tolist())

    print("\n=== RAGAS Evaluation Results ===\n")
    display_cols = [c for c in ["user_input", "faithfulness", "answer_relevancy", "context_precision", "context_recall"] if c in df.columns]
    print(df[display_cols].to_string())

    print("\n=== Average Scores ===")
    for metric in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        if metric in df.columns:
            print(f"{metric}: {df[metric].mean():.3f}")

    print(f"\nFull results saved to: {output_path}")

    return df


if __name__ == "__main__":
    run_ragas_evaluation()