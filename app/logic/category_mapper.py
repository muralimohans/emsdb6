def map_score_to_category(score: int) -> str:
    """
    Map a numeric email validation score (0-100) to one of 4 categories:
    Valid, Risky, Possibly Invalid, Invalid
    """
    if score >= 90:
        return "valid"
    elif score >= 70:
        return "risky"
    elif score >= 50:
        return "possibly_invalid"
    else:
        return "invalid"
