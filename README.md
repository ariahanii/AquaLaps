# Aqual Laps

This projects uses scientific papers and experimental data available to provide swimmers
with the most optimized training tailored to their goals and their current situation.

### This is the general structure of the project

swim-ai-coach/
├── data/
│   ├── raw_papers/          # PDFs and papers collected
│   └── processed/           # chunked/cleaned text, might get gitignored
├── src/
│   ├── __init__.py
│   ├── ingest.py            # parses papers into chunks
│   ├── embed.py             # builds the vector store
│   ├── retrieve.py          # given a query, returns relevant chunks
│   ├── generate.py          # calls the LLM with retrieved context
│   ├── schema.py            # pydantic models for the training plan output
│   └── rules.py             # sanity-check logic (volume caps, taper rules)
├── app.py                   # Streamlit entrypoint
├── tests/
│   └── test_rules.py
├── requirements.txt
├── .env.example              # placeholder for API keys, real .env gitignored
└── README.md