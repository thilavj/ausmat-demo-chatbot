import streamlit as st
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from io import BytesIO
import os

# --- Configuration ---
# You need to ensure 'tofucat.png' is in the same directory as this script.
PLACEHOLDER_IMAGE_PATH = "tofucat.png"

st.set_page_config(
    page_title="TofuCat Image Mixer",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Vibrant UI/UX ---
# Injecting custom CSS for a fun, vibrant look with playful colors and fonts.
st.markdown("""
<style>
/* 1. Main App Background and Font */
.stApp {
    background-color: #F7F7E0; /* Light Cream Background */
    color: #4B0082; /* Indigo/Violet Text */
    font-family: 'Comic Sans MS', cursive, sans-serif; /* Playful Font */
}

/* 2. Header and Title */
h1 {
    color: #FF6347; /* Tomato Red */
    text-shadow: 3px 3px 6px #00000030;
    border-bottom: 3px solid #FFD700; /* Gold Line */
    padding-bottom: 5px;
}
h2, h3 {
    color: #4682B4; /* Steel Blue */
}

/* 3. Sidebar Customization */
.css-1d391kg { /* Sidebar background */
    background-color: #ADD8E6; /* Light Blue/Cyan */
}
.css-1d391kg .stTextInput > div > div > input,
.css-1d391kg .stSelectbox > div > button,
.css-1d391kg .stSlider {
    border: 2px solid #FFD700; /* Gold borders for inputs */
    border-radius: 10px;
}
.sidebar .sidebar-content {
    color: #4B0082; /* Dark Text */
}
.css-1d391kg .st-eb {
    color: #4B0082; /* Sidebar header color */
}


/* 4. Download Button Styling (Making it stand out) */
.stDownloadButton>button {
    background-color: #3CB371; /* Medium Sea Green */
    color: white;
    border-radius: 20px; /* Highly rounded */
    border: 0px;
    padding: 15px 30px;
    font-size: 1.2rem;
    font-weight: bolder;
    box-shadow: 0 5px #2E8B57; /* 3D effect */
    transition: all 0.1s;
}
.stDownloadButton>button:hover {
    background-color: #43CD80; 
    box-shadow: 0 2px #2E8B57;
    transform: translateY(3px); /* Press effect */
}

/* 5. Info Box (Upload Prompt) */
div[data-testid="stAlert"] {
    background-color: #FFFFE0; /* Light Yellow */
    color: #DAA520; /* Goldenrod text */
    border-left: 8px solid #FFC107; /* Gold left border */
    border-radius: 15px;
    padding: 20px;
    font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

# --- Helper Functions for Image Processing ---

def apply_selected_filter(img, filter_name):
    """Applies a specific filter from PIL's ImageFilter."""
    if filter_name == "Blur":
        return img.filter(ImageFilter.BLUR)
    elif filter_name == "Contour":
        return img.filter(ImageFilter.CONTOUR)
    elif filter_name == "Detail":
        return img.filter(ImageFilter.DETAIL)
    elif filter_name == "Edge Enhance":
        return img.filter(ImageFilter.EDGE_ENHANCE)
    elif filter_name == "Sharpen":
        return img.filter(ImageFilter.SHARPEN)
    elif filter_name == "Smooth":
        return img.filter(ImageFilter.SMOOTH)
    elif filter_name == "Emboss":
        return img.filter(ImageFilter.EMBOSS)
    elif filter_name == "Find Edges":
        return img.filter(ImageFilter.FIND_EDGES)
    else:
        return img

def process_image(img, filter_choice, brightness, color, contrast, rotate_angle, mirror_h, mirror_v):
    """Applies enhancements and transformations."""
    
    processed_img = apply_selected_filter(img, filter_choice)

    enhancer = ImageEnhance.Brightness(processed_img)
    processed_img = enhancer.enhance(brightness)
    
    enhancer = ImageEnhance.Color(processed_img)
    processed_img = enhancer.enhance(color)
    
    enhancer = ImageEnhance.Contrast(processed_img)
    processed_img = enhancer.enhance(contrast)

    if rotate_angle != 0:
        processed_img = processed_img.rotate(rotate_angle, expand=True)
        
    if mirror_h:
        processed_img = ImageOps.mirror(processed_img)
    if mirror_v:
        processed_img = ImageOps.flip(processed_img)
        
    return processed_img

def get_image_download_link(img, filename, text):
    """Generates a link for downloading the processed image."""
    
    buf = BytesIO()
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label=text,
        data=byte_im,
        file_name=filename,
        mime="image/png"
    )

# --- Main Streamlit App ---

def main():
    st.title("🐾 TofuCat Image Mixer!")
    st.markdown("## 🌈 Upload your photo and make it POP!")

    # --- Sidebar for Image Upload and Options ---
    st.sidebar.header("📥 Upload Zone")
    uploaded_file = st.sidebar.file_uploader("Grab a file (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
    
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Edit Power")

    # Initialize control variables 
    filter_choice = "Original"
    brightness = 1.0
    color = 1.0
    contrast = 1.0
    rotate_angle = 0
    mirror_h = False
    mirror_v = False
    
    # Filters
    filter_choice = st.sidebar.selectbox(
        "✨ Select a Fun Filter",
        ["Original", "Sharpen", "Blur", "Contour", "Detail", "Edge Enhance", "Smooth", "Emboss", "Find Edges"]
    )

    # Enhancements Sliders
    st.sidebar.subheader("🌟 Brightness & Contrast")
    brightness = st.sidebar.slider("🔆 Brightness", 0.0, 3.0, 1.0, 0.1)
    color = st.sidebar.slider("🎨 Color Balance", 0.0, 3.0, 1.0, 0.1)
    contrast = st.sidebar.slider("🌑 Contrast", 0.0, 3.0, 1.0, 0.1)

    # Transformations
    st.sidebar.subheader("📐 Move & Flip")
    rotate_angle = st.sidebar.slider("🔄 Rotate (90° Increments)", 0, 360, 0, 90)
    col_h, col_v = st.sidebar.columns(2)
    with col_h:
        mirror_h = st.checkbox("🪞 Mirror (Horizontal)")
    with col_v:
        mirror_v = st.checkbox("⬇️ Flip (Vertical)")
        
    st.sidebar.markdown("---")
    st.sidebar.info("Adjust the sliders and filters, the image updates instantly!")
    
    # --- Main Content Area ---
    if uploaded_file is not None:
        try:
            original_image = Image.open(uploaded_file)
            
            # --- Processing ---
            edited_image = process_image(
                original_image, 
                filter_choice, 
                brightness, 
                color, 
                contrast, 
                rotate_angle, 
                mirror_h, 
                mirror_v
            )

            # --- Display ---
            st.header("Your Before & After")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original")
                # Fix: Use use_container_width=True
                st.image(original_image, use_container_width=True)

            with col2:
                st.subheader(f"Edited ({filter_choice})")
                # Fix: Use use_container_width=True
                st.image(edited_image, use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Download Button
                st.subheader("Time to Share!")
                get_image_download_link(edited_image, "tofucat-masterpiece.png", "🎉 DOWNLOAD YOUR IMAGE!")

        except Exception as e:
            st.error(f"Whoops! Something went wrong while processing the image: {e}")
            st.info("Try a smaller PNG or JPG file.")
            
    else:
        st.info("☝️ Upload an image using the sidebar to start mixing and matching!")
        
        # --- Placeholder Image Section (Fix) ---
        st.header("Meet TofuCat! 😻")
        
        # Check if the placeholder file exists
        if os.path.exists(PLACEHOLDER_IMAGE_PATH):
            try:
                placeholder_img = Image.open(PLACEHOLDER_IMAGE_PATH)
                st.image(placeholder_img, caption="TofuCat Placeholder (Image courtesy of the user)", use_container_width=True)
            except Exception as e:
                st.warning(f"Could not load the local image '{PLACEHOLDER_IMAGE_PATH}'. Error: {e}")
        else:
            st.error(f"Placeholder image '{PLACEHOLDER_IMAGE_PATH}' not found! Please place the file in the same folder as the script.")
        

if __name__ == "__main__":
    main()