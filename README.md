# Aqual Laps

This projects uses scientific papers and experimental data available to provide swimmers
with the most optimized training tailored to their goals and their current situation.

### This is the general structure of the project

swim-ai-coach/ <br>
├── data/<br>
│   ├── raw_papers/          # PDFs and papers collected <br>
│   └── processed/           # chunked/cleaned text, might get gitignored <br>
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
│   └── test_rules.py <br>
├── requirements.txt <br>
├── .env.example              # placeholder for API keys, real .env gitignored <br>
└── README.md <br>