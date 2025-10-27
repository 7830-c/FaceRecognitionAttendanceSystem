import streamlit as st
import base64


st.set_page_config(
    page_title="Home",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        st.error(f"ERROR: Image file not found at path: {bin_file}. Please check the path and file name.")
        return None





img_path = "Resources/Graphics/BG_image_app.jpg"
bin_str = get_base64_of_bin_file(img_path)

if bin_str:

    page_bg_img = f''' 
    <style> 
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: right top; /* Keeps the person on the right */
    }} 

    [data-testid="stBlock"] {{
        max-width: 50%; /* Adjust this percentage as needed (e.g., 40% or 60%) */
        color: black !important; /* Forces all elements inside the block to black */
        text-shadow: 1px 1px 2px white; /* Optional: Adds a slight shadow to make black text stand out against a busy background */
    }}

    h1, h2, h3, .stMarkdown p {{
        color: black !important; 
    }}
    </style> 
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)



st.subheader("Face Recognition")
st.subheader("🎥🎥 Attendance System ")

st.markdown("""
<div style="color: black;">

<br>
            
### Key Features:
* **Zero-Contact Check-in** 
* **Real-Time Data** 
* **High Accuracy**

</div>
""", unsafe_allow_html=True)
