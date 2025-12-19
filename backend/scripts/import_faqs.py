import json
import os
import django
import sys

# Setup Django
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'astrotamil_api.settings')
django.setup()

from faq.models import FAQ


def import_faqs_from_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        faqs_data = json.load(f)
    
    imported_count = 0
    for faq_data in faqs_data:
        # Convert comma-separated keywords to list if needed
        keywords_raw = faq_data.get('keywords', '')
        if isinstance(keywords_raw, str):
            keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()]
        elif isinstance(keywords_raw, list):
            keywords = keywords_raw
        else:
            keywords = []
        
        # Create or update FAQ
        faq, created = FAQ.objects.update_or_create(
            question=faq_data['question'],
            defaults={
                'answer': faq_data.get('answer', ''),
                'keywords': keywords,
                'category': faq_data.get('category', '')
            }
        )
        
        if created:
            imported_count += 1
    
    print(f"Imported {imported_count} FAQs from {len(faqs_data)} records")
    print(f"Total FAQs in database: {FAQ.objects.count()}")


if __name__ == '__main__':
    # Adjust the path to your JSON file
    json_file = 'astrologer_faqs_complete.json'
    import_faqs_from_json(json_file)
