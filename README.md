# Aqual Laps

*since this is not a commercial project*
*It is not live on any server in order to*
*deploy it you need to use your own gemini api key*

This projects uses scientific papers and experimental data available to provide swimmers
with the most optimized training tailored to their goals and their current situation.

### This is the general structure of the project

swim-ai-coach/ <br>
├── data/<br>
│   ├── raw_papers/          # PDFs and papers collected <br>
│   ├── processed/           # chunked/cleaned text, might get gitignored <br>
|   └── chroma_db/           # embeded text that have been vectored gets stored here <br>
├── src/ <br>
│   ├── __init__.py <br>
│   ├── ingest.py            # parses papers into chunks <br>
│   ├── embed.py             # builds the vector store <br>
│   ├── retrieve.py          # given a query, returns relevant chunks <br>
│   ├── generate.py          # calls the LLM with retrieved context <br>
│   ├── schema.py            # pydantic models for the training plan output <br>
│   └── rules.py             # sanity-check logic (volume caps, taper rules) <br>
├── app.py                   # Streamlit entrypoint <br>
├── tests/ <br>
│   └── test_api.py <br>
├── requirements.txt <br>
├── .env              # placeholder for API keys, real .env gitignored <br>
└── README.md <br>


## Local Deployment


1. First we start by installing setting up the python virtual environment
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Because we have the data saved in the form of pdfs we need to first extract them and
then store them in chunks using the *ingest.py* (has to be run from the parent directory) and then *embed.py*
```
python src/ingest.py
python src/embed.py
```

3. the gemini api key needs to be added either using environment injection (using .env file) or by running
the following in terminal replacing *abcd* with your gemini api key
```
echo "GEMINI_API_KEY='abcd'" > .env
```

4. finally to run the UI we run it using streamlit
```
streamlit run app.py
```
