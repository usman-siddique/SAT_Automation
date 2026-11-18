# ============================================================
# tests/about_us/test_about_us.py
#
# HOW TO RUN:
#   pytest tests/about_us/test_about_us.py -v -s
# ============================================================

import sys
import os
import pytest
from playwright.sync_api import Error as PlaywrightError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from config import BASE_URL
from pages.about_us.about_sat_page import AboutSatPage
from pages.about_us.company_profile_page import CompanyProfilePage
from pages.about_us.corporate_page import CorporatePage
from pages.about_us.customer_reviews_page import CustomerReviewsPage
from pages.about_us.loyalty_program_page import LoyaltyProgramPage
from pages.about_us.join_sat_pro_page import JoinSatProPage
from pages.about_us.privacy_policy_page import PrivacyPolicyPage
from pages.about_us.security_export_control_page import SecurityExportControlPage
from pages.about_us.shipping_agents_page import ShippingAgentsPage
from pages.about_us.terms_conditions_page import TermsConditionsPage
from pages.about_us.why_choose_sat_page import WhyChooseSatPage


# ============================================================
# About SAT: desktop content and business claims
# ============================================================

def test_about_sat_content_and_milestones(page_no_login):
    about = AboutSatPage(page_no_login)
    about.go_to_about_sat()
    about.verify_about_sat()


# ============================================================
# About SAT: media galleries and interactive carousel
# ============================================================

def test_about_sat_media_and_carousel(page_no_login):
    about = AboutSatPage(page_no_login)
    about.go_to_about_sat()
    about.verify_about_sat_media_and_carousel()


# ============================================================
# About SAT: every featured link and the linked PDF
# ============================================================

def test_about_sat_feature_links_and_pdf(page_no_login):
    about = AboutSatPage(page_no_login)
    about.go_to_about_sat()
    about.verify_about_sat_feature_links_and_pdf()


@pytest.fixture
def about_us_mobile_page(browser, request):
    context = browser.new_context(
        viewport={"width": 390, "height": 844},
        screen={"width": 390, "height": 844},
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 "
            "Mobile/15E148 Safari/604.1"
        ),
        device_scale_factor=3,
        is_mobile=True,
        has_touch=True,
    )
    mobile_page = context.new_page()
    mobile_page.set_default_timeout(30000)
    request.node._sat_active_page = mobile_page

    last_error = "unknown mobile homepage error"
    for attempt in range(1, 4):
        try:
            response = mobile_page.goto(
                BASE_URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )
            if response is not None and response.status >= 500:
                raise AssertionError(f"Homepage returned HTTP {response.status}")
            mobile_page.locator("#navbar_mobile_header").wait_for(
                state="visible",
                timeout=10000,
            )
            break
        except (PlaywrightError, AssertionError) as error:
            last_error = str(error)
            if attempt == 3:
                context.close()
                raise AssertionError(
                    "Development mobile homepage did not become ready after "
                    f"3 attempts: {last_error}"
                ) from error

    try:
        yield mobile_page
    finally:
        if not mobile_page.is_closed():
            mobile_page.close()
        context.close()


# ============================================================
# About SAT: real mobile navigation and responsive layout
# ============================================================

def test_about_sat_mobile_navigation_and_layout(about_us_mobile_page):
    about = AboutSatPage(about_us_mobile_page)
    about.go_to_about_sat_mobile()
    about.verify_about_sat_mobile_layout()


# ============================================================
# Company Profile: overview, business details, and content consistency
# ============================================================

def test_company_profile_overview_and_details(page_no_login):
    about = CompanyProfilePage(page_no_login)
    about.go_to_company_profile()
    about.verify_company_profile_overview_and_details()


# ============================================================
# Company Profile: milestones, services, values, and media
# ============================================================

def test_company_profile_milestones_services_and_values(page_no_login):
    about = CompanyProfilePage(page_no_login)
    about.go_to_company_profile()
    about.verify_company_profile_milestones_services_and_values()


# ============================================================
# Company Profile: every featured link and the linked PDF
# ============================================================

def test_company_profile_feature_links_and_pdf(page_no_login):
    about = CompanyProfilePage(page_no_login)
    about.go_to_company_profile()
    about.verify_company_profile_feature_links_and_pdf()


# ============================================================
# Company Profile: real mobile navigation and responsive layout
# ============================================================

def test_company_profile_mobile_navigation_and_layout(about_us_mobile_page):
    about = CompanyProfilePage(about_us_mobile_page)
    about.go_to_company_profile_mobile()
    about.verify_company_profile_mobile_layout()


