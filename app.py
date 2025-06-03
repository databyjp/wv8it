import streamlit as st
import json
import torch

torch.classes.__path__ = []  # Prevent error shown here https://discuss.streamlit.io/t/error-in-torch-with-streamlit/90908/5

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

# Custom CSS for better styling
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        .main-header {
            font-size: 3rem;
            font-weight: 700;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .demo-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid #e9ecef;
        }
        .demo-title {
            color: #1E88E5;
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        .demo-description {
            color: #666;
            font-size: 1rem;
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

# Add repository link
st.sidebar.markdown("---")
st.sidebar.markdown("Source code: [https://github.com/databyjp/wv8it](https://github.com/databyjp/wv8it)")

# Main content area
if st.session_state.current_page:
    # Load and execute the selected page
    with open(st.session_state.current_page, "r") as f:
        exec(f.read())
else:
    # Show welcome page
    st.markdown('<div class="main-header">🚀 Fun with Weaviate</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Explore the power of vector search and AI with these interactive demos</div>', unsafe_allow_html=True)

    # Display available demos
    st.markdown("### Available Demos")
    st.markdown("---")
    st.markdown("**Select any demo from the sidebar** to get started with your exploration!")
    st.markdown("---")

    # Create a grid of demo cards
    enabled_pages = [page for page in config["navigation"]["pages"] if page["enabled"]]
    for i in range(0, len(enabled_pages), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(enabled_pages):
                with cols[j]:
                    page = enabled_pages[i + j]
                    st.markdown(f"""
                        <div class="demo-card">
                            <div class="demo-title">{page['name']}</div>
                            <div class="demo-description">{page['description']}</div>
                        </div>
                    """, unsafe_allow_html=True)

