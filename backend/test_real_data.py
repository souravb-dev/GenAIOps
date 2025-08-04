#!/usr/bin/env python3
import requests
import json

print('🧪 Testing Access Analyzer with Real Data...')
print('=' * 50)

# Login
login_data = {'username': 'admin', 'password': 'AdminPass123!'}
auth_response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data)

if auth_response.status_code == 200:
    token = auth_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test RBAC endpoint
    print('🔍 Testing RBAC Analysis...')
    rbac_response = requests.get('http://localhost:8000/api/v1/access/rbac', headers=headers)
    print(f'RBAC Status: {rbac_response.status_code}')
    
    if rbac_response.status_code == 200:
        rbac_data = rbac_response.json()
        print('✅ RBAC Success!')
        print(f'   Roles: {len(rbac_data.get("roles", []))}')
        print(f'   Bindings: {len(rbac_data.get("bindings", []))}')
        print(f'   Cluster: {rbac_data.get("cluster_name", "Unknown")}')
        
        # Show sample role names
        roles = rbac_data.get('roles', [])[:5]
        if roles:
            print('   Sample Roles:')
            for role in roles:
                print(f'     - {role.get("name", "unknown")} ({role.get("kind", "unknown")})')
    else:
        print(f'❌ RBAC Failed: {rbac_response.text[:200]}')
    
    # Test Summary endpoint
    print('\n🔍 Testing Summary...')
    summary_response = requests.get('http://localhost:8000/api/v1/access/summary?compartment_id=test', headers=headers)
    print(f'Summary Status: {summary_response.status_code}')
    
    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        print('✅ Summary Success!')
        print(f'   Cluster: {summary_data.get("cluster_name", "Unknown")}')
        rbac_summary = summary_data.get('rbac_summary', {})
        print(f'   Total Roles: {rbac_summary.get("total_roles", 0)}')
        print(f'   Total Bindings: {rbac_summary.get("total_bindings", 0)}')
        print(f'   High Risk Roles: {rbac_summary.get("high_risk_roles", 0)}')
        print(f'   Overall Risk Score: {summary_data.get("overall_risk_score", 0)}/100')
    else:
        print(f'❌ Summary Failed: {summary_response.text[:200]}')
        
else:
    print(f'❌ Login failed: {auth_response.text}')

print('\n🎯 Next Step: Test the frontend at http://localhost:3000')
print('   Navigate to Access Analyzer tab to see your real cluster data!') 