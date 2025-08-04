#!/usr/bin/env python3
"""
Direct kubeconfig test to diagnose authentication issues
"""

import os
import tempfile
import yaml
from kubernetes import client, config
from kubernetes.config import ConfigException

KUBECONFIG_PATH = r"C:\Users\2375603\.kube\config"

def read_and_analyze_kubeconfig():
    """Read and analyze the kubeconfig to understand authentication method"""
    print("📋 ANALYZING KUBECONFIG")
    print("=" * 50)
    
    try:
        with open(KUBECONFIG_PATH, 'r') as f:
            kubeconfig_data = yaml.safe_load(f)
        
        print(f"✅ Kubeconfig loaded successfully")
        
        # Analyze users and authentication methods
        users = kubeconfig_data.get('users', [])
        for user in users:
            user_name = user.get('name')
            user_config = user.get('user', {})
            
            print(f"\n👤 User: {user_name}")
            
            if 'exec' in user_config:
                exec_config = user_config['exec']
                print(f"   🔧 Auth Method: exec")
                print(f"   📋 Command: {exec_config.get('command', 'Unknown')}")
                print(f"   📝 Args: {exec_config.get('args', [])}")
                print(f"   🌍 Env: {len(exec_config.get('env', []))} variables")
            elif 'token' in user_config:
                print(f"   🔑 Auth Method: static token")
            elif 'client-certificate' in user_config:
                print(f"   📜 Auth Method: client certificate")
            else:
                print(f"   ❓ Auth Method: unknown")
                print(f"   📋 Available keys: {list(user_config.keys())}")
        
        return kubeconfig_data
        
    except Exception as e:
        print(f"❌ Failed to analyze kubeconfig: {e}")
        return None

def test_direct_kubectl_python():
    """Test direct connection using Python kubernetes client"""
    print("\n🐍 TESTING PYTHON KUBERNETES CLIENT")
    print("=" * 50)
    
    try:
        # Load kubeconfig from default location
        config.load_kube_config(config_file=KUBECONFIG_PATH)
        print("✅ Kubeconfig loaded into Python client")
        
        # Create API client
        v1 = client.CoreV1Api()
        print("✅ CoreV1Api client created")
        
        # Test simple call
        print("🔍 Testing API call...")
        nodes = v1.list_node(timeout_seconds=10)
        print(f"✅ Successfully retrieved {len(nodes.items)} nodes!")
        
        for node in nodes.items:
            print(f"   📦 Node: {node.metadata.name}")
            print(f"      Status: {node.status.conditions[-1].type if node.status.conditions else 'Unknown'}")
            print(f"      Version: {node.status.node_info.kubelet_version}")
        
        return True
        
    except ConfigException as e:
        print(f"❌ Kubeconfig error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_with_temp_file():
    """Test using temporary file approach (like our service does)"""
    print("\n📁 TESTING TEMP FILE APPROACH")
    print("=" * 50)
    
    try:
        # Read kubeconfig content
        with open(KUBECONFIG_PATH, 'r') as f:
            kubeconfig_content = f.read()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(kubeconfig_content)
            temp_path = f.name
        
        print(f"📝 Created temp kubeconfig: {temp_path}")
        
        # Load from temp file
        config.load_kube_config(config_file=temp_path)
        print("✅ Loaded kubeconfig from temp file")
        
        # Test API call
        v1 = client.CoreV1Api()
        nodes = v1.list_node(timeout_seconds=10)
        print(f"✅ Successfully retrieved {len(nodes.items)} nodes via temp file!")
        
        # Cleanup
        os.unlink(temp_path)
        print("🧹 Cleaned up temp file")
        
        return True
        
    except Exception as e:
        print(f"❌ Temp file approach failed: {e}")
        # Cleanup on error
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        return False

def test_environment_variables():
    """Check if there are any required environment variables"""
    print("\n🌍 CHECKING ENVIRONMENT VARIABLES")
    print("=" * 50)
    
    oci_vars = [
        'OCI_CLI_CONFIG_FILE',
        'OCI_CLI_PROFILE', 
        'OCI_CONFIG_FILE',
        'OCI_CLI_AUTH'
    ]
    
    for var in oci_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    # Check if OCI CLI is available
    try:
        import subprocess
        result = subprocess.run(['oci', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ OCI CLI available: {result.stdout.strip()}")
        else:
            print(f"❌ OCI CLI error: {result.stderr}")
    except Exception as e:
        print(f"❌ OCI CLI check failed: {e}")

def main():
    print("🔍 KUBERNETES AUTHENTICATION DIAGNOSIS")
    print("=" * 60)
    
    # Step 1: Analyze kubeconfig
    kubeconfig_data = read_and_analyze_kubeconfig()
    if not kubeconfig_data:
        return
    
    # Step 2: Check environment
    test_environment_variables()
    
    # Step 3: Test direct Python client
    direct_success = test_direct_kubectl_python()
    
    # Step 4: Test temp file approach
    temp_success = test_with_temp_file()
    
    print(f"\n📊 DIAGNOSIS SUMMARY")
    print("=" * 60)
    print(f"Direct Python client: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print(f"Temp file approach:   {'✅ SUCCESS' if temp_success else '❌ FAILED'}")
    
    if direct_success and temp_success:
        print("\n🎉 Both approaches work! The issue might be in our service implementation.")
    elif direct_success and not temp_success:
        print("\n💡 Direct works but temp file fails. Issue with temp file handling.")
    elif not direct_success and not temp_success:
        print("\n🔧 Both fail. Likely authentication method compatibility issue.")
        print("   Recommendation: Check if exec-based auth is properly configured.")

if __name__ == "__main__":
    main() 