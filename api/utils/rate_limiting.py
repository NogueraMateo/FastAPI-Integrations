from redis import Redis

def rate_limit_exceeded(redis_client: Redis, identifier: str, max_requests: int, period: int):
    key = f"rate_limit:{identifier}"
    current_requests = redis_client.get(key)

    if current_requests and int(current_requests) >= max_requests:
        return True
    else: 
        # Increment the request count and set the expiration if it's a new key
        pipe = redis_client.pipeline()
        pipe.incr(key, 1)
        if not current_requests:
            pipe.expire(key, period)
        pipe.execute()
        return False