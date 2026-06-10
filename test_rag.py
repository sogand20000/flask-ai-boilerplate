import os
import sys

from backend.src.services.rag_service import insert_document

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_test():
    print("⏳ Starting RAG testing pipeline...")

    sample_knowledge = (
        "سیاست جدید شرکت در سال ۲۰۲۶: ساعت کاری رسمی از شنبه تا چهارشنبه "
        "از ساعت ۹:۰۰ صبح الی ۱۷:۰۰ عصر است. کارمندان مجاز به استفاده از "
        "شناوری ۳۰ دقیقه‌ای در ورود هستند."
    )
    sample_metadata = {"source": "company_handbook_2026.txt", "category": "HR_Policy"}

    success = insert_document(content=sample_knowledge, metadata=sample_metadata)

    if success:
        print("🎉 Test completed successfully! Check your Supabase Table Editor.")
    else:
        print("❌ Test failed. Please check the logs above for errors.")


if __name__ == "__main__":
    run_test()
