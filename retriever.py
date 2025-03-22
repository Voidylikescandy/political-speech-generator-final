from database import insert_text_into_db, db
from serper_api import fetch_additional_results

def search_with_threshold(query, threshold=0.85, limit=5, recursion_depth=0, max_recursion=3):
    table = db.open_table("words")
    results_df = table.search(query).metric("cosine").limit(limit).to_pandas()
    results_df["similarity_score"] = 1 - results_df["_distance"]

    filtered_results = results_df[results_df["similarity_score"] >= threshold]
    print(f"Fetched {len(filtered_results)} results from DB")

    if len(filtered_results) < 2 and recursion_depth < max_recursion:
        print(f"Fetching more results (depth: {recursion_depth+1})")
        additional_results = fetch_additional_results(query, min_results=5)

        if additional_results:
            insert_text_into_db(additional_results)
            return search_with_threshold(query, threshold, limit, recursion_depth + 1, max_recursion)

    return "\n".join(filtered_results["text"]) if not filtered_results.empty else ""
