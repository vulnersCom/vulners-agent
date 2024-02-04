def remove_non_ascii(s):
    return "".join(char for char in s if ord(char) < 128).strip()
