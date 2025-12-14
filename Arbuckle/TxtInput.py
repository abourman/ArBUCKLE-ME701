def parse_value(v: str):
    """Convert string values from input file to Python types."""
    v = v.strip()

    # None Types
    if v.lower() == "none":
        return None 

    # Booleans
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False

    # Numbers (int or float)
    try:
        if "." in v or "e" in v.lower():
            return float(v)
        return int(v)
    except ValueError:
        pass

    # Otherwise return string
    return v


def load_config(filename="config.txt"):
    config = {}

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()

            # Skip blank lines or comments
            if not line or line.startswith("#"):
                continue

            # Expect "key = value"
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = parse_value(value)

            config[key] = value

    return config


# Example usage
if __name__ == "__main__":
    import sys
    try:
        filename = sys.argv[1]
    except:
        print("No Input File Given")
        print("Use: python Input.py input.txt")  
        sys.exit()  
    
    cfg = load_config(filename)
    print("Loaded configuration:")
    for k, v in cfg.items():
        print(f"{k} : {v}")
