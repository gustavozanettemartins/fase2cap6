def validar_str(data: str) -> bool:
    return isinstance(data, str) and data.strip() != ""

def validar_int(data: str) -> bool:
    try:
        int(data)
        return True
    except (ValueError, TypeError):
        return False

def validar_float(data: str) -> bool:
    try:
        float(data)
        return True
    except (ValueError, TypeError):
        return False

def validar_bool(data: str) -> bool:
    if isinstance(data, bool):
        return True
    if isinstance(data, str):
        return data.lower() in ["true", "false", "sim", "não", "nao", "1", "0"]
    if isinstance(data, int):
        return data in [0, 1]
    return False