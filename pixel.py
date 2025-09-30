import streamlit as st
import numpy as np
from PIL import Image
from io import BytesIO
import base64 
import json # Need for creating the initial_drawing structure
from streamlit_drawable_canvas import st_canvas
import os # Added for file checking (optional, but good practice)

# --- Configuration and Initialization ---
st.set_page_config(
    page_title="Interactive Pixel Art Editor",
    page_icon="🎨",
    layout="wide"
)

# Constants for the canvas component display
CANVAS_DISPLAY_SIZE = 512 # The fixed width/height of the canvas in the UI

# Initialize Session State
if 'canvas_size' not in st.session_state:
    st.session_state.canvas_size = 16
if 'canvas_data' not in st.session_state:
    # Initialize as an array of 255 (white)
    st.session_state.canvas_data = np.full((16, 16, 3), 255, dtype=np.uint8)
if 'message' not in st.session_state:
    st.session_state.message = "Click the 'Apply Size / Import Image' button to start or load an image!"

# --- Custom CSS for Vibrant UI/UX ---
st.markdown("""
<style>
/* Main App Background and Font */
.stApp {
    background-color: #F0F8FF; /* Light Azure Background */
    color: #4B0082; /* Indigo/Violet Text */
    font-family: 'Arial', sans-serif; 
}

/* Header and Title */
h1 {
    color: #FF6347; /* Tomato Red */
    text-shadow: 2px 2px 4px #00000030;
    border-bottom: 3px solid #FFD700; /* Gold Line */
    padding-bottom: 5px;
}
h2, h3 {
    color: #4682B4; /* Steel Blue */
}

/* Sidebar Customization */
.css-1d391kg { /* Sidebar background */
    background-color: #B0E0E6; /* Powder Blue */
}
.sidebar .sidebar-content {
    color: #000080; /* Navy Text */
}

/* Download Button Styling (Making it stand out) */
.stDownloadButton>button {
    background-color: #3CB371; /* Medium Sea Green */
    color: white;
    border-radius: 10px;
    border: 0px;
    padding: 15px 30px;
    font-size: 1.1rem;
    font-weight: bold;
    box-shadow: 0 4px #2E8B57; 
    transition: all 0.1s;
}
.stDownloadButton>button:hover {
    background-color: #43CD80; 
    box-shadow: 0 2px #2E8B57;
    transform: translateY(2px); 
}

/* Info/Success Boxes */
div[data-testid="stAlert"] {
    border-radius: 10px;
    font-weight: bold;
}
.stRadio > label {
    font-weight: bold;
    color: #4682B4;
}
/* Thumbnail styling for a cleaner look */
.stImage > img {
    border: 2px solid #DDDDDD;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---

def rgb_to_hex(rgb_array: np.ndarray) -> str:
    """Converts a NumPy RGB array [R, G, B] to a hex string."""
    r, g, b = int(rgb_array[0]), int(rgb_array[1]), int(rgb_array[2])
    return f'#{r:02x}{g:02x}{b:02x}'

def create_initial_drawing_json(canvas_data: np.ndarray, display_size: int) -> dict:
    """
    Creates the JSON structure required by st_canvas to pre-populate the grid.
    """
    size = canvas_data.shape[0]
    pixel_size = display_size / size
    
    objects = []
    
    for y in range(size):
        for x in range(size):
            rgb = canvas_data[y, x]
            hex_color = rgb_to_hex(rgb)
            
            rect = {
                "type": "rect",
                "left": x * pixel_size,
                "top": y * pixel_size,
                "width": pixel_size,
                "height": pixel_size,
                "fill": hex_color,
                "stroke": "#DDDDDD", # Light border for the grid lines
                "strokeWidth": 1,
                "selectable": False,
                "evented": False, 
            }
            objects.append(rect)
            
    return {"objects": objects, "background": "#FFFFFF"}

def apply_pixelation(img: Image.Image, size: int) -> np.ndarray:
    """Resizes an image using NEAREST neighbor to achieve the pixelation effect."""
    img_small = img.resize((size, size), Image.Resampling.NEAREST)
    return np.array(img_small)

def get_image_download_link(img_array: np.ndarray, filename: str, text: str):
    """Creates a download button for the processed pixel art."""
    img = Image.fromarray(img_array, 'RGB')
    buf = BytesIO()
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

    col_controls, col_canvas = st.columns([1, 2])

    with col_controls:
        st.header("⚙️ Controls")

        # 1. Color Palette/Picker
        st.subheader("Current Brush Color")
        current_color_hex = st.color_picker(
            "Pick a color for the brush", 
            "#32A852", 
            key='current_color_hex'
        )
        st.markdown(f"**Selected:** <span style='color:{current_color_hex}; font-weight:bold;'>{current_color_hex}</span>", unsafe_allow_html=True)
        st.markdown("---")
        
        # 2. Tool Selector (Draw or Eraser)
        st.subheader("Drawing Tool")
        
        tool_mode = st.radio(
            "Select Tool", 
            ('Draw', 'Eraser'),
            key='tool_mode',
            horizontal=True
        )
        
        if tool_mode == 'Eraser':
            brush_color_for_canvas = "#FFFFFF" 
            st.warning("Eraser selected! Clicks will turn pixels white.")
        else:
            brush_color_for_canvas = current_color_hex
        
        st.markdown("---")

        # 3. Image Upload / Pixelation / Size Control
        st.subheader("Canvas Size & Import")
        
        uploaded_file = st.file_uploader(
            "Upload an image to pixelate", 
            type=["png", "jpg", "jpeg"]
        )
        
        new_size = st.number_input(
            "Canvas Size (N x N)", 
            min_value=8, 
            max_value=64, 
            value=st.session_state.canvas_size, 
            step=4,
            key='size_input'
        )
        
        if st.button("🖼️ Apply Size / Import Image", key="apply_size_btn"):
            if new_size != st.session_state.canvas_size:
                st.session_state.canvas_size = new_size
            
            if uploaded_file is not None:
                try:
                    img = Image.open(uploaded_file).convert("RGB")
                    st.session_state.canvas_data = apply_pixelation(img, st.session_state.canvas_size)
                    st.session_state.message = f"Image imported and pixelated to {st.session_state.canvas_size}x{st.session_state.canvas_size}."
                except Exception as e:
                    st.error(f"Error loading image: {e}")
            else:
                st.session_state.canvas_data = np.full(
                    (st.session_state.canvas_size, st.session_state.canvas_size, 3), 
                    255, dtype=np.uint8
                )
                st.session_state.message = f"Created a blank {st.session_state.canvas_size}x{st.session_state.canvas_size} canvas."
                
            st.rerun() 
                
        if st.button("🗑️ Reset Canvas to White", key="reset_btn"):
            st.session_state.canvas_data = np.full(
                (st.session_state.canvas_size, st.session_state.canvas_size, 3), 
                255, dtype=np.uint8
            )
            st.session_state.message = "Canvas reset to white!"
            st.rerun() 

    with col_canvas:
        st.header("🖼️ Your Interactive Canvas")
        st.success(st.session_state.message)
        
        # --- Interactive Canvas Setup ---
        
        pixel_size = CANVAS_DISPLAY_SIZE / st.session_state.canvas_size

        initial_drawing = create_initial_drawing_json(st.session_state.canvas_data, CANVAS_DISPLAY_SIZE)

        canvas_result = st_canvas(
            fill_color=brush_color_for_canvas, 
            stroke_width=pixel_size, 
            stroke_color=brush_color_for_canvas, 
            
            background_color="#FFFFFF", 
            initial_drawing=initial_drawing, 
            
            update_streamlit=True,
            height=CANVAS_DISPLAY_SIZE,
            width=CANVAS_DISPLAY_SIZE,
            drawing_mode="rect", 
            key="canvas_component"
        )
        
        # --- Logic to Extract and Update Canvas Data ---
        
        if canvas_result.json_data is not None and canvas_result.json_data['objects']:
            
            new_data = np.full((st.session_state.canvas_size, st.session_state.canvas_size, 3), 255, dtype=np.uint8)
            
            for obj in canvas_result.json_data['objects']:
                if obj['type'] == 'rect':
                    x_coord = int(obj['left'] / pixel_size)
                    y_coord = int(obj['top'] / pixel_size)
                    
                    hex_color = obj['fill']
                    rgb = np.array([int(hex_color[i:i+2], 16) for i in (1, 3, 5)], dtype=np.uint8)
                    
                    if 0 <= y_coord < st.session_state.canvas_size and 0 <= x_coord < st.session_state.canvas_size:
                        new_data[y_coord, x_coord] = rgb

            if not np.array_equal(new_data, st.session_state.canvas_data):
                st.session_state.canvas_data = new_data
                action = "Erased" if tool_mode == 'Eraser' else "Drew"
                st.session_state.message = f"{action} pixel(s) on the canvas."
                st.rerun() 

        st.markdown("---")
        
        # 4. Download
        st.subheader("Export")
        get_image_download_link(
            st.session_state.canvas_data, 
            f"pixel_art_interactive_{st.session_state.canvas_size}x{st.session_state.canvas_size}.png", 
            "🎉 DOWNLOAD PIXEL ART PNG"
        )
    
    # --- NEW SECTION: THUMBNAILS AT THE BOTTOM ---
    st.markdown("---") # Separator line
    st.subheader("App Files Showcase (Thumbnails)")

    THUMBNAIL_WIDTH = 150 # Define the size for the thumbnails

    # Create columns: 150px for each image, then a large spacer
    thumb_col1, thumb_col2, _ = st.columns([THUMBNAIL_WIDTH, THUMBNAIL_WIDTH, 5]) 

    # Display tofu.jpg
    with thumb_col1:
        if os.path.exists("tofu.jpg"):
            st.image("tofu.jpg", caption="App File: tofu.jpg", width=THUMBNAIL_WIDTH)
        else:
            st.error("tofu.jpg not found in directory.")

    # Display tofucat.png
    with thumb_col2:
        if os.path.exists("tofucat.png"):
            st.image("tofucat.png", caption="App File: tofucat.png", width=THUMBNAIL_WIDTH)
        else:
            st.error("tofucat.png not found in directory.")


if __name__ == "__main__":
    main()