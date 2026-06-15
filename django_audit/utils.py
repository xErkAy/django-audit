def dict_diff(old: dict, new: dict) -> dict:
    diff = {}
    all_keys = set(old.keys()) | set(new.keys())
    for key in all_keys:
        old_value = old.get(key)
        new_value = new.get(key)
        if old_value != new_value:
            diff[key] = {"old_value": old_value, "new_value": new_value}
    return diff
