import streamlit as st
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import os, sys

# Specify the virtual environment path so that it can look up google.generativeai
venv_path = os.path.join(os.path.dirname(__file__), '.venv', 'lib', 'site-packages')
# print(f'venv_path: {venv_path}')
sys.path.append(venv_path)


import google
import google.generativeai as genai

# input variables to genai
image = None
prompt = ""
llm_response = ""
use_custom_prompt = False
custom_prompt = ""

# Methods
def on_calculate_clicked():
    try:
        generation_config = {
            "temperature": 0,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE",
        },
        ]

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
        
        chat_session = model.start_chat()

        prompt = custom_prompt if use_custom_prompt else st.session_state['prompt']

        response = chat_session.send_message([prompt, image])

        print(response)

        llm_response = response.candidates[0].content.parts[0].text

        st.session_state.update({ "llm_response": llm_response })
    except google.api_core.exceptions.InvalidArgument as e:
        st.session_state.update({ "error": e.message })
        print(st.session_state["error"])


def on_api_key_changed():
    st.session_state["is_genai_configured"] = False
    if "error" in st.session_state:
        del st.session_state["error"]


def sentence_joiner(parts: list[str], delimiter = ", ") -> str:
    """ Given [a, b, c] return 'a, b and c' """
    if len(parts) == 0:
        return ""
    elif len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        all_but_last = parts[:-1]
        return delimiter.join(all_but_last) + " and " + parts[-1]


def build_prompt(params_dict):
    what_inclusions = []
    area_inclusions = []

    what_to_paint = params_dict["what"]
    areas_to_paint = params_dict["areas"]

    wall_height = params_dict["wall_height"]
    door_height = params_dict["door_height"]
    door_width = params_dict["door_width"]

    if what_to_paint['paint_ceiling']:
        what_inclusions.append("ceiling")

    if what_to_paint['paint_walls']:
        what_inclusions.append("walls")

    if what_to_paint['paint_doors']:
        what_inclusions.append("doors")

    if areas_to_paint['paint_bedrooms']:
        area_inclusions.append("bedrooms")

    if areas_to_paint['paint_dining_lounge_room']:
        area_inclusions.append("dining/lounge room")

    if areas_to_paint['paint_bathrooms']:
        area_inclusions.append("bathroom")

    if areas_to_paint['paint_kitchen']:
        area_inclusions.append("kitchen")
    
    door_hint = f"Assume that door height is {door_height}mm and width is {door_width}mm. Both sides of the door need to be painted." \
            if what_to_paint['paint_doors'] else ""

    prompt = f"""I want to paint the interior {sentence_joiner(what_inclusions)} of the house, including {sentence_joiner(area_inclusions)}.
Ceilings use one type of paint.
Walls use another type of paint.
Doors use another type of paint.

Assume that wall height is {wall_height}m. 
{door_hint}
I need to paint {num_coats} coats for everything.

Assume 1 litre of paint covers 10sqm for all types of paint.
Provide breakdown of the amount of paint required for each of {sentence_joiner(what_inclusions)}.
Calculate the total amount of paint required for each of {sentence_joiner(what_inclusions)}.
"""
    
    # Calculate the total amount of paint required.

    return prompt


# UI
st.header("DIY Paint Estimator")
with st.sidebar as sb:
    st.subheader("Gemini API Key")
    
    is_genai_configured = False
    gemini_api_key = st.text_input("Please enter Google Gemini API Key", key="gemini_api_key", type="password", on_change=on_api_key_changed)
    if not gemini_api_key:
        load_dotenv()
        gemini_api_key = os.environ["GEMINI_API_KEY"]

    if not is_genai_configured:
        genai.configure(api_key=gemini_api_key)
        is_genai_configured = True

    
    # Input controls
    uploaded_file = st.file_uploader("Upload Floorplans",
                                      type=['png', 'jpg', 'jpeg', 'gif'],
                                      accept_multiple_files=False,
                                      key="id_fileuploader",
                                      on_change=None)
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_stream = BytesIO(bytes_data)
        image = Image.open(image_stream)

        st.subheader("Choose what to paint")
        paint_walls = st.checkbox("Walls", value=True)
        paint_ceiling = st.checkbox("Ceiling")
        paint_doors = st.checkbox("Doors")
        
        st.subheader("Choose area to paint")
        paint_dining_lounge_room = st.checkbox("Dining/Lounge Room", value=True)
        paint_bedrooms = st.checkbox("Bedrooms", value=True)
        paint_kitchen = st.checkbox("Kitchen",  value=False)
        paint_bathrooms = st.checkbox("Bathrooms/Toilets", value=False)
        surfaces = [paint_bathrooms, paint_bedrooms, paint_kitchen, paint_walls, paint_ceiling, paint_doors]
        has_at_least_one_surface = any(surfaces)
        if not has_at_least_one_surface:
            error_message = "At least one area is required"
            st.markdown(f"<span style='color:red'>{error_message}</span>", unsafe_allow_html=True)

        num_coats = st.slider("How many coats?", min_value=1, max_value=3, value=2, step=1)
        wall_height = st.number_input("Wall height (m)", value=2.5)
        if paint_doors:
            door_height = st.number_input("Door height (mm)", value=2048)
            door_width = st.number_input("Door width (mm)", value=820)
        else:
            # Use defaults
            door_height = 2048
            door_width = 820

        params = {
            "what": {
                "paint_walls": paint_walls,
                "paint_ceiling": paint_ceiling,
                "paint_doors": paint_doors,
            },
            "areas": {
                "paint_bedrooms": paint_bedrooms,
                "paint_kitchen": paint_kitchen,
                "paint_bathrooms": paint_bathrooms,
                "paint_dining_lounge_room": paint_dining_lounge_room
            },
            "num_coats": num_coats,
            "wall_height": wall_height,
            "door_height": door_height,
            "door_width": door_width
        }
        prompt = build_prompt(params)
        st.session_state.update({ "prompt": prompt })

        use_custom_prompt = st.checkbox("Use custom prompt")
        if use_custom_prompt:
            custom_prompt = st.text_area("Custom prompt", height=200)
        
        st.button("Calculate", disabled=not has_at_least_one_surface, on_click=on_calculate_clicked)
        


if image is not None:
    st.image(image=image)

    with st.container():
        # Error message (if any)
        if "error" in st.session_state and st.session_state["error"] is not None:
            st.markdown(f"<span style='color:red'>{st.session_state['error']}</span>", unsafe_allow_html=True)
            st.stop()

        # Response
        if "llm_response" in st.session_state:
            st.write(st.session_state["llm_response"])
