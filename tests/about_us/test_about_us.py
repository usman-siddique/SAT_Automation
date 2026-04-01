# ============================================================
# tests/about_us/test_about_us.py
#
# HOW TO RUN:
#   pytest tests/about_us/test_about_us.py -v -s
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pages.about_us.about_us_page import AboutUsPage
from pages.about_us.loyalty_program_page import LoyaltyProgramPage
from pages.about_us.join_sat_pro_page import JoinSatProPage


# ============================================================
# Test 1: About SAT
# ============================================================

def test_about_sat(page_no_login):
    print("\n" + "="*60)
    print("✅ ABOUT SAT - CONTENT VERIFICATION")
    print("="*60)

    about = AboutUsPage(page_no_login)
    about.go_to_about_sat()
    about.verify_about_sat()

    print("\n✅ ABOUT SAT TEST COMPLETE")


# ============================================================
# Test 2: Company Profile
# ============================================================

def test_company_profile(page_no_login):
    print("\n" + "="*60)
    print("✅ COMPANY PROFILE - CONTENT VERIFICATION")
    print("="*60)

    about = AboutUsPage(page_no_login)
    about.go_to_company_profile()
    about.verify_company_profile()

    print("\n✅ COMPANY PROFILE TEST COMPLETE")


# ============================================================
# Test 3: Why Choose SAT
# ============================================================

def test_why_choose_sat(page_no_login):
    print("\n" + "="*60)
    print("✅ WHY CHOOSE SAT - CONTENT VERIFICATION")
    print("="*60)

    about = AboutUsPage(page_no_login)
    about.go_to_why_choose_sat()
    about.verify_why_choose_sat()

    print("\n✅ WHY CHOOSE SAT TEST COMPLETE")


# ============================================================
# Test 4: Privacy Policy
# ============================================================

def test_privacy_policy(page_no_login):
    print("\n" + "="*60)
    print("✅ PRIVACY POLICY - CONTENT VERIFICATION")
    print("="*60)

    about = AboutUsPage(page_no_login)
    about.go_to_privacy_policy()
    about.verify_privacy_policy()

    print("\n✅ PRIVACY POLICY TEST COMPLETE")


# ============================================================
# Test 5: Terms and Conditions
# ============================================================

def test_terms_and_conditions(page_no_login):
    print("\n" + "="*60)
    print("✅ TERMS AND CONDITIONS - CONTENT VERIFICATION")
    print("="*60)

    about = AboutUsPage(page_no_login)
    about.go_to_terms_and_conditions()
    about.verify_terms_and_conditions()

    print("\n✅ TERMS AND CONDITIONS TEST COMPLETE")


# ============================================================
# Test 6: Shipping Agents
# ============================================================

def test_shipping_agents(page_no_login):
    print("\n" + "="*60)
    print("✅ SHIPPING AGENTS - CONTENT VERIFICATION")
    print("="*60)

    about = AboutUsPage(page_no_login)
    about.go_to_shipping_agents()
    about.verify_shipping_agents()

    print("\n✅ SHIPPING AGENTS TEST COMPLETE")


# ============================================================
# Test 7: Loyalty Program - Logged Out
# ============================================================

def test_loyalty_program_logged_out(page_no_login):
    print("\n" + "="*60)
    print("✅ LOYALTY PROGRAM - LOGGED OUT STATE")
    print("="*60)

    loyalty = LoyaltyProgramPage(page_no_login)
    loyalty.go_to_loyalty_program()
    loyalty.verify_logged_out_state()

    print("\n✅ LOYALTY PROGRAM LOGGED OUT TEST COMPLETE")


# ============================================================
# Test 8: Loyalty Program - Logged In
# ============================================================

def test_loyalty_program_logged_in(page):
    print("\n" + "="*60)
    print("✅ LOYALTY PROGRAM - LOGGED IN STATE")
    print("="*60)

    loyalty = LoyaltyProgramPage(page)
    loyalty.verify_logged_in_state()

    print("\n✅ LOYALTY PROGRAM LOGGED IN TEST COMPLETE")


# ============================================================
# Test 9: Join SAT Pro - Logged Out Flow
# Handles both states: if session already active, skips login
# ============================================================

def test_join_sat_pro_logged_out(page_no_login):
    print("\n" + "="*60)
    print("✅ JOIN SAT PRO - LOGGED OUT FLOW")
    print("="*60)

    sat_pro = JoinSatProPage(page_no_login)
    sat_pro.flow_logged_out()

    print("\n✅ JOIN SAT PRO LOGGED OUT TEST COMPLETE")


# ============================================================
# Test 10: Join SAT Pro - Logged In Flow
# ============================================================

def test_join_sat_pro_logged_in(page):
    print("\n" + "="*60)
    print("✅ JOIN SAT PRO - LOGGED IN FLOW")
    print("="*60)

    sat_pro = JoinSatProPage(page)
    sat_pro.flow_logged_in()

    print("\n✅ JOIN SAT PRO LOGGED IN TEST COMPLETE")