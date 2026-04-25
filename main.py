import json
import os
import sys

# Ensure terminal supports UTF-8 for emojis/special chars
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
from config_loader import load_config
from database import init_db, save_creators, save_outreach_log
from discovery.orchestrator import run_discovery
from filtering.filters import apply_filters
from enrichment.youtube_enrichment import enrich_youtube_creator
from content.content_pipeline import run_content_pipeline
from filtering.segmentation import segment_creators
from scoring.brand_fit_scorer import score_all_creators
from strategy.collaboration_strategy import assign_strategy
from outreach.message_generator import generate_outreach_messages
from outreach.email_sender import run_email_campaign
from models.creator_profile import CreatorProfile

def run_pipeline():
    # 0. Setup
    print("\n" + "="*50)
    print("MICRO-INFLUENCER DISCOVERY PIPELINE START")
    print("="*50 + "\n")
    
    config = load_config()
    brand = config.get("brand", {})
    keywords = config.get("keywords", [])
    
    init_db()
    
    # 1. Discovery
    raw_creators = run_discovery(config)
    if not raw_creators:
        print("[Pipeline] No creators discovered. Exiting.")
        return

    # 2. Filtering
    filtered_creators = apply_filters(raw_creators, keywords)
    
    # Cap to 20 creators to stay well within API quota limits (Production Optimization)
    filtered_creators = filtered_creators[:20]
    
    # 3. Enrichment (With Consistency Check)
    from discovery.youtube_discovery import get_youtube_service
    youtube = get_youtube_service()
    
    print(f"[Enrichment] Enriching {len(filtered_creators)} creators with Consistency Checks...")
    enriched_creators = [enrich_youtube_creator(c, youtube) for c in filtered_creators]
    
    # 4. Content Intelligence (Parallel Optimization)
    # Pre-load model to avoid race conditions in threads
    if enriched_creators:
        from content.signal_extractor import get_model
        get_model()
        
    analyzed_creators = run_content_pipeline(enriched_creators, brand.get("industry", "general"))
    
    # 5. Segmentation
    segmented_creators = segment_creators(analyzed_creators, brand.get("industry", "general"))
    
    # 6. Scoring
    brand["keywords"] = keywords # Pass keywords for scoring
    scored_creators = score_all_creators(segmented_creators, brand)
    
    # 7. Strategy Assignment
    final_creators = assign_strategy(scored_creators, brand.get("industry", "general"))
    
    # 8. Message Generation
    final_creators = generate_outreach_messages(final_creators, brand)
    
    # 9. Validation & Storage
    validated_profiles = []
    for c in final_creators:
        try:
            profile = CreatorProfile(**c)
            validated_profiles.append(profile.model_dump())
        except Exception as e:
            print(f"[Validation] Skipping {c.get('channel_title')}: {e}")
            
    save_creators(validated_profiles)
    
    # 10. Outreach Execution (Optional)
    if config.get("outreach", {}).get("send_emails"):
        email_results = run_email_campaign(validated_profiles, brand)
        save_outreach_log("email", email_results)
        print(f"[Pipeline] Email Campaign Results: {email_results}")

    # 11. Final Output
    output_dir = "output"
    output_path_json = f"{output_dir}/enriched_creators.json"
    output_path_csv = f"{output_dir}/enriched_creators.csv"
    output_path_top = f"{output_dir}/top_creators.json"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save JSON (Full List)
    with open(output_path_json, "w", encoding="utf-8") as f:
        json.dump(validated_profiles, f, indent=2)
        
    # Save JSON (Top 5 Shortlist)
    top_5 = validated_profiles[:5]
    with open(output_path_top, "w", encoding="utf-8") as f:
        json.dump(top_5, f, indent=2)
        
    # Save CSV
    import csv
    if validated_profiles:
        keys = validated_profiles[0].keys()
        with open(output_path_csv, "w", newline="", encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(validated_profiles)
        
    print("\n" + "="*50)
    print(f"PIPELINE COMPLETE: {len(validated_profiles)} creators processed.")
    print(f"Full data: {output_path_json}")
    print(f"Shortlist: {output_path_top}")
    print(f"CSV Report: {output_path_csv}")
    print(f"Database: creators.db")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_pipeline()
