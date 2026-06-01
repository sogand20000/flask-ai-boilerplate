import requests

url = "http://127.0.0.1:5001/api/chat"

# Using requests.Session to maintain cookies and session memory across requests
with requests.Session() as session:
    # --- FIRST MESSAGE: Introduction ---
    payload1 = {"message": "Hello, my name is Somayeh and I have a Flask project."}

    # FIXED: Changed from requests.post to session.post to correctly track the session cookie
    r1 = session.post(url, json=payload1)

    print(f"Status Code 1: {r1.status_code}")
    if r1.status_code == 200:
        res_data1 = r1.json()
        print("Response 1:\n", res_data1["data"]["response"])
    else:
        print("Raw Error 1:\n", r1.text)

    print("-" * 50)

    # --- SECOND MESSAGE: Testing context retention (Session Memory) ---
    payload2 = {"message": "My project execution team consists of 4 people."}
    r2 = session.post(url, json=payload2)

    print(f"Status Code 2: {r2.status_code}")
    if r2.status_code == 200:
        res_data2 = r2.json()
        print("Response 2:\n", res_data2["data"]["response"])
    else:
        print("Raw Error 2:\n", r2.text)
