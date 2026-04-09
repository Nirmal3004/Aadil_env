MIN_SCORE = 0.0001
MAX_SCORE = 0.9999


def normalize_task_score(score):
    try:
        score = float(score)
    except Exception:
        return MIN_SCORE

    if score <= 0.0:
        return MIN_SCORE
    if score >= 1.0:
        return MAX_SCORE

    # Round first, then clamp again so formatting can never produce 0.0 or 1.0.
    rounded = round(score, 4)
    if rounded <= 0.0:
        return MIN_SCORE
    if rounded >= 1.0:
        return MAX_SCORE
    return rounded


def self_check_normalize_task_score():
    return {
        0: normalize_task_score(0),
        1: normalize_task_score(1),
        0.5: normalize_task_score(0.5),
        -3: normalize_task_score(-3),
        7: normalize_task_score(7),
        0.00001: normalize_task_score(0.00001),
        0.99996: normalize_task_score(0.99996),
    }
