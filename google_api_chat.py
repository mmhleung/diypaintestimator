"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""
import requests
import os
from io import BytesIO
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def download_image_from_uri(uri) -> Image:
    response = requests.get(url=uri)
    if response.status_code == 200:
        image_data = response.content

        # Read the image data from the response content
        image_data = response.content
        
        # Convert the image data to a BytesIO object
        image_stream = BytesIO(image_data)
        
        # Open the image using Pillow
        image = Image.open(image_stream)
        
        return image
    else:
        raise Exception(f"Failed to download image. Status code: {response.status_code}")
    


# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
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

# Reference local file
# image_url = "C:\\\\work\\code\\labs\\gemini-vision-pro-labs\\11-52-WestParade-WestRyde.jpeg"
# image_drive0 = Image.open(image_url)

# Download directly from web
image_url = "https://rimh2.domainstatic.com.au/L23xHDnZAtCWqI5WCzJUS4fWn3c=/fit-in/1920x1080/filters:format(jpeg):quality(80):background_color(white):no_upscale()/2019250405_9_3_240517_025633-w2121-h1500"
image_drive0 = download_image_from_uri(image_url)

chat_session = model.start_chat()
response = chat_session.send_message(["""I want to paint the interior walls and ceiling of the house, excluding kitchen and bathroom.
Assume that the wall height is 2.5m and I need to paint 2 coats.
Assume 1 litre of paint covers 10sqm for both wall and ceiling paint.
Calculate how much paint is required for walls and for ceiling.
""", image_drive0])

print(response.text)

print("------------")

# answer = "you will need approximately 16.5 liters of wall paint and 7 liters of ceiling paint."
response2 = chat_session.send_message([response.text, "From given input, return only the JSON (with no markdown markers) showing the amount of paint required for wall and ceiling."])
print(response2.text)
