import streamlit as st
import requests
import time
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv

# Test the installation
print("dotenv installed successfully")

# Load environment variables
load_dotenv()

# Print all environment variables
print(dict(os.environ))

# Print specific API key
print("FLUX_API_KEY:", os.getenv('FLUX_API_KEY'))

# Get API key from environment variable
API_KEY = os.getenv("FLUX_API_KEY")
if not API_KEY:
    st.error("API key not found. Please set the FLUX_API_KEY environment variable.")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="Flux AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

def generate_images(prompt, width, height, num_images, model_params):
    image_urls = []  # List to store image URLs
    progress_text = st.empty()
    progress_bar = st.progress(0)

    for i in range(num_images):
        progress_text.text(f"Generating image {i+1} of {num_images}...")
        progress_bar.progress((i) / num_images)

        # Initial request to generate image
        response = requests.post(
            'https://api.bfl.ml/v1/flux-pro-1.1',
            headers={
                'accept': 'application/json',
                'x-key': API_KEY,
                'Content-Type': 'application/json',
            },
            json={
                'prompt': prompt,
                'width': width,
                'height': height,
                'num_outputs': 1,
                **model_params  # Include all model parameters
            },
        ).json()

        # Get request ID
        request_id = response.get("id")
        if not request_id:
            continue

        # Poll for results
        status_text = st.empty()
        while True:
            time.sleep(0.5)
            result = requests.get(
                'https://api.bfl.ml/v1/get_result',
                headers={
                    'accept': 'application/json',
                    'x-key': API_KEY,
                },
                params={
                    'id': request_id,
                },
            ).json()

            status = result.get("status")
            status_text.text(f"Status for image {i+1}: {status}")

            if status == "Ready":
                image_url = result['result']['sample']
                if image_url:
                    image_urls.append(image_url)
                break
            elif status == "Failed":
                st.error(f"Failed to generate image {i+1}")
                break

        progress_bar.progress((i + 1) / num_images)

    progress_text.text("All images generated!")
    progress_bar.progress(1.0)
    return image_urls

def main():
    st.markdown("<h1 class='title'>Flux - AI Image Generator 🎨</h1>", unsafe_allow_html=True)

    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            background-color: #FF4B4B;
            color: white;
        }
        .stButton>button:hover {
            background-color: #FF6B6B;
        }
        .title {
            text-align: left;
            color: #FF4B4B;
        }
        </style>
        """, unsafe_allow_html=True)

    # Sidebar for model parameters
    with st.sidebar:
        st.header("Model Parameters")
        show_advanced = st.checkbox("Show Advanced Settings", False)

        if show_advanced:
            st.subheader("Generation Settings")
            guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5, 0.5,
                                     help="Higher values make the output more closely match the prompt but may reduce quality")

            inference_steps = st.slider("Inference Steps", 20, 100, 50, 5,
                                      help="More steps generally create better images but take longer")

            st.subheader("Sampling Settings")
            scheduler = st.selectbox("Scheduler",
                                   ["DPM++ 2M Karras", "DPM++ 2M", "Euler", "Euler A"],
                                   help="Different schedulers produce different results")

            seed = st.number_input("Seed", -1, 2147483647, -1,
                                 help="Set a specific seed for reproducible results. -1 for random")

            st.subheader("Image Settings")
            negative_prompt = st.text_area("Negative Prompt", "",
                                         help="Specify what you don't want in the image")

            safety_checker = st.checkbox("Enable Safety Checker", True,
                                       help="Filter out NSFW content")

            model_params = {
                "guidance_scale": guidance_scale,
                "num_inference_steps": inference_steps,
                "scheduler": scheduler,
                "seed": seed if seed != -1 else None,
                "negative_prompt": negative_prompt if negative_prompt else None,
                "safety_checker": safety_checker
            }
        else:
            model_params = {}  # Use defaults if advanced settings are hidden


    prompt = st.text_area(
        "Enter your prompt:",
        height=100,
        placeholder="Describe the image you want to generate..."
    )


# Main content
    col1, col2, col3 = st.columns(3)
    with col1:
        width = st.number_input("Width", min_value=128, max_value=1024, value=1024, step=128)
    with col2:
        height = st.number_input("Height", min_value=128, max_value=1024, value=768, step=128)
    with col3:
        num_outputs = st.number_input("Number of Images", min_value=1, max_value=4, value=1)


    if st.button("🎨 Generate Images"):
        if not prompt:
            st.error("Please enter a prompt first!")
            return

        try:
            with st.spinner('🎨 Creating your masterpieces...'):
                start_time = time.time()

                # Generate images with all parameters
                image_urls = generate_images(prompt, width, height, num_outputs, model_params)

                if image_urls:
                    st.success("✨ Images generated successfully!")

                    # Create columns for displaying images
                    cols = st.columns(2)

                    # Display images in a grid
                    for idx, url in enumerate(image_urls):
                        # Get the image
                        image_response = requests.get(
                            url,
                            headers={
                                'accept': 'application/json',
                                'x-key': API_KEY,
                            }
                        )

                        if image_response.status_code == 200:
                            # Convert to PIL Image
                            image = Image.open(BytesIO(image_response.content))

                            # Display in appropriate column
                            with cols[idx % 2]:
                                st.image(image, caption=f"Generated Image {idx + 1}")
                                st.download_button(
                                    label=f"📥 Download Image {idx + 1}",
                                    data=image_response.content,
                                    file_name=f"generated_image_{idx + 1}.png",
                                    mime="image/png"
                                )

                end_time = time.time()
                st.metric("Total Generation Time", f"{end_time - start_time:.2f} seconds")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
        <p>Made with ❤️ by René Salmon</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
