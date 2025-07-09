#!/usr/bin/env python3
"""
Integration test script for GitHub commit automation system
Tests MCP server functionality and validates configuration
"""

import asyncio
import json
import os
import requests
import sys
import time
from pathlib import Path

# Test configuration
MCP_SERVER_URL = "http://localhost:8001"
TEST_DATA_DIR = Path(__file__).parent / "test_data"

def print_status(message, status="INFO"):
    """Print formatted status message"""
    colors = {
        "INFO": "\033[36m",    # Cyan
        "SUCCESS": "\033[32m", # Green 
        "ERROR": "\033[31m",   # Red
        "WARNING": "\033[33m", # Yellow
    }
    reset = "\033[0m"
    print(f"{colors.get(status, '')}{status}: {message}{reset}")

def test_mcp_server_health():
    """Test MCP server health endpoint"""
    print_status("Testing MCP server health endpoint...")
    try:
        response = requests.get(f"{MCP_SERVER_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_status(f"MCP server is healthy - Version: {data.get('version')}", "SUCCESS")
            return True
        else:
            print_status(f"MCP server health check failed: {response.status_code}", "ERROR")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"Cannot connect to MCP server: {e}", "ERROR")
        return False

def test_mcp_capabilities():
    """Test MCP server capabilities endpoint"""
    print_status("Testing MCP server capabilities...")
    try:
        response = requests.get(f"{MCP_SERVER_URL}/capabilities", timeout=10)
        if response.status_code == 200:
            data = response.json()
            capabilities = data.get('capabilities', [])
            print_status(f"MCP server capabilities: {', '.join(capabilities)}", "SUCCESS")
            return True
        else:
            print_status(f"Capabilities endpoint failed: {response.status_code}", "ERROR")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"Cannot get capabilities: {e}", "ERROR")
        return False

