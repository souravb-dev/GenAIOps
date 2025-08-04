import requests
import json
import traceback

print('🔍 Debug Summary Endpoint...')

# Get token
login_data = {
    'username': 'admin',
    'password': 'AdminPass123!'
}

try:
    auth_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
    if auth_response.status_code == 200:
        token = auth_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test summary endpoint with detailed error info
        print('Testing summary endpoint...')
        summary_response = requests.get(
            'http://localhost:8000/api/v1/access/summary?compartment_id=test_compartment', 
            headers=headers, 
            timeout=30
        )
        
        print(f'Status: {summary_response.status_code}')
        print(f'Response Headers: {dict(summary_response.headers)}')
        print(f'Response Text: {summary_response.text}')
        
        if summary_response.status_code == 200:
            print('✅ Summary endpoint working!')
            print('Response:', json.dumps(summary_response.json(), indent=2))
        else:
            print(f'❌ Summary endpoint failed: {summary_response.status_code}')
            try:
                error_detail = summary_response.json()
                print('Error details:', json.dumps(error_detail, indent=2))
            except:
                print('Raw error response:', summary_response.text)
    else:
        print(f'Auth failed: {auth_response.text}')
        
except Exception as e:
    print(f'❌ Request failed: {e}')
    traceback.print_exc() 