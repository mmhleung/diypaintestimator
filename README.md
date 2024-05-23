# Paint Estimator App

This app uses Google Vision Pro to analyse a floorplan and calculate the amount of paint required for walls and ceilings.

See [Live demo](https://mmhleung-diypaintestimator.streamlit.app/).

## Pre-requisites
* Gemini API Key 

You can create a `.env` file and add a line `GEMINI_API_KEY=XXX`, where **XXX** is your API Key.

The API key can be obtained by signing in to **Google AI Studio** and click "**Get API Key**".

## Create virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/scripts/activate
!pip install -r requirements.txt
```

## Run streamlit app
```bash
streamlit run streamlit_app.py
```

## Run command line
```bash
python google_api_chat.py
```