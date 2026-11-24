import sys
from pathlib import Path
from starlette.testclient import TestClient

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from main import app


def run_api_tests():
    print("=" * 80)
    print("FASTAPI BACKEND: FULL API TEST SUITE")
    print("=" * 80)

    client = TestClient(app)

    # Test 1: Frontend and Root endpoints
    print("\n[Test 1] GET / and /api/info")
    r1 = client.get("/")
    print(f"GET / Status: {r1.status_code}")
    assert r1.status_code == 200, "Frontend serving failed"
    assert "<!DOCTYPE html>" in r1.text, "Expected index.html content"

    r1_info = client.get("/api/info")
    print(f"GET /api/info Status: {r1_info.status_code}")
    assert r1_info.status_code == 200, "API info endpoint failed"

    # Test 2: Health check
    print("\n[Test 2] GET /api/health")
    r2 = client.get("/api/health")
    print(f"Status: {r2.status_code}")
    print(f"Response: {r2.json()}")
    assert r2.status_code == 200, "Health endpoint failed"

    # Test 3: Weather endpoint
    print("\n[Test 3] GET /api/weather?location=Nagpur")
    r3 = client.get("/api/weather?location=Nagpur")
    print(f"Status: {r3.status_code}")
    w_data = r3.json()
    print(f"Location: {w_data['location']} | Temp: {w_data['temperature_c']} C | Advisories: {len(w_data['agricultural_advisories'])}")
    assert r3.status_code == 200, "Weather endpoint failed"

    # Test 4: Mandi price endpoint
    print("\n[Test 4] GET /api/mandi?commodity=Cotton")
    r4 = client.get("/api/mandi?commodity=Cotton")
    print(f"Status: {r4.status_code}")
    m_data = r4.json()
    print(f"Status: {m_data['status']} | Records Found: {m_data['count']}")
    if m_data["count"] > 0:
        top = m_data["data"][0]
        print(f"Top Mandi: {top['market']} | Modal Price: Rs {top['modal_price']}/{top['unit']}")
    assert r4.status_code == 200, "Mandi endpoint failed"

    # Test 5: Soil advisory endpoint
    print("\n[Test 5] POST /api/soil/advisory")
    soil_payload = {
        "soil_type": "black",
        "ph": 7.2,
        "land_size_acres": 5.0,
        "preferred_crop": "Cotton",
        "language": "mr"
    }
    r5 = client.post("/api/soil/advisory", json=soil_payload)
    print(f"Status: {r5.status_code}")
    s_data = r5.json()
    print(f"Profile: {s_data['soil_profile']}")
    print(f"Suitability: {s_data['crop_suitability']}")
    assert r5.status_code == 200, "Soil endpoint failed"

    # Test 6: Multilingual Chatbot (Marathi Query with RAG)
    print("\n[Test 6] POST /api/chat (Marathi Query on Cotton Pink Bollworm)")
    chat_payload_mr = {
        "query": "कापसावरील गुलाबी बोंडअळी कशी ओळखावी आणि तिचे नियंत्रण कसे करावे?",
        "language": "mr",
        "location": "Akola",
        "commodity": "Cotton"
    }
    r6 = client.post("/api/chat", json=chat_payload_mr)
    print(f"Status: {r6.status_code}")
    c6_data = r6.json()
    print(f"Language: {c6_data['language']} | Has RAG Context: {c6_data['has_rag_context']}")
    print(f"Sources Cited: {len(c6_data['sources'])}")
    for s in c6_data["sources"]:
        print(f"  * {s['document']} (Page {s['page']})")
    print("\nGenerated Advisory Preview:")
    print(c6_data["answer"][:300] + "...")
    assert r6.status_code == 200, "Chat endpoint failed"

    # Test 7: Multilingual Chatbot (Hindi Query on Soybean Yellowing)
    print("\n[Test 7] POST /api/chat (Hindi Query on Soybean Yellowing)")
    chat_payload_hi = {
        "query": "सोयाबीन की पत्तियां पीली क्यों पड़ रही हैं और इसका क्या उपचार है?",
        "language": "hi",
        "location": "Indore",
        "commodity": "Soybean"
    }
    r7 = client.post("/api/chat", json=chat_payload_hi)
    print(f"Status: {r7.status_code}")
    c7_data = r7.json()
    print(f"Language: {c7_data['language']} | Has RAG Context: {c7_data['has_rag_context']}")
    print(f"Sources Cited: {len(c7_data['sources'])}")
    print("\nGenerated Advisory Preview:")
    print(c7_data["answer"][:300] + "...")
    assert r7.status_code == 200, "Chat endpoint failed"

    print("\n" + "=" * 80)
    print("ALL 7 API TEST CASES PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_api_tests()
