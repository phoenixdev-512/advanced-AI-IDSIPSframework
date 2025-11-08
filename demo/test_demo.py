#!/usr/bin/env python3
"""
Test script to validate the demo webpage.
"""

import os
from pathlib import Path

def test_demo_structure():
    """Test that all demo files exist"""
    demo_dir = Path(__file__).parent
    
    # Check main files
    assert (demo_dir / "index.html").exists(), "index.html missing"
    assert (demo_dir / "serve.py").exists(), "serve.py missing"
    assert (demo_dir / "README.md").exists(), "README.md missing"
    
    # Check screenshots
    screenshots_dir = demo_dir / "screenshots"
    assert screenshots_dir.exists(), "screenshots directory missing"
    
    required_screenshots = [
        "main-dashboard.png",
        "admin-model-training.png",
        "network-discovery.png",
        "device-details.png",
        "alerts-incidents.png"
    ]
    
    for screenshot in required_screenshots:
        screenshot_path = screenshots_dir / screenshot
        assert screenshot_path.exists(), f"Screenshot {screenshot} missing"
        assert screenshot_path.stat().st_size > 0, f"Screenshot {screenshot} is empty"
    
    # Check assets
    assets_dir = demo_dir / "assets"
    assert assets_dir.exists(), "assets directory missing"
    
    print("✅ All demo files present and valid!")
    return True

def test_html_content():
    """Test that HTML contains expected content"""
    demo_dir = Path(__file__).parent
    html_content = (demo_dir / "index.html").read_text()
    
    # Check for key sections
    assert "Project Argus" in html_content, "Missing project title"
    assert "Dashboard Screenshots" in html_content, "Missing screenshots section"
    assert "Key Features" in html_content, "Missing features section"
    assert "Quick Start" in html_content, "Missing quick start section"
    assert "Technology Stack" in html_content, "Missing tech stack section"
    
    # Check for all screenshots
    assert "main-dashboard.png" in html_content, "Missing main dashboard reference"
    assert "admin-model-training.png" in html_content, "Missing admin page reference"
    assert "network-discovery.png" in html_content, "Missing network discovery reference"
    assert "device-details.png" in html_content, "Missing device details reference"
    assert "alerts-incidents.png" in html_content, "Missing alerts reference"
    
    print("✅ HTML content validated!")
    return True

if __name__ == "__main__":
    print("🧪 Testing Project Argus Demo...")
    print("=" * 50)
    
    try:
        test_demo_structure()
        test_html_content()
        print("=" * 50)
        print("✅ All tests passed!")
        print("\n📝 Demo is ready to use!")
        print("   Run: python3 serve.py")
        print("   Then open: http://localhost:8080/")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