# ============================================================
# Corporate: content, navigation cards, destinations, and media
# ============================================================

def test_corporate_overview_cards_and_media(page_no_login):
    about = CorporatePage(page_no_login)
    about.go_to_corporate()
    about.verify_corporate_overview_cards_and_media()


# ============================================================
# Corporate: every blog, review, vehicle-search, and share link
# ============================================================

def test_corporate_blog_and_review_links(page_no_login):
    about = CorporatePage(page_no_login)
    about.go_to_corporate()
    about.verify_corporate_blog_and_review_links()


# ============================================================
# Corporate: real mobile menu navigation
# ============================================================

def test_corporate_mobile_navigation(about_us_mobile_page):
    about = CorporatePage(about_us_mobile_page)
    about.go_to_corporate_mobile()


# ============================================================
# Corporate: direct mobile layout, content, images, and card grids
# ============================================================

def test_corporate_mobile_layout(about_us_mobile_page):
    about = CorporatePage(about_us_mobile_page)
    about.open_corporate_direct()
    about.verify_corporate_mobile_layout()


# ============================================================
# Customer Reviews: filter contract, review metadata, and video links
# ============================================================

def test_customer_reviews_filters_content_and_celebrity_links(page_no_login):
    reviews = CustomerReviewsPage(page_no_login)
    reviews.go_to_customer_reviews()
    reviews.verify_filter_controls_reviews_and_celebrity_links()


# ============================================================
# Customer Reviews: populated countries, empty country, and clear filter
# ============================================================

def test_customer_reviews_country_filters_and_empty_state(page_no_login):
    reviews = CustomerReviewsPage(page_no_login)
    reviews.go_to_customer_reviews()
    reviews.verify_country_filters_and_empty_state()


# ============================================================
# Customer Reviews: dependent Make/Model and star filters
# ============================================================

def test_customer_reviews_make_model_and_star_filters(page_no_login):
    reviews = CustomerReviewsPage(page_no_login)
    reviews.go_to_customer_reviews()
    reviews.verify_make_model_and_star_filters()


# ============================================================
# Customer Reviews: real mobile navigation, country filter, and reset
# ============================================================

def test_customer_reviews_mobile_country_filter_and_reset(about_us_mobile_page):
    reviews = CustomerReviewsPage(about_us_mobile_page)
    reviews.go_to_customer_reviews_mobile()
    reviews.verify_mobile_country_filter_reset_and_layout()


# Why Choose SAT: full content, loaded media, and alternating desktop layout

def test_why_choose_sat_content_images_and_desktop_layout(page_no_login):
    why_choose = WhyChooseSatPage(page_no_login)
    why_choose.go_to_why_choose_sat()
    why_choose.verify_content_images_and_desktop_layout()


# Why Choose SAT: page-specific inquiry link destination

def test_why_choose_sat_inquiry_link_navigation(page_no_login):
    why_choose = WhyChooseSatPage(page_no_login)
    why_choose.go_to_why_choose_sat()
    why_choose.verify_inquiry_link()


# Why Choose SAT: mobile navigation, content, images, stacking, and overflow

def test_why_choose_sat_mobile_content_navigation_and_layout(
    about_us_mobile_page,
):
    why_choose = WhyChooseSatPage(about_us_mobile_page)
    why_choose.go_to_why_choose_sat_mobile()
    why_choose.verify_mobile_content_and_layout()


# Policy pages: browser titles and all page headings

def test_policy_pages_titles_and_headings(page_no_login):
    privacy = PrivacyPolicyPage(page_no_login)
    terms = TermsConditionsPage(page_no_login)
    failures = []

    privacy.go_to_privacy_policy()
    try:
        privacy.verify_privacy_title_and_headings()
    except AssertionError as error:
        failures.append(f"Privacy Policy: {error}")

    terms.go_to_terms_and_conditions()
    try:
        terms.verify_terms_title_and_headings()
    except AssertionError as error:
        failures.append(f"Terms and Conditions: {error}")

    assert not failures, "Policy page failures:\n- " + "\n- ".join(failures)


# Policy pages: Privacy email links and Terms vehicle agreement PDF

def test_policy_pages_hyperlinks_and_vehicle_pdf(page_no_login):
    privacy = PrivacyPolicyPage(page_no_login)
    terms = TermsConditionsPage(page_no_login)
    privacy.go_to_privacy_policy()
    privacy.verify_privacy_email_links()
    terms.go_to_terms_and_conditions()
    terms.verify_terms_vehicle_agreement_pdf()


