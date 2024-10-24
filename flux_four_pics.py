import streamlit as st
import requests
import time
from io import BytesIO
from PIL import Image

# Get API key from Streamlit secrets
API_KEY = st.secrets["FLUX_API_KEY"]

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
                'x-key': API_KEY,  # Using secret API key
                'Content-Type': 'application/json',
            },
            json={
                'prompt': prompt,
                'width': width,
                'height': height,
                'num_outputs': 1,
                **model_params
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
                    'x-key': API_KEY,  # Using secret API key
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
    st.markdown("<h1 class='title'> Flux AI Image Generator 🎨</h1>", unsafe_allow_html=True)

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

    prompt = st.text_area(
        "Enter your prompt:",
        height=100,
        placeholder="Describe the image you want to generate..."
    )

    # Input controls
    col1, col2, col3 = st.columns(3)
    with col1:
        width = st.number_input("Width", min_value=128, max_value=1024, value=1024, step=128)
    with col2:
        height = st.number_input("Height", min_value=128, max_value=1024, value=768, step=128)
    with col3:
        num_outputs = st.number_input("Number of Images", min_value=1, max_value=4, value=1)

    if st.button("Generate Images 🖼️"):
        if not prompt:
            st.error("Please enter a prompt first!")
            return

        try:
            with st.spinner('Creating your masterpieces...'):
                start_time = time.time()

                # Generate images with user-specified parameters
                image_urls = generate_images(prompt, width, height, num_outputs, {})

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
                                'x-key': API_KEY,  # Using secret API key
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
