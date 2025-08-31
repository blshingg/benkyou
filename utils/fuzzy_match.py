
def fuzzy_match(query, target):
    query = query.lower()
    target = target.lower()
    
    if not query:
        return True # Empty query matches everything

    query_idx = 0
    for char in target:
        if query_idx < len(query) and char == query[query_idx]:
            query_idx += 1
    
    return query_idx == len(query)
