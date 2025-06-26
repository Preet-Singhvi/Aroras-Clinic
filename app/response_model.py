def success_response(data, message="Success", status_code=200):
    """Standard success response format"""
    return {
        "status": "success",
        "code": status_code,
        "message": message,
        "data": data
    }, status_code

def error_response(message, status_code=400, errors=None):
    """Standard error response format"""
    response = {
        "status": "error",
        "code": status_code,
        "message": message
    }
    if errors:
        response["errors"] = errors
    return response, status_code