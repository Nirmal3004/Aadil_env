def normalize_task_score(score):
    try:
        score = float(score)
    except Exception:
        return 0.01

    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return round(score, 4)


def self_check_normalize_task_score():
    return {
        0: normalize_task_score(0),
        1: normalize_task_score(1),
        0.5: normalize_task_score(0.5),
        -3: normalize_task_score(-3),
        7: normalize_task_score(7),
    }
