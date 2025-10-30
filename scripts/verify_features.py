#!/usr/bin/env python3
"""
Simple verification script for new features.
This script performs basic checks without requiring full package installation.
"""

import sys
import ast
import json
from pathlib import Path


def check_file_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def check_api_endpoints():
    """Check if all required API endpoints are defined"""
    api_file = Path("src/api/main.py")
    
    if not api_file.exists():
        return False, "API file not found"
    
    required_endpoints = [
        "/api/network/discover",
        "/api/train/upload_dataset",
        "/api/train/start",
        "/api/train/history",
        "/api/model/activate"
    ]
    
    with open(api_file, 'r') as f:
        content = f.read()
    
    missing = []
    for endpoint in required_endpoints:
        if endpoint not in content:
            missing.append(endpoint)
    
    if missing:
        return False, f"Missing endpoints: {', '.join(missing)}"
    
    return True, f"All {len(required_endpoints)} required endpoints found"


def check_dashboard_routing():
    """Check if dashboard has routing support"""
    dashboard_file = Path("src/dashboard/main.py")
    
    if not dashboard_file.exists():
        return False, "Dashboard file not found"
    
    with open(dashboard_file, 'r') as f:
        content = f.read()
    
    required_elements = [
        "dcc.Location",
        "display_page",
        "/admin",
        "create_admin_layout"
    ]
    
    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)
    
    if missing:
        return False, f"Missing routing elements: {', '.join(missing)}"
    
    return True, "Dashboard routing configured"


def check_admin_page():
    """Check if admin page exists and has required components"""
    admin_file = Path("src/dashboard/admin_page.py")
    
    if not admin_file.exists():
        return False, "Admin page file not found"
    
    with open(admin_file, 'r') as f:
        content = f.read()
    
    required_components = [
        "upload-dataset",
        "model-type-select",
        "btn-start-training",
        "training-history-list",
        "current-model-info"
    ]
    
    missing = []
    for component in required_components:
        if component not in content:
            missing.append(component)
    
    if missing:
        return False, f"Missing components: {', '.join(missing)}"
    
    return True, f"All {len(required_components)} required components found"


def check_network_discovery_ui():
    """Check if network discovery UI is added to dashboard"""
    dashboard_file = Path("src/dashboard/main.py")
    
    with open(dashboard_file, 'r') as f:
        content = f.read()
    
    required_elements = [
        "Live Network Discovery",
        "btn-network-scan",
        "network-scan-results"
    ]
    
    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)
    
    if missing:
        return False, f"Missing UI elements: {', '.join(missing)}"
    
    return True, "Network discovery UI components found"


def check_documentation():
    """Check if documentation file exists"""
    doc_file = Path("docs/LOCAL_TESTING_GUIDE.md")
    
    if not doc_file.exists():
        return False, "LOCAL_TESTING_GUIDE.md not found"
    
    with open(doc_file, 'r') as f:
        content = f.read()
    
    required_sections = [
        "Step 1: Clone the Repository",
        "Step 2: Check Out the Feature Branch",
        "Step 3: Set Up the Python Virtual Environment",
        "Step 6: Create Required Directories",
        "Step 7: Run the Application",
        "Step 8: View the New Features"
    ]
    
    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)
    
    if missing:
        return False, f"Missing documentation sections: {', '.join(missing)}"
    
    return True, "Documentation complete with all required sections"


def check_tests():
    """Check if tests exist for new features"""
    test_file = Path("tests/test_new_features.py")
    
    if not test_file.exists():
        return False, "Test file not found"
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    required_tests = [
        "TestNetworkDiscovery",
        "TestModelTraining",
        "test_network_discover_endpoint",
        "test_upload_dataset",
        "test_start_training",
        "test_activate_model"
    ]
    
    missing = []
    for test in required_tests:
        if test not in content:
            missing.append(test)
    
    if missing:
        return False, f"Missing tests: {', '.join(missing)}"
    
    return True, f"All {len(required_tests)} required tests found"


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("Project Argus - Feature Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("API File Syntax", lambda: check_file_syntax("src/api/main.py")),
        ("Dashboard File Syntax", lambda: check_file_syntax("src/dashboard/main.py")),
        ("Admin Page File Syntax", lambda: check_file_syntax("src/dashboard/admin_page.py")),
        ("Test File Syntax", lambda: check_file_syntax("tests/test_new_features.py")),
        ("API Endpoints", check_api_endpoints),
        ("Dashboard Routing", check_dashboard_routing),
        ("Admin Page Components", check_admin_page),
        ("Network Discovery UI", check_network_discovery_ui),
        ("Documentation", check_documentation),
        ("Test Coverage", check_tests),
    ]
    
    results = []
    for name, check_func in checks:
        success, message = check_func()
        results.append((name, success, message))
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
        print(f"     {message}")
        print()
    
    print("=" * 60)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✅ All verification checks passed!")
        print("The implementation is ready for testing.")
        return 0
    else:
        print("\n❌ Some verification checks failed.")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
