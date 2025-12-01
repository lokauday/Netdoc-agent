"""
NetDoc AI — Billing Engine (Stripe + Multi-Tenant SaaS)
"""

import streamlit as st
import stripe
from database import SessionLocal, Organization

# Load Stripe Secret Key
STRIPE_SECRET = st.secrets.get("STRIPE_SECRET")

if STRIPE_SECRET:
    stripe.api_key = STRIPE_SECRET
else:
    stripe.api_key = None    # avoids errors if not yet configured


# ============================================================
#  PLAN DEFINITIONS
# ============================================================
PLANS = {
    "free": {
        "name": "Free Tier",
        "price_id": None,            # No Stripe checkout
        "monthly_price": 0,
        "seats": 1,
        "features": [
            "1 user",
            "Basic Upload & Audit",
            "No AI Documentation",
            "No Combined PDF",
            "No API Access"
        ]
    },
    "pro": {
        "name": "Pro",
        "price_id": st.secrets.get("STRIPE_PRICE_PRO"),  # Stripe Price ID
        "monthly_price": 29,
        "seats": 5,
        "features": [
            "Up to 5 users",
            "Full AI Documentation",
            "Security Audits",
            "Topology Generator",
            "Combined Enterprise PDF",
            "API Access"
        ]
    },
    "enterprise": {
        "name": "Enterprise",
        "price_id": st.secrets.get("STRIPE_PRICE_ENTERPRISE"),
        "monthly_price": 99,
        "seats": 25,
        "features": [
            "25 users",
            "Unlimited audits",
            "Unlimited configs",
            "Advanced AI",
            "SLA / Priority Support",
            "Custom Integrations",
            "Admin API"
        ]
    }
}


# ============================================================
#  BILLING PAGE UI
# ============================================================
def billing_page():
    st.title("💳 NetDoc AI Billing")

    org_id = st.session_state.get("org_id")

    if not org_id:
        st.warning("No organization detected.")
        return

    db = SessionLocal()
    org = db.query(Organization).filter(Organization.id == org_id).first()
    db.close()

    st.subheader(f"Organization: {org.name}")
    st.write(f"Current Plan: **{org.plan or 'free'}**")

    st.write("---")
    st.header("Available Plans")

    # Display plans
    for plan_key, p in PLANS.items():
        st.subheader(f"🌐 {p['name']}")
        st.write(f"💲 ${p['monthly_price']}/mo")
        st.write("**Features:**")
        for f in p["features"]:
            st.write(f"✔ {f}")

        # Billing button
        if plan_key == "free":
            st.info("You are automatically on Free Tier.")
        else:
            if st.button(f"Upgrade to {p['name']}", key=plan_key):
                if not stripe.api_key:
                    st.error("Stripe is not configured. Add STRIPE_SECRET to secrets.")
                else:
                    checkout_url = stripe.checkout.Session.create(
                        success_url=st.secrets["SUCCESS_URL"],
                        cancel_url=st.secrets["CANCEL_URL"],
                        mode="subscription",
                        line_items=[
                            {"price": p["price_id"], "quantity": 1}
                        ],
                        metadata={
                            "org_id": org_id,
                            "plan": plan_key
                        }
                    ).url

                    st.markdown(f"[Click here to proceed to checkout]({checkout_url})")


# ============================================================
#  PLAN GATEKEEPER
# ============================================================
def require_plan(required_plan):
    """
    Use inside any feature page to restrict usage:

    require_plan("pro")
    """
    org_plan = st.session_state.get("org_plan", "free")

    plan_order = ["free", "pro", "enterprise"]

    if plan_order.index(org_plan) < plan_order.index(required_plan):
        st.error(f"🚫 This feature requires the **{required_plan.upper()}** plan.")
        st.stop()

