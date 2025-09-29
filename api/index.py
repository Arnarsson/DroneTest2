def handler(request, context):
    """
    Minimal Vercel Python function handler
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': {
            'message': 'DroneWatch API is working!',
            'status': 'operational',
            'path': request.get('path', '/'),
            'method': request.get('method', 'GET')
        }
    }