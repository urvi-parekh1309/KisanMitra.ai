import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from services.rag_service import rag_service


def run_rag_test():
    print("=" * 80)
    print("AGRICULTURAL RAG PIPELINE: END-TO-END VERIFICATION TEST")
    print("=" * 80)

    # 1. Initialize and ingest documents
    print("\n[Step 1] Ingesting documents into ChromaDB...")
    ingest_result = rag_service.initialize(force_reindex=True)
    print(f"-> Ingestion Result: {ingest_result}")

    # Check status
    status = rag_service.get_status()
    print(f"-> ChromaDB Status: {status}")
    assert status["total_chunks"] > 0, "Error: ChromaDB has 0 chunks!"

    # 2. Test Questions
    test_queries = [
        {
            "name": "Test 1: Cotton Pest Management (Marathi Query)",
            "query": "कापसावरील गुलाबी बोंडअळीचे नियंत्रण कसे करावे आणि फुले चोथा का होतात?",
            "expected_keyword": "cotton",
            "should_find": True
        },
        {
            "name": "Test 2: Soybean Yellow Mosaic & Sowing (Hindi Query)",
            "query": "सोयाबीन की बुवाई कब करनी चाहिए और पीला मोजेक वायरस का लक्षण क्या है?",
            "expected_keyword": "soybean",
            "should_find": True
        },
        {
            "name": "Test 3: Heavy Rainfall Crop Protection (English Query)",
            "query": "How can I protect my standing crop during heavy rainfall and waterlogging?",
            "expected_keyword": "rainfall",
            "should_find": True
        },
        {
            "name": "Test 4: Out-of-Domain Tractor Mechanic Query (Negative Test)",
            "query": "How do I replace the clutch plate in a Mahindra 575 tractor gearbox?",
            "expected_keyword": "none",
            "should_find": False
        }
    ]

    print("\n" + "=" * 80)
    print("EVALUATING RETRIEVAL FOR TEST QUESTIONS")
    print("=" * 80)

    for item in test_queries:
        print(f"\n--- {item['name']} ---")
        print(f"Query: {item['query']}")

        result = rag_service.retrieve(item['query'], top_k=3)
        has_context = result["has_context"]
        sources = result["sources"]

        print(f"Has Context: {has_context}")
        print(f"Sources Found: {len(sources)}")
        for s in sources:
            print(f"  * Document: {s['document']} (Page {s['page']}) | Relevance Score: {s['relevance_score']}")
            print(f"    Snippet: {s['snippet'][:120]}...")

        if item["should_find"]:
            if has_context and len(sources) > 0:
                print("Result: PASSED (Relevant agricultural context successfully retrieved)")
            else:
                print("Result: FAILED (Expected relevant context but none found)")
        else:
            # Negative test: Out-of-domain query should have low relevance or no context
            top_score = sources[0]["relevance_score"] if sources else 0.0
            print(f"Out-of-domain top relevance score: {top_score}")
            if not has_context or top_score < 0.35:
                print("Result: PASSED (Correctly rejected/marked out-of-domain knowledge)")
            else:
                print(f"Result: WARNING (Relevance was {top_score})")

    print("\n" + "=" * 80)
    print("ALL RAG VERIFICATION CHECKS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_rag_test()
