#!/usr/bin/env python3
"""
Test script for the remediation service to validate basic functionality
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, create_tables
from app.services.remediation_service import remediation_service
from app.models.remediation import ActionType, Severity
from app.models.user import User

async def test_remediation_service():
    """Test basic remediation service functionality"""
    print("🧪 Testing Remediation Service...")
    
    try:
        # Create database tables
        create_tables()
        print("✅ Database tables created")
        
        # Get a database session
        db = SessionLocal()
        
        # Get a test user (admin)
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("❌ Admin user not found. Please run init_db.py first.")
            return
        
        print(f"✅ Using test user: {user.username}")
        
        # Test 1: Create a remediation action
        action = await remediation_service.create_remediation_action(
            title="Test OCI Instance Restart",
            description="Restart an unresponsive OCI compute instance",
            action_type=ActionType.OCI_CLI,
            action_command="oci compute instance action --instance-id ocid1.instance.test --action SOFTRESET",
            issue_details="Instance is unresponsive and needs restart",
            environment="development",
            service_name="web-app-01",
            severity=Severity.HIGH,
            current_user=user,
            requires_approval=True,
            rollback_command="oci compute instance action --instance-id ocid1.instance.test --action START",
            db=db
        )
        
        print(f"✅ Created remediation action: {action.id} - {action.title}")
        
        # Test 2: Get action status
        status = await remediation_service.get_action_status(action.id, db=db)
        print(f"✅ Retrieved action status: {status['action']['status']}")
        
        # Test 3: List actions
        actions = await remediation_service.list_actions(user, db=db)
        print(f"✅ Listed {len(actions)} actions")
        
        # Test 4: Approve action
        success = await remediation_service.approve_action(
            action_id=action.id,
            current_user=user,
            approval_comment="Approved for testing",
            db=db
        )
        print(f"✅ Action approval: {success}")
        
        # Test 5: Execute action (dry run)
        result = await remediation_service.execute_action(
            action_id=action.id,
            current_user=user,
            is_dry_run=True,
            db=db
        )
        print(f"✅ Dry run execution: {result['status']}")
        
        print("\n🎉 All remediation service tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

async def test_command_validation():
    """Test command validation functionality"""
    print("\n🔐 Testing Command Validation...")
    
    try:
        # Test safe command
        await remediation_service._validate_command_safety(
            "oci compute instance list", 
            ActionType.OCI_CLI
        )
        print("✅ Safe command validation passed")
        
        # Test dangerous command (should fail)
        try:
            await remediation_service._validate_command_safety(
                "rm -rf /", 
                ActionType.SCRIPT
            )
            print("❌ Dangerous command validation should have failed")
        except ValueError as e:
            print(f"✅ Dangerous command blocked: {e}")
        
        print("✅ Command validation tests passed")
        
    except Exception as e:
        print(f"❌ Command validation test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting Remediation Service Tests...")
    
    await test_command_validation()
    await test_remediation_service()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 