# Policy pages: mobile navigation, headings, links, and responsive layout

def test_policy_pages_mobile_navigation_content_and_layout(
    about_us_mobile_page,
):
    privacy = PrivacyPolicyPage(about_us_mobile_page)
    terms = TermsConditionsPage(about_us_mobile_page)
    privacy.go_to_privacy_policy_mobile()
    privacy.verify_privacy_policy_mobile()
    terms.go_to_terms_and_conditions_mobile()
    terms.verify_terms_and_conditions_mobile()


# Shipping Agents: page content, all agent details, map, and card media

def test_shipping_agents_content_cards_and_media(page_no_login):
    shipping = ShippingAgentsPage(page_no_login)
    shipping.go_to_shipping_agents()
    shipping.verify_content_cards_and_media()


# Shipping Agents: every country filter and All reset behavior

def test_shipping_agents_every_country_filter_and_reset(page_no_login):
    shipping = ShippingAgentsPage(page_no_login)
    shipping.go_to_shipping_agents()
    shipping.verify_every_country_filter_and_reset()


# Shipping Agents: mobile menu navigation, filtering, reset, and usable layout

def test_shipping_agents_mobile_navigation_filter_and_layout(
    about_us_mobile_page,
):
    shipping = ShippingAgentsPage(about_us_mobile_page)
    shipping.go_to_shipping_agents_mobile()
    shipping.verify_mobile_filter_and_layout()


# Security Export Control: complete compliance content and desktop media

def test_security_export_control_content_and_desktop_media(page_no_login):
    security_export = SecurityExportControlPage(page_no_login)
    security_export.go_to_security_export_control()
    security_export.verify_desktop_content_and_media()


# Security Export Control: real mobile navigation, responsive media, and layout

def test_security_export_control_mobile_content_media_and_layout(
    about_us_mobile_page,
):
    security_export = SecurityExportControlPage(about_us_mobile_page)
    security_export.go_to_security_export_control_mobile()
    security_export.verify_mobile_content_media_and_layout()


# Loyalty Program: complete guest content, lock states, FAQs, and login CTA

def test_loyalty_program_guest_content_locks_faqs_and_signup(page_no_login):
    loyalty = LoyaltyProgramPage(page_no_login)
    loyalty.go_to_loyalty_program()
    loyalty.verify_logged_out_state()


# Loyalty Program: mobile navigation, content, interactions, and layout

def test_loyalty_program_mobile_guest_experience(about_us_mobile_page):
    loyalty = LoyaltyProgramPage(about_us_mobile_page)
    loyalty.go_to_loyalty_program_mobile()
    loyalty.verify_mobile_logged_out_state()


# Loyalty Program: permanent Master Level 3 account state

def test_loyalty_program_master_level_three(loyalty_master_page):
    loyalty = LoyaltyProgramPage(loyalty_master_page)
    loyalty.go_to_loyalty_program()
    loyalty.verify_master_level_three_state()


# Loyalty Program: active SAT Pro account state

def test_loyalty_program_sat_pro_member(loyalty_pro_page):
    loyalty = LoyaltyProgramPage(loyalty_pro_page)
    loyalty.go_to_loyalty_program()
    loyalty.verify_sat_pro_member_state()


# Join SAT Pro: complete guest content and all three login redirects

def test_join_sat_pro_guest_content_faqs_and_all_cta_redirects(page_no_login):
    sat_pro = JoinSatProPage(page_no_login)
    sat_pro.go_to_sat_pro()
    sat_pro.verify_landing_content()
    sat_pro.verify_all_guest_join_redirects()


# Join SAT Pro: mobile menu, content, CTA, and layout

def test_join_sat_pro_mobile_guest_experience(about_us_mobile_page):
    sat_pro = JoinSatProPage(about_us_mobile_page)
    sat_pro.go_to_sat_pro_mobile()
    sat_pro.verify_mobile_guest_experience()


# Join SAT Pro: non-Pro user payment page and safe popup checks

def test_join_sat_pro_non_member_payment_options(loyalty_master_page):
    sat_pro = JoinSatProPage(loyalty_master_page)
    sat_pro.go_to_sat_pro()
    sat_pro.open_non_member_payment_page()
    sat_pro.verify_payment_page_and_safe_popups()


# Join SAT Pro: active member CTAs and non-destructive membership management

def test_join_sat_pro_active_member_management_without_cancellation(
    loyalty_pro_page,
):
    sat_pro = JoinSatProPage(loyalty_pro_page)
    sat_pro.go_to_sat_pro()
    sat_pro.verify_active_member_and_membership_page()
