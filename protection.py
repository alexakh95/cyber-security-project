from datetime import datetime, timedelta


# Configuration for rate-limit 
MAX_TOKENS = 10       # Bucket capacity (Burst)
REFILL_RATE = 1       # Tokens added per minute
bucket_storage = {}   # In-memory storage: { ip: {"tokens": 10, "last_updated": datetime} }


def check_rate_limit(ip):
    now = datetime.utcnow()
    
    # Initialize bucket for new IPs
    if ip not in bucket_storage:
        bucket_storage[ip] = {"tokens": MAX_TOKENS, "last_updated": now}

    record = bucket_storage[ip]
    
    # 1. REFILL LOGIC
    # Calculate how much time passed and add tokens accordingly
    time_passed = (now - record["last_updated"]).total_seconds()
    new_tokens = time_passed * (REFILL_RATE / 60.0) # Convert rate to per-second
    
    record["tokens"] = min(MAX_TOKENS, record["tokens"] + new_tokens)
    record["last_updated"] = now

    # 2. CONSUMPTION LOGIC
    if record["tokens"] >= 1:
        record["tokens"] -= 1
        return True  # Access granted
    else:
        return False # Rate limited