def test_commit_analysis():
    """Test commit analysis functionality"""
    print_status("Testing commit analysis...")
    
    test_commit = {
        "commit_hash": "test123abc456",
        "commit_message": "feat: implement automated testing framework",
        "commit_author": "Test Developer",
        "repository_name": "Dashboard",
        "branch_name": "feature/testing",
        "added_files": ["tests/test_automation.py", "tests/fixtures.py"],
        "modified_files": ["app/main.py", "requirements.txt"],
        "removed_files": [],
        "total_files_changed": 4,
        "commit_url": "https://github.com/test/repo/commit/test123abc456"
    }
    
    try:
        response = requests.post(
            f"{MCP_SERVER_URL}/analyze-commit",
            json=test_commit,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Validate response structure
            required_fields = ["commit_hash", "quality_score", "category", "impact_level", "report"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print_status(f"Missing required fields: {missing_fields}", "ERROR")
                return False
            
            print_status(f"Analysis successful - Quality: {data['quality_score']}/10, Category: {data['category']}", "SUCCESS")
            print_status(f"Impact Level: {data['impact_level']}", "INFO")
            
            # Check if report is generated
            if data.get('report') and len(data['report']) > 100:
                print_status("Detailed report generated successfully", "SUCCESS")
            else:
                print_status("Report seems too short or missing", "WARNING")
            
            return True
        else:
            print_status(f"Commit analysis failed: {response.status_code} - {response.text}", "ERROR")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"Cannot analyze commit: {e}", "ERROR")
        return False

def test_various_commit_types():
    """Test analysis with different types of commits"""
    print_status("Testing various commit types...")
    
    test_cases = [
        {
            "name": "Feature commit",
            "data": {
                "commit_hash": "feat001",
                "commit_message": "feat: add user dashboard",
                "commit_author": "Developer",
                "repository_name": "Dashboard",
                "branch_name": "feature/dashboard",
                "added_files": ["dashboard.py"],
                "modified_files": ["app.py"],
                "removed_files": [],
                "total_files_changed": 2,
                "commit_url": "https://github.com/test/repo/commit/feat001"
            },
            "expected_category": "feature"
        },
        {
            "name": "Bugfix commit",
            "data": {
                "commit_hash": "fix001",
                "commit_message": "fix: resolve authentication bug",
                "commit_author": "Developer",
                "repository_name": "Dashboard",
                "branch_name": "hotfix/auth",
                "added_files": [],
                "modified_files": ["auth.py"],
                "removed_files": [],
                "total_files_changed": 1,
                "commit_url": "https://github.com/test/repo/commit/fix001"
            },
            "expected_category": "bugfix"
        },
        {
            "name": "Documentation commit",
            "data": {
                "commit_hash": "docs001",
                "commit_message": "docs: update API documentation",
                "commit_author": "Developer",
                "repository_name": "Dashboard",
                "branch_name": "main",
                "added_files": [],
                "modified_files": ["README.md"],
                "removed_files": [],
                "total_files_changed": 1,
                "commit_url": "https://github.com/test/repo/commit/docs001"
            },
            "expected_category": "documentation"
        }
    ]
    
    success_count = 0
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{MCP_SERVER_URL}/analyze-commit",
                json=test_case["data"],
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("category") == test_case["expected_category"]:
                    print_status(f"{test_case['name']}: Correctly categorized as {data['category']}", "SUCCESS")
                    success_count += 1
                else:
                    print_status(f"{test_case['name']}: Expected {test_case['expected_category']}, got {data.get('category')}", "WARNING")
            else:
                print_status(f"{test_case['name']}: Analysis failed", "ERROR")
                
        except Exception as e:
            print_status(f"{test_case['name']}: Error - {e}", "ERROR")
    
    print_status(f"Commit type analysis: {success_count}/{len(test_cases)} passed", "INFO")
    return success_count == len(test_cases)

def test_configuration_files():
    """Test that all required configuration files exist"""
    print_status("Checking configuration files...")
    
    required_files = [
        "workflows/github-notion-automation.json",
        "mcp-server/commit-analyzer.py",
        "mcp-server/requirements.txt",
        "mcp-server/config.json",
        "docs/setup-guide.md",
        "docs/notion-database-template.md",
        ".env.example",
        "docker-compose.yml",
        ".gitignore"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print_status(f"Missing required files: {', '.join(missing_files)}", "ERROR")
        return False
    else:
        print_status("All required configuration files present", "SUCCESS")
        return True

def test_n8n_workflow():
    """Test n8n workflow file structure"""
    print_status("Validating n8n workflow...")
    
    workflow_path = Path("workflows/github-notion-automation.json")
    try:
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)
        
        # Check for required workflow components
        required_components = ["name", "nodes", "connections"]
        missing_components = [comp for comp in required_components if comp not in workflow_data]
        
        if missing_components:
            print_status(f"Workflow missing components: {missing_components}", "ERROR")
            return False
        
        # Check for essential nodes
        node_names = [node.get("name", "") for node in workflow_data.get("nodes", [])]
        essential_nodes = ["GitHub Webhook", "Analyze Commit with MCP", "Create Notion Entry"]
        missing_nodes = [node for node in essential_nodes if node not in node_names]
        
        if missing_nodes:
            print_status(f"Workflow missing essential nodes: {missing_nodes}", "WARNING")
        
        print_status(f"n8n workflow validated - {len(node_names)} nodes found", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"Failed to validate workflow: {e}", "ERROR")
        return False

def run_all_tests():
    """Run all tests and return overall result"""
    print_status("Starting GitHub Commit Automation System Tests", "INFO")
    print("=" * 60)
    
    tests = [
        ("Configuration Files", test_configuration_files),
        ("n8n Workflow", test_n8n_workflow),
        ("MCP Server Health", test_mcp_server_health),
        ("MCP Capabilities", test_mcp_capabilities),
        ("Commit Analysis", test_commit_analysis),
        ("Commit Type Analysis", test_various_commit_types),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Running: {test_name}")
        print(f"{'-' * 40}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"Test {test_name} failed with exception: {e}", "ERROR")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print_status("TEST RESULTS SUMMARY", "INFO")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = "SUCCESS" if result else "ERROR"
        print_status(f"{test_name}: {status}", color)
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print_status("🎉 All tests passed! The system is ready for deployment.", "SUCCESS")
        return True
    else:
        print_status(f"❌ {len(results) - passed} tests failed. Please check the issues above.", "ERROR")
        return False

if __name__ == "__main__":
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)