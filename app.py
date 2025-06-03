import streamlit as st
import json

# Load navigation configuration
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = None

# Load config
config = load_config()

# Set page config
st.set_page_config(
    page_title=config["navigation"]["title"],
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide the default navigation
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title(config["navigation"]["title"])

# Add navigation links
for page in config["navigation"]["pages"]:
    if page["enabled"]:
        if st.sidebar.button(page["name"], help=page["description"]):
            st.session_state.current_page = page["path"]

# Main content area
if st.session_state.current_page:
    # Load and execute the selected page
    with open(st.session_state.current_page, "r") as f:
        exec(f.read())
else:
    # Show welcome page
    st.title("Fun with Weaviate")
    st.write("Select a demo from the sidebar to get started!")

    # Display available demos
    st.subheader("Demos & descriptions")
    cols = st.columns(2)
    for i, page in enumerate(config["navigation"]["pages"]):
        if page["enabled"]:
            with cols[i % 2]:
                st.info(f"**{page['name']}**\n\n{page['description']}")
