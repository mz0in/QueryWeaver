#!/usr/bin/env python3
"""
Test script to verify role assignment works correctly.
"""

import sys
import os
sys.path.append('.')

from api.extensions import db
from api.auth.organization_management import (
    check_or_create_organization, 
    get_user_role,
    extract_email_domain
)
from api.auth.user_management import ensure_user_in_organizations

def test_first_user_admin_role():
    """Test that the first user in an organization gets admin role."""
    
    # Test email
    test_email = "admin@testcompany.com"
    domain = extract_email_domain(test_email)
    
    print(f"Testing role assignment for: {test_email}")
    print(f"Domain: {domain}")
    
    # Clear any existing data for this test domain
    try:
        organizations_graph = db.select_graph("Organizations")
        
        # Clean up test data
        cleanup_query = """
        MATCH (user:User {email: $email})-[r:BELONGS_TO]->(org:Organization {domain: $domain})
        DELETE r
        WITH user, org
        OPTIONAL MATCH (user)<-[:AUTHENTICATES]-(identity:Identity)
        DELETE identity, user, org
        """
        organizations_graph.query(cleanup_query, {"email": test_email, "domain": domain})
        print("Cleaned up existing test data")
        
    except Exception as e:
        print(f"Cleanup warning: {e}")
    
    # Test user creation (should be first user and get admin role)
    print("\n1. Creating first user in organization...")
    is_new_user, user_info = ensure_user_in_organizations(
        provider_user_id="test123",
        email=test_email,
        name="Test Admin",
        provider="google"
    )
    
    if user_info:
        print(f"✓ User created successfully: {is_new_user}")
        
        # Check user role
        role = get_user_role(test_email)
        print(f"✓ User role: {role}")
        
        if role == "admin":
            print("✅ SUCCESS: First user correctly assigned admin role!")
        else:
            print(f"❌ FAILURE: First user has role '{role}', expected 'admin'")
            
        # Check organization creation
        is_new_org, org_info = check_or_create_organization(test_email)
        print(f"✓ Organization new: {not is_new_org} (should be False since it exists now)")
        
    else:
        print("❌ FAILURE: User creation failed")
    
    # Test second user (should get default 'user' role and be pending)
    print("\n2. Creating second user in same organization...")
    second_email = "user@testcompany.com"
    
    is_new_user2, user_info2 = ensure_user_in_organizations(
        provider_user_id="test456",
        email=second_email,
        name="Test User",
        provider="google"
    )
    
    if user_info2:
        print(f"✓ Second user created: {is_new_user2}")
        
        role2 = get_user_role(second_email)
        print(f"✓ Second user role: {role2}")
        
        if role2 == "user":
            print("✅ SUCCESS: Second user correctly assigned user role!")
        else:
            print(f"❌ FAILURE: Second user has role '{role2}', expected 'user'")
    else:
        print("❌ FAILURE: Second user creation failed")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_first_user_admin_role()
