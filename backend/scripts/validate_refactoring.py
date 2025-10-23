#!/usr/bin/env python3
"""
Validation script for Phase 1 refactoring
Checks that the Message model has been properly replaced with CommunicationLog
"""
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_imports():
    """Check for any remaining Message imports in critical files"""
    print("🔍 Checking for deprecated Message model imports...")
    
    critical_paths = [
        "app/tasks/email_sync_task.py",
        "app/services/communication_service.py",
        "app/services/task_service.py",
        "app/routers/emails.py",
        "app/workers/social_sync.py",
        "app/workers/embedding_generator.py",
        "app/security/audit.py",
    ]
    
    issues = []
    for path in critical_paths:
        full_path = Path(__file__).parent.parent / path
        if full_path.exists():
            with open(full_path, 'r') as f:
                content = f.read()
                if 'from ..models.message import Message' in content or 'from app.models.message import Message' in content:
                    issues.append(f"  ❌ {path} still imports Message model")
        else:
            print(f"  ⚠️  {path} not found (may have been deleted)")
    
    if issues:
        print("\n".join(issues))
        return False
    else:
        print("  ✅ No Message imports found in critical files")
        return True


def check_models():
    """Verify Message model is deleted and CommunicationLog exists"""
    print("\n🔍 Checking model files...")
    
    message_path = Path(__file__).parent.parent / "app/models/message.py"
    comm_log_path = Path(__file__).parent.parent / "app/models/communication_log.py"
    
    if message_path.exists():
        print("  ❌ Message model still exists at app/models/message.py")
        return False
    else:
        print("  ✅ Message model successfully deleted")
    
    if comm_log_path.exists():
        print("  ✅ CommunicationLog model exists")
        return True
    else:
        print("  ❌ CommunicationLog model not found")
        return False


def check_migration():
    """Check migration file exists"""
    print("\n🔍 Checking migration file...")
    
    migration_path = Path(__file__).parent.parent / "alembic/versions/004_drop_messages_clean_slate.py"
    
    if migration_path.exists():
        print("  ✅ Migration 004_drop_messages_clean_slate.py exists")
        
        with open(migration_path, 'r') as f:
            content = f.read()
            if 'op.drop_table(\'messages\')' in content:
                print("  ✅ Migration drops messages table")
                return True
            else:
                print("  ❌ Migration does not drop messages table")
                return False
    else:
        print("  ❌ Migration file not found")
        return False


def test_imports():
    """Try importing key modules to check for import errors"""
    print("\n🔍 Testing module imports...")
    
    try:
        from app.models.communication_log import CommunicationLog, CommunicationType
        print("  ✅ CommunicationLog imports successfully")
    except Exception as e:
        print(f"  ❌ Failed to import CommunicationLog: {e}")
        return False
    
    try:
        from app.services.contact_service import ContactService
        print("  ✅ ContactService imports successfully")
    except Exception as e:
        print(f"  ❌ Failed to import ContactService: {e}")
        return False
    
    try:
        from app.tasks.email_sync_task import sync_gmail_account
        print("  ✅ Email sync tasks import successfully")
    except Exception as e:
        print(f"  ❌ Failed to import email sync tasks: {e}")
        return False
    
    return True


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("Phase 1 Refactoring Validation")
    print("=" * 60)
    
    results = []
    
    results.append(("Import Check", check_imports()))
    results.append(("Model Check", check_models()))
    results.append(("Migration Check", check_migration()))
    results.append(("Module Import Test", test_imports()))
    
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All validation checks passed!")
        print("\nNext steps:")
        print("1. Run migration: cd backend && alembic upgrade head")
        print("2. Start backend: cd backend && python -m app.main")
        print("3. Test email sync with a Gmail account")
        print("4. Verify timeline displays in frontend")
        return 0
    else:
        print("\n⚠️  Some validation checks failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

