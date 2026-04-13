from rapidfuzz import fuzz

def match_columns(cols1, cols2):
    mapping = {}

    for c1 in cols1:
        best_match = None
        best_score = 0

        for c2 in cols2:
            score = fuzz.ratio(c1.lower(), c2.lower())

            if score > best_score:
                best_score = score
                best_match = c2

        if best_score > 50:
            mapping[c1] = {
                "match": best_match,
                "confidence": best_score
            }

    return mapping