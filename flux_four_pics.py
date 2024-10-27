import streamlit as st
import requests
import time
from io import BytesIO
from PIL import Image
import base64

# Get API key from Streamlit secrets
API_KEY = st.secrets["FLUX_API_KEY"]

def generate_images(prompt, width, height, num_images, model_params):
    image_urls = []  # List to store image URLs
    progress_text = st.empty()
    progress_bar = st.progress(0)
    status_container = st.empty()

    for i in range(num_images):
        progress_text.text(f"Generating image {i+1} of {num_images}...")
        progress_bar.progress((i) / num_images)

        # Create a copy of model_params for each iteration
        current_params = model_params.copy()

        # If seed is -1 or not set, generate a unique seed for each image
        if 'seed' not in current_params or current_params['seed'] == -1:
            current_params['seed'] = int(time.time() * 1000) + i
        else:
            # If seed is set, increment it for each image to ensure variation
            current_params['seed'] = current_params['seed'] + i

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
                **current_params
            },
        ).json()

        # Get request ID
        request_id = response.get("id")
        if not request_id:
            continue

        # Poll for results
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
            status_container.text(f"Status for image {i+1}: {status}")

            if status == "Ready":
                image_url = result['result']['sample']
                if image_url:
                    image_urls.append(image_url)
                break
            elif status == "Failed":
                st.error(f"Failed to generate image {i+1}")
                break

        progress_bar.progress((i + 1) / num_images)

    progress_text.empty()
    progress_bar.empty()
    status_container.empty()
    return image_urls

def main():

    # Initialize default values
    seed_preset = None
    preset_scheduler = 'Standard-Produktion (DPM++ 2M)'  # Default value
    guidance_scale = 7.5  # Default value
    num_inference_steps = 50  # Default value
    seed = -1  # Default value

    # Update the preset dictionary with optimized parameters
# Update the preset dictionary with optimized parameters
    preset_params = {
        "01 | Folge strickt meinem Konzept in höchster Qualität": {
            "seed": 67890,
            "guidance_scale": 12.0,
            "num_inference_steps": 100,
            "scheduler": "Premium-Qualität (DPM++ 2M Karras)",
            "description": "Maximale Kontrolle über visuelle Identität",
            "num_outputs": 1
        },
        "02 | Folge meinem Konzept mit kontrollierten Variationen": {
            "seed": 12345,
            "guidance_scale": 7.5,
            "num_inference_steps": 50,
            "scheduler": "Standard-Produktion (DPM++ 2M)",
            "description": "Konsistente Basis mit kontrollierten Variationen",
            "num_outputs": 4
        },
        "03 | Findet kreative Ideen für mein Konzept": {
            "seed": -1,
            "guidance_scale": 3.0,
            "num_inference_steps": 30,
            "scheduler": "Kreativ-Exploration (Euler A)",
            "description": "Maximale kreative Freiheit für neue Ideen",
            "num_outputs": 4
        }
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
         /* Add this to your existing CSS styles */
        /* Add this to your existing CSS styles */
        .download-button {
            width: 100%;
            height: 50px;
            background-color: transparent;
            color: white;
            border-radius: 4px;
            border: 1px solid #757575;
            padding: 8px 16px;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 20px auto;
        }

        .download-button:hover {
            background-color: rgba(158, 158, 158, 0.1);
            border-color: #9e9e9e;
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
        }

        .center-content {
            display: flex;
            justify-content: center;
            width: 100%;
            margin: 20px 0;
        }

        </style>
    """, unsafe_allow_html=True)


    prompt = st.text_area(
        "Bildkonzept:",
        height=200,
        placeholder="Beschreibe dein Bild..."
    )

    # First selectbox (Ziel des Bildes)
    seed_preset = st.selectbox(
        "Modus:",
        options=list(preset_params.keys()),
        help="Wähle eine vordefinierten Modus für deine Marketingziele",
        key="preset_selector"
    )

    # Get the selected preset parameters
    selected_preset = preset_params[seed_preset] if seed_preset else preset_params[list(preset_params.keys())[0]]

    # Input controls
    col1, col2, col3 = st.columns(3)
    with col1:
        width = st.number_input("Breite", min_value=128, max_value=1024, value=1024, step=128)

    with col2:
        height = st.number_input("Höhe", min_value=128, max_value=1024, value=768, step=128)

    with col3:
        num_outputs = st.number_input(
            "Anzahl Varianten",
            min_value=1,
            max_value=4,
            value=selected_preset["num_outputs"],
            key=f"num_outputs_{seed_preset}"
        )

    # Update model parameters
    model_params = {
        "seed": selected_preset["seed"],
        "guidance_scale": selected_preset["guidance_scale"],
        "num_inference_steps": selected_preset["num_inference_steps"],
        "scheduler": selected_preset["scheduler"].split(" (")[0],
        "num_outputs": selected_preset["num_outputs"]
    }

    if st.button("✨Bilder generieren✨"):
        if not prompt:
            st.error("Please enter a prompt first!")
            return

        try:
            with st.spinner('Creating your masterpieces...'):
                start_time = time.time()

                # Get the selected preset parameters
                if seed_preset:
                    selected_preset = preset_params[seed_preset]

                    # Create model parameters dictionary with all settings
                    model_params = {
                        "seed": selected_preset["seed"] if selected_preset["seed"] == -1 else int(time.time()),  # New seed each time unless random
                        "guidance_scale": selected_preset["guidance_scale"],
                        "num_inference_steps": selected_preset["num_inference_steps"],
                        "scheduler": selected_preset["scheduler"].split(" (")[0]
                    }
                else:
                    # Default parameters if no preset is selected
                    model_params = {
                        "seed": int(time.time()),  # Generate new seed each time
                        "guidance_scale": 7.5,
                        "num_inference_steps": 50,
                        "scheduler": "Standard-Produktion (DPM++ 2M)"
                    }

                # Generate images with the complete model_params
                image_urls = generate_images(prompt, width, height, num_outputs, model_params)

                if image_urls:
                    st.success("✨ Bilder erfolgreich generiert!")
                    # ... rest of the code remains the same ...

                    # Store all images data
                    all_images_data = []

                    # Process and display images
                    for idx, url in enumerate(image_urls):
                        image_response = requests.get(
                            url,
                            headers={
                                'accept': 'application/json',
                                'x-key': API_KEY,
                            }
                        )

                        if image_response.status_code == 200:
                            # Store image data
                            all_images_data.append(image_response.content)

                            # Convert to PIL Image for display
                            image = Image.open(BytesIO(image_response.content))

                            # Display image with full column width
                            st.image(
                                image,
                                caption=f"Generiertes Bild {idx + 1}",
                                use_column_width="always"
                            )

                    # Create centered container for single download button
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        # Create a ZIP in memory
                        import io
                        import zipfile

                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for idx, img_data in enumerate(all_images_data):
                                zip_file.writestr(f"generated_image_{idx + 1}.png", img_data)

                        # Add single download button for ZIP file
                        st.download_button(
                            label="Bilder herunterladen",
                            data=zip_buffer.getvalue(),
                            file_name="generated_images.zip",
                            mime="application/zip",
                            key=f"download_all_{time.time()}",  # Unique key using timestamp
                            use_container_width=True
                        )


                        # Add generation time
                        st.markdown(
                            f'<p style="color: #757575; text-align: center;">Generierungszeit: {(time.time() - start_time):.2f} Sekunden</p>',
                            unsafe_allow_html=True
                        )
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

        # Update the parameters based on selected preset
        if seed_preset:
            selected_preset = preset_params[seed_preset]
            preset_seed = selected_preset["seed"]
            preset_guidance = selected_preset["guidance_scale"]
            preset_steps = selected_preset["num_inference_steps"]
            preset_scheduler = selected_preset["scheduler"]
            num_outputs = selected_preset["num_outputs"]
        else:
            # Use default values if no preset is selected
            num_outputs = 1
            preset_seed = -1
            preset_guidance = 7.5
            preset_steps = 50
            preset_scheduler = "Premium-Qualität (DPM++ 2M Karras)"

        # Now use the preset values in your inputs
        scheduler = st.selectbox(
            "Bildwiedergabe Optionen",
            options=["Premium-Qualität (DPM++ 2M Karras)",
                    "Standard-Produktion (DPM++ 2M)",
                    "Schnellvorschau (Euler)",
                    "Kreativ-Exploration (Euler A)"],
            index=["Premium-Qualität (DPM++ 2M Karras)",
                "Standard-Produktion (DPM++ 2M)",
                "Schnellvorschau (Euler)",
                "Kreativ-Exploration (Euler A)"].index(preset_scheduler),
            help="Wählen Sie die Rendering-Qualität entsprechend Ihres Workflows",
            key="scheduler_selector"
        )

        guidance_scale = st.slider(
            "Beachtung deiner Vorgaben",
            min_value=1.0,
            max_value=20.0,
            value=preset_guidance,
            step=0.5,
            help="Niedrig: Maximale kreative Freiheit | Hoch: Strikte Vorgabentreue"
        )

        num_inference_steps = st.slider(
            "Detailgenauigkeit",
            min_value=20,
            max_value=100,
            value=preset_steps,
            step=5,
            help="Niedrig: Schnelle Vorschau (20) | Standard: Produktionsqualität (30) | Premium: Maximale Details (50+)"
        )

        # Update seed input to use preset value
        seed = st.number_input(
            "Reproduzierbarkeit",
            min_value=-1,
            max_value=2147483647,
            value=preset_seed,
            help="Zufällige Generierung (Seed = -1) für kreative Exploration. Feste Seed-Werte für reproduzierbare Ergebnisse",
            key="seed_input"  # Add unique key
        )

        # Update the model parameters when generating images
        # Update the model parameters
        model_params = {
                "seed": seed,
                "guidance_scale": guidance_scale,
                "num_inference_steps": num_inference_steps,
                "scheduler": scheduler.split(" (")[0]
        }

        # Add parameter descriptions directly without nested expander
        # Add this markdown section after the seed_preset selectbox or in the expander section
        st.markdown("""
            <div style="color: #ffffff; background-color: #424242; padding: 15px; border-radius: 4px; border: 1px solid #616161;">
            <h4 style="color: #ffffff; margin-bottom: 10px; font-weight: 500;">Modus - Voreinstellungen</h4>

            <p style="color: #bdbdbd;">
                <strong style="color: #ffffff;">Folge strikt meinem Konzept in höchster Qualität</strong>
                <ul style="margin-left: 20px; color: #bdbdbd;">
                    <li>Maximale Kontrolle über visuelle Identität</li>
                    <li>Präzise Einhaltung von Markenrichtlinien</li>
                    <li>Ideal für: Kundenaufträge, Corporate Design, Markenkommunikation</li>
                    <li>Technisch: Fester Seed (67890), hohe Markentreue</li>
                </ul>
            </p>

            <p style="color: #bdbdbd;">
                <strong style="color: #ffffff;">Folge meinem Konzept mit kontrollierten Variationen</strong>
                <ul style="margin-left: 20px; color: #bdbdbd;">
                    <li>Konsistente Basis mit kontrollierten Variationen</li>
                    <li>Reproduzierbare Ergebnisse für A/B-Tests</li>
                    <li>Ideal für: Kampagnen-Rollout, Content-Serien, Social Media</li>
                    <li>Technisch: Fester Seed (12345), mittlere Markentreue</li>
                </ul>
            </p>

            <p style="color: #bdbdbd;">
                <strong style="color: #ffffff;">Findet kreative Ideen für mein Konzept</strong>
                <ul style="margin-left: 20px; color: #bdbdbd;">
                    <li>Maximale kreative Freiheit für neue Ideen</li>
                    <li>Zufällige Ergebnisse für Inspiration</li>
                    <li>Ideal für: Konzeptfindung, Moodboards, erste Entwürfe</li>
                    <li>Technisch: Zufälliger Seed (-1), niedrige Markentreue</li>
                </ul>
            </p>

            <p style="color: #bdbdbd; margin-top: 15px;">
                <strong style="color: #ffffff;">Anwendung:</strong>
                <ul style="margin-left: 20px; color: #bdbdbd;">
                    <li>Kreativität vs. Kontrolle</li>
                    <li>Variation vs. Konsistenz</li>
                    <li>Experimentell vs. Markentreu</li>
                </ul>
                Wählen Sie die Voreinstellung entsprechend Ihres Projektziels. Die Parameter werden automatisch optimiert für die Balance zwischen diesen Faktoren.
            </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="color: #ffffff; background-color: #424242; padding: 15px; border-radius: 4px; border: 1px solid #616161;">
            <h4 style="color: #ffffff; margin-bottom: 10px; font-weight: 500;">Workflow-Optionen</h4>

            <p style="color: #bdbdbd;">
                <strong style="color: #ffffff;">Bachtung deiner Vorgaben:</strong>
                Steuert die Balance zwischen kreativer Freiheit und Prompt-Treue. Höhere Werte erzeugen Bilder, die enger an Ihrer Beschreibung bleiben, können aber weniger kreativ wirken.
            </p>

            <p style="color: #bdbdbd;">
                <strong style="color: #ffffff;">Bildwiedergabe Optionen:</strong>
                Verschiedene Algorithmen für unterschiedliche Anwendungsfälle:
            </p>
            <ul style="margin-left: 20px; color: #bdbdbd;">
                <li><strong style="color: #ffffff;">Premium-Qualität:</strong> Beste Gesamtqualität für finale Präsentationen</li>
                <li><strong style="color: #ffffff;">Standard-Produktion:</strong> Ausgewogenes Verhältnis zwischen Geschwindigkeit und Qualität</li>
                <li><strong style="color: #ffffff;">Schnellvorschau:</strong> Schnelle Generierung für Konzeptphase</li>
                <li><strong style="color: #ffffff;">Kreativ-Exploration:</strong> Maximale kreative Interpretation</li>
            </ul>
            </p>
            <p style="color: #bdbdbd;">
                <strong style="color: #ffffff;">Detailgenauigkeit:</strong>
                Bestimmt die Feinheit der Ausarbeitung. Mehr Details bedeuten bessere Qualität, aber längere Generierungszeit:
                <ul style="margin-left: 20px; color: #bdbdbd;">
                    <li><strong style="color: #ffffff;">Entwurf (20):</strong> Schnelle Konzeptvisualisierung</li>
                    <li><strong style="color: #ffffff;">Standard (30):</strong> Ausgewogene Produktionsqualität</li>
                    <li><strong style="color: #ffffff;">Premium (50+):</strong> Maximale Detailtiefe</li>
                </ul>
            </p>

            <p style="color: #bdbdbd;">
                <strong style="color: #ffffff;">Workflow-Voreinstellungen:</strong>
                Optimierte Einstellungskombinationen für verschiedene Anwendungsfälle:
            </p>
            <ul style="margin-left: 20px; color: #bdbdbd;">
                <li><strong style="color: #ffffff;">Kreativ-Exploration:</strong> Maximale Freiheit für Ideenfindung und Brainstorming</li>
                <li><strong style="color: #ffffff;">Kampagnen-Erstellung:</strong> Ideal für konsistente Variationen eines Konzepts</li>
                <li><strong style="color: #ffffff;">Marken-Bilderwelt:</strong> Strikte Einhaltung von Markenrichtlinien</li>
            </ul>
            </p>
            <p style="color: #bdbdbd;">
                <strong style="color: #ffffff;">Ausschlusskriterien:</strong>
                Definition unerwünschter Elemente zur Wahrung der Markensicherheit und CI-Konformität.
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
