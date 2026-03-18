import streamlit as st

from utils.ocr_config import configure_ocr

configure_ocr()

from utils.navigation import render_sidebar

render_sidebar()

st.title("Subscription Plans")

plans = [
    {
        "name": "Starter",
        "price": "Free",
        "features": [
            "5 Free Uses",
            "Basic AI Tools",
            "Limited Storage"
        ]
    },
    {
        "name": "Pro",
        "price": "₦50,000",
        "features": [
            "Unlimited Access",
            "All AI Tools",
            "Vault Storage",
            "Priority Processing"
        ]
    },
    {
        "name": "Enterprise",
        "price": "Custom",
        "features": [
            "Team Access",
            "Advanced Analytics",
            "API Access",
            "Dedicated Support"
        ]
    }
]

for plan in plans:

    st.subheader(plan["name"])
    st.write(f"💰 {plan['price']}")

    for f in plan["features"]:
        st.write(f"✔️ {f}")

    if st.button(f"Choose {plan['name']}"):
        st.info("Payment workflow coming next")

    st.divider()