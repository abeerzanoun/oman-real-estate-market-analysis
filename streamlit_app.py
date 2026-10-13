"""Local, read-only Oman real estate dashboard. Run: streamlit run streamlit_app.py."""
import streamlit as st

from src.dashboard_data import load_dashboard
from src.dashboard_pages import PAGES, render_page, style


def main():
    st.set_page_config(page_title="Oman Real Estate Observatory", page_icon="🏛️",
                       layout="wide", initial_sidebar_state="auto")
    style()
    with st.sidebar:
        st.markdown("### OMAN / عُمان\n**REAL ESTATE OBSERVATORY**")
        st.caption("Audited records · Transparent coverage")
        page = st.radio("Explore | استكشف", list(PAGES), format_func=lambda name: PAGES[name], key="page")
        st.divider()
        st.caption("Counts describe source record occurrences. Unique transactions are unverified.")
    try:
        bundle = load_dashboard()
    except (ValueError, OSError, KeyError) as exc:
        st.error(f"Data integrity check failed. Dashboard stopped: {exc}")
        st.stop()
    render_page(page, bundle)
    st.divider()
    st.caption("Reviewed EDA 168665c92a8a2ff91598 · Duplicate audit 4162ac42cfdaebd9d962 · "
               "Original uploads preserved · No missing months inferred")


if __name__ == "__main__":
    main()
