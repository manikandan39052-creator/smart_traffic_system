from collections import Counter
from anpr.plate_validator import normalize_plate
def vote_plate(results: list[tuple[str,float]]) -> tuple[str | None,float]:
    cleaned=[(normalize_plate(x),c) for x,c in results if normalize_plate(x)]
    if not cleaned: return None,0.0
    winner=Counter(x for x,_ in cleaned).most_common(1)[0][0]; scores=[c for x,c in cleaned if x==winner]; return winner,sum(scores)/len(scores)
