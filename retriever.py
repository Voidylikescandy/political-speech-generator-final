from database import insert_text_into_db, db
from serper_api import fetch_additional_results
from logger import logger

def search_with_threshold(table, query, threshold=0.85, metric="cosine", limit=5, recursion_depth=0, max_recursion=3):
    """
    Searches for the query in the LanceDB table and filters results based on a similarity threshold.
    If filtered results are fewer than 2, it fetches additional results using the Serper API.
    
    Parameters:
    - table: The LanceDB table instance.
    - query: The search query (string).
    - threshold: The minimum similarity score required.
    - metric: The distance metric (default is "cosine").
    - limit: The maximum number of results to retrieve before filtering.
    - recursion_depth: Current recursion depth (used internally).
    - max_recursion: Maximum number of times to recurse to prevent infinite loops.
    
    Returns:
    - A single string containing the combined text of all filtered results.
    """
    logger.info(f"Searching for query: '{query}' with threshold {threshold}")
    results_df = table.search(query).metric(metric).limit(limit).to_pandas()
    
    if metric == "cosine":
        results_df["similarity_score"] = 1 - results_df["_distance"]  # Cosine similarity
    elif metric == "l2":
        results_df["similarity_score"] = 1 / (1 + results_df["_distance"])  # Normalize L2
    elif metric == "dot":
        results_df["similarity_score"] = results_df["_distance"]  # Dot product already represents similarity
    elif metric == "ip":
        results_df["similarity_score"] = -results_df["_distance"]  # Invert inner product for similarity
    
    # Filter based on threshold
    filtered_results = results_df[results_df["similarity_score"] >= threshold]
    # print(f"Fetched {len(filtered_results)} results from database that meet the threshold")
    logger.info(f"Fetched {len(filtered_results)} results from database that meet the threshold")

    # If we don't have enough results and haven't exceeded max recursion
    if len(filtered_results) < 2 and recursion_depth < max_recursion:
        # print(f"Invoking Serper API (recursion depth: {recursion_depth+1}/{max_recursion})")
        logger.info(f"Invoking Serper API (recursion depth: {recursion_depth+1}/{max_recursion})")    
        additional_results = fetch_additional_results(query, min_results=5)
        
        # Only proceed if we actually got new results
        if additional_results:
            logger.info(f"Adding {len(additional_results)} new sources to the database")
            # print(f"Adding {len(additional_results)} new sources to the database")
            insert_text_into_db(additional_results)
            
            # Recursively search again with incremented recursion depth
            return search_with_threshold(
                table, query, threshold=threshold, metric=metric, 
                limit=limit, recursion_depth=recursion_depth+1, max_recursion=max_recursion
            )
        else:
            logger.warning("No new sources found. Using current results.")
            # print("No new sources found. Using current results.")
            pass
    
    # If we still don't have enough results after recursion or API calls,
    # we'll just return what we have
    if len(filtered_results) == 0:
        logger.info("No results meet the similarity threshold.")
        return ""
    
    logger.info(f"Returning {len(filtered_results)} filtered results")
    return "\n".join(filtered_results["text"])