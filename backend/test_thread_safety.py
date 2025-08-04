import requests
import time

print('🔍 Testing IMMEDIATELY After Restart...')
print('=' * 50)

# Login
login_data = {'username': 'admin', 'password': 'AdminPass123!'}
auth_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)

if auth_response.status_code == 200:
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test 1: First request (should work)
    print('1️⃣ First request...')
    start = time.time()
    try:
        response = requests.get('http://localhost:8000/api/v1/access/summary?compartment_id=default', headers=headers, timeout=15)
        elapsed = time.time() - start
        if response.status_code == 200:
            data = response.json()
            roles = data.get('rbac_summary', {}).get('total_roles', 0)
            print(f'   ✅ Success: {elapsed:.2f}s - Roles: {roles}')
        else:
            print(f'   ❌ Failed: Status {response.status_code}')
    except Exception as e:
        elapsed = time.time() - start
        print(f'   ❌ Failed: {elapsed:.2f}s - {e}')
    
    # Test 2: Second request immediately (likely to fail if thread-unsafe)
    print('2️⃣ Second request immediately...')
    start = time.time()
    try:
        response = requests.get('http://localhost:8000/api/v1/access/summary?compartment_id=default', headers=headers, timeout=15)
        elapsed = time.time() - start
        if response.status_code == 200:
            data = response.json()
            roles = data.get('rbac_summary', {}).get('total_roles', 0)
            print(f'   ✅ Success: {elapsed:.2f}s - Roles: {roles}')
        else:
            print(f'   ❌ Failed: Status {response.status_code}')
    except Exception as e:
        elapsed = time.time() - start
        print(f'   ❌ Failed: {elapsed:.2f}s - {e}')
        
    # Test 3: Third request (confirm pattern)
    print('3️⃣ Third request...')
    start = time.time()
    try:
        response = requests.get('http://localhost:8000/api/v1/access/summary?compartment_id=default', headers=headers, timeout=10)
        elapsed = time.time() - start
        if response.status_code == 200:
            data = response.json()
            roles = data.get('rbac_summary', {}).get('total_roles', 0)
            print(f'   ✅ Success: {elapsed:.2f}s - Roles: {roles}')
        else:
            print(f'   ❌ Failed: Status {response.status_code}')
    except Exception as e:
        elapsed = time.time() - start
        print(f'   ❌ Failed: {elapsed:.2f}s - {e}')
        
else:
    print('❌ Login failed')

print('\n🎯 If first works but others fail = Thread-safety issue!')
print('🎯 If all fail = Different issue!') 