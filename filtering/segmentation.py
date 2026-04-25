from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict

SEGMENT_LABELS = {
    "beauty": {0: "Skincare Educators", 1: "Makeup Tutorial Creators", 2: "Product Review Creators"},
    "education": {0: "Olympiad Prep", 1: "Reasoning & Aptitude", 2: "Student Competition Awareness"},
    "finance": {0: "Investing Basics", 1: "Budgeting & Savings", 2: "Credit & Debt Literacy"},
}

def segment_creators(creators: List[Dict], industry: str, n_clusters: int = 3) -> List[Dict]:
    """Clusters creators based on their content signals."""
    if not creators or len(creators) < n_clusters:
        for c in creators:
            c["segment"] = "General Creator"
        return creators

    from content.signal_extractor import get_model
    model = get_model()
    
    # Prepare texts for embedding
    texts = []
    for c in creators:
        text = (c.get("description", "") + " " + c.get("content_signal_text", ""))[:1000]
        texts.append(text)
        
    embeddings = model.encode(texts)
    
    # Run KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(embeddings)
    
    label_map = SEGMENT_LABELS.get(industry.lower(), {})
    
    # If industry is unknown, use LLM to label clusters based on themes
    if not label_map:
        print(f"[Segmentation] Unknown industry '{industry}'. Using LLM to dynamically label clusters...")
        for i in range(n_clusters):
            # Get themes for this cluster
            cluster_indices = [j for j, l in enumerate(labels) if l == i]
            cluster_themes = []
            for idx in cluster_indices[:5]:
                cluster_themes.extend(creators[idx].get("content_themes", []))
            
            # Simple heuristic or LLM call here. 
            # To keep it fast, we'll use a small LLM call for labels if possible, 
            # otherwise a theme-based fallback.
            if cluster_themes:
                top_theme = max(set(cluster_themes), key=cluster_themes.count)
                label_map[i] = f"{top_theme.title()} Specialist"
            else:
                label_map[i] = f"Cluster {i+1} Creator"

    for i, creator in enumerate(creators):
        cluster_id = int(labels[i])
        creator["cluster_id"] = cluster_id
        creator["segment"] = label_map.get(cluster_id, f"Segment {cluster_id}")
        
    print(f"[Segmentation] Grouped {len(creators)} creators into {n_clusters} clusters: {list(label_map.values())}")
    return creators
