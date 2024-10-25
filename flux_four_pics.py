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


    # Add the seed presets dictionary right before the seed input
    preset_seeds = {
        "Kreativ-Exploration: Brainstorming & Ideation": -1,
        "Kampagnen-Erstellung: Ein Konzept, Multiple Varianten": 12345,
        "Konsistente Marken-Bilderwelt: Stricktes folgen der Guidelines": 67890

    }

    st.markdown("<h1 class='title'>AI Image Generator | Flux 1.1 Pro </h1>", unsafe_allow_html=True)

   # Custom CSS with Material Design grey and black theme
    st.markdown("""
        <style>

        .title {
        text-align: left;
        color: #757575;  /* Material Grey 900 - darkest grey */
        font-weight: 500;  /* Medium weight for better visibility */
        font-size: 24px
        }

        /* Main background */
        .stApp {
            background-color: #212121;
            color: #ffffff;
        }

        /* Expander */
        .streamlit-expanderHeader {
            background-color: transparent;
            color: #ffffff;
            border-radius: 4px;
            padding: 8px;
        }

        .streamlit-expanderHeader:hover {
            color: #ffffff;  /* Bright white text on hover */
            border-color: #9e9e9e;  /* Lighter border on hover */
            background-color: rgba(158, 158, 158, 0.1);  /* Very subtle grey background */

        }

        .streamlit-expanderContent {
            color: #ffffff;  /* Bright white text on hover */
            border-color: #9e9e9e;  /* Lighter border on hover */
            background-color: rgba(158, 158, 158, 0.1);  /* Very subtle grey background */

        }

        /* Input fields and controls */
        .stTextInput>div>div>input {
            background-color: #424242;
            color: #ffffff;
            border: 1px solid #616161;
        }

        .stSlider>div>div>div {
            background-color: #757575;
        }

        .stSelectbox>div>div {
            background-color: transparent;
            color: #ffffff;
            border: 1px solid #616161;
        }

        /* Custom classes */
        .parameter-title {
            color: #ffffff;
            font-size: 14px;
            font-weight: 500;
        }

        .parameter-help {
            color: #bdbdbd;
            font-size: 12px;
        }

        /* Button styling */
        .stButton>button {
            background-color: #757575;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
        }

        .stButton>button:hover {
            background-color: transparent;
            border: 1px solid #757575;
        }
        div.stButton > button {
            width: 100%;
            height: 50px;
            background-color: transparent;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 8px 16px;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
            text-transform: uppercase;  /* Optional: makes text uppercase */
            letter-spacing: 1px;  /* Optional: spaces out the text */
        }
        div.stButton > button:hover {
                color: #ffffff;  /* Bright white text on hover */
                border-color: #9e9e9e;  /* Lighter border on hover */
                background-color: rgba(158, 158, 158, 0.1);  /* Very subtle grey background */
                text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);  /* Subtle glow effect */
        }
        .button-container {
            padding: 10px 0;
            margin: 100px 0;
        }
        </style>
    """, unsafe_allow_html=True)



    prompt = st.text_area(
        "Bildkonzept:",
        height=200,
        placeholder="Beschreibe dein Bild..."
    )

    # Add preset selector before the seed input
    seed_preset = st.selectbox(
        "Ziel der Bildes",
        options=list(preset_seeds.keys()),
        help="Wählen Sie einen vordefinierten Modus für Ihre Marketingziele"
        )

    # Input controls (make sure this is at the same indentation level as other main content)
    col1, col2, col3= st.columns(3)
    with col1:
        width = st.number_input("Breite", min_value=128, max_value=1024, value=1024, step=128)

    with col2:
        height = st.number_input("Höhe", min_value=128, max_value=1024, value=768, step=128)

    with col3:
        num_outputs = st.number_input("Anzahl Varianten", min_value=1, max_value=4, value=1)


    if st.button("✨Bild generieren✨"):
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

    #st.markdown("### 🛠️ Fine-tune Model Like a Pro")
    with st.expander("Details einstellen", expanded=False):
        # Add a container with custom styling
        st.markdown("""
            <style>
            .advanced-settings {
                color: #ffffff;  /* Bright white text on hover */
                border-color: #9e9e9e;  /* Lighter border on hover */
                background-color: rgba(158, 158, 158, 0.1);  /* Very subtle grey background */
                text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);  /* Subtle glow effect */
            }
            .parameter-title {
                color: #424242;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 8px;
            }
            .parameter-help {
                color: #757575;
                font-size: 12px;
            }
            </style>
            """, unsafe_allow_html=True)

        col_tune1, col_tune2 = st.columns(2)

        with col_tune1:
            scheduler = st.selectbox(
                        "Bildwiedergabe Optionen",
                        options=["Premium-Qualität (DPM++ 2M Karras)",
                        "Standard-Produktion (DPM++ 2M)",
                        "Schnellvorschau (Euler)",
                        "Kreativ-Exploration (Euler A)"],
                        index=0,
                        help="Wählen Sie die Rendering-Qualität entsprechend Ihres Workflows"
                    )

            guidance_scale = st.slider(
                "Gestaltungsfreiheit",
                min_value=1.0,
                max_value=20.0,
                value=7.5,
                step=0.5,
                help="Niedrig: Maximale kreative Freiheit | Hoch: Strikte Markentreue"
            )

            num_inference_steps = st.slider(
                "Detailgenauigkeit",
                min_value=20,
                max_value=100,
                value=50,
                step=5,
                help="Niedrig: Schnelle Vorschau (20) | Standard: Produktionsqualität (30) | Premium: Maximale Details (50+)"
            )


            # Update seed value based on preset
            if seed_preset:
                preset_seed = preset_seeds[seed_preset]
            else:
                preset_seed = -1

            # Modified seed input to use preset value
            seed = st.number_input(
                "Reproduzierbarkeit",
                min_value=-1,
                max_value=2147483647,
                value=preset_seed,
                help="Setzen Sie einen spezifischen Wert für wiederholbare Ergebnisse. -1 für zufällige Generierung"
            )
            safety_checker = st.checkbox(
                "Sicherheits-Filter aktiv",
                value=True,
                help="Filter out NSFW content"
            )
        with col_tune2:
            negative_prompt = st.text_area(
                "Ausschlusskriterien",
                placeholder="Definieren Sie unerwünschte Elemente, Stilkonflikte...",
                help="Markensicherheit & Ausschlüsse",
                height=200
            )
        # Add separator with material design style
        st.markdown("""
            <div style="
                height: 1px;
                background: linear-gradient(to right, #424242, #757575, #424242);
                margin: 20px 0;
            "></div>
            """, unsafe_allow_html=True)

        # Add parameter descriptions directly without nested expander
        st.markdown("""
            <div style="color: #ffffff; background-color: #424242; padding: 15px; border-radius: 4px; border: 1px solid #616161;">
            <h4 style="color: #ffffff; margin-bottom: 10px; font-weight: 500;">Workflow-Voreinstellungen</h4>

            <p style="color: #bdbdbd;">
            <strong style="color: #ffffff;">Schnellkonzept:</strong>
            Ideal für erste Entwürfe und Ideenfindung
            - Niedrige Markentreue
            - Schnellvorschau
            - 20 Verfeinerungsschritte
            </p>

            <p style="color: #bdbdbd;">
            <strong style="color: #ffffff;">Reproduzierbarkeit:</strong>
            Ein Werkzeug für konsistente Kampagnen. Verwenden Sie den gleichen Wert, um identische Bilder zu generieren - ideal für:
            • A/B-Testing von Werbekampagnen
            • Konsistente Markenbildsprache
            • Iterative Designprozesse
            </p>

            <p style="color: #bdbdbd;">
            <strong style="color: #ffffff;">Produktionsstandard:</strong>
            Ausgewogene Einstellungen für die tägliche Produktion
            - Mittlere Markentreue
            - Standard-Produktion
            - 30 Verfeinerungsschritte
            </p>

             <p style="color: #bdbdbd;">
            <strong style="color: #ffffff;">Kundenpräsentation:</strong>
            Höchste Qualität für finale Präsentationen
            - Hohe Markentreue
            - Premium-Qualität
            - 40+ Verfeinerungsschritte
            </p>
            </div>
            """, unsafe_allow_html=True)


    st.markdown(
        """
        <div style='text-align: center'>
        <p style="color: #bdbdbd;">
        <p>Made with ❤️ by René Salmon</p>


        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
