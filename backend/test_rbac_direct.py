import requests
import json

print('🧪 Testing RBAC endpoint directly...')

# Get token
login_data = {
    'username': 'admin',
    'password': 'admin123'
}

try:
    auth_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)
    if auth_response.status_code == 200:
        token = auth_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test just the RBAC endpoint
        print('Testing RBAC endpoint...')
        rbac_response = requests.get('http://localhost:8000/api/v1/access/rbac', headers=headers, timeout=15)
        print(f'Status: {rbac_response.status_code}')
        if rbac_response.status_code != 200:
            print(f'Error response: {rbac_response.text}')
        else:
            data = rbac_response.json()
            print(f'✅ RBAC endpoint working! Got data: {data}')
    else:
        print(f'Auth failed: {auth_response.text}')
        
except Exception as e:
    print(f'❌ Request failed: {e}')
    import traceback
    traceback.print_exc() 