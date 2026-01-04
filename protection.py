from datetime import datetime, timedelta


# Configuration for rate-limit 
MAX_TOKENS = 10       # Bucket capacity (Burst)
REFILL_RATE = 1       # Tokens added per minute
bucket_storage = {}   # In-memory storage: { ip: {"tokens": 10, "last_updated": datetime} }


def check_rate_limit(user):
    now = datetime.utcnow()
    
    # Initialize bucket for new IPs
    if user not in bucket_storage:
        bucket_storage[user] = {"tokens": MAX_TOKENS, "last_updated": now}

    record = bucket_storage[user]
    
    # Calculate how much time passed and add tokens accordingly
    time_passed = (now - record["last_updated"]).total_seconds()
    new_tokens = time_passed * (REFILL_RATE / 60.0) # Convert rate to per-second
    
    record["tokens"] = min(MAX_TOKENS, record["tokens"] + new_tokens)
    record["last_updated"] = now

   
    if record["tokens"] >= 1:
        record["tokens"] -= 1
        return True  # Access granted
    else:
        return False # Rate limited
    

    