## RAG Knowledge Integration Test

To test the smart chunking pipeline and Supabase document insertion with international standards, run the following `curl` command:

```bash
curl -X 'POST' \
  'http://localhost:5177/api/knowledge/add' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @tests/data/test_knowledge_payload.json