# Messaging API Backend Assignment
```
src/
│
├── app/                     # Main application code
│   ├── main.py              # FastAPI app entrypoint
│   ├── db.py                # DB connection setup
│   ├── models.py            # All DB models
│   ├── schemas.py           # Pydantic models
│   ├── routes.py            # API routes
│   └── mcp_server.py        # (Optional) MCP entrypoint
│
├── tests/                   # Test cases
│   ├── test_users.py
│   └── test_messages.py
│
├── justfile                 # Command shortcuts
├── Dockerfile               # Containerize FastAPI app
├── docker-compose.yml       # Run app and PostgreSQL
├── requirements.txt         # Python dependencies
├── .mcp.json                # (Optional) MCP manifest
├── .env.example             # Sample environment variables
├── .gitignore
└── README.md                # Setup and usage instructions
```

