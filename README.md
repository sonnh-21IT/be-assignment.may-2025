# Intern Backend Developer Assignment
- Copyright (c) River Flow Solutions, Jsc. 2025. All rights reserved.
- We only use the submissions for candidates evaluation.

## A. Instructions
Candidate must fork this repository to a public repo under their name for submission.

Implement a backend messaging system API with the following goals:

- Build APIs based on the provided data model.
- Use **FastAPI** for API development.
- Use **PostgreSQL/SQLite** for data management.
- Use **Justfile** for all run and development commands.
- Use **GitHub Actions** for CI/CD and Automatic testing.
- (Optional – Advanced) Use **Docker** to containerize the application.
- (Optional – Advanced) Convert the API to an **MCP server** and connect to **Claude Desktop** for testing.

You can setup `Postgresql` local via `docker-compose.yml` using command:

- `just up`: Run postgres
- `just down`: Stop postgres

## B. Messaging System Data Model
The following tables must be implemented:

#### `users`
- `id`: UUID (primary key)
- `email`: String (unique)
- `name`: String
- `created_at`: DateTime

#### `messages`
- `id`: UUID (primary key)
- `sender_id`: UUID (foreign key to users)
- `subject`: String (optional)
- `content`: Text
- `timestamp`: DateTime

#### `message_recipients`
- `id`: UUID (primary key)
- `message_id`: UUID (foreign key to messages)
- `recipient_id`: UUID (foreign key to users)
- `read`: Boolean
- `read_at`: DateTime (nullable)

## C. Tech Requirements
- Python 3.11+
- FastAPI
- PostgreSQL/SQLite
- SQLAlchemy ORM
- Justfile
- GitHub Actions for CI/CD
- (Optional) Docker & Docker Compose
- (Optional) MCP integration for AI agent testing

## D. Review Criteria
#### **Please check the box for each item you have completed before submitting your GitHub repository.**

### D1. API Requirements

The system must support the following API functionality:

#### User APIs
- `[x]` Create a user
- `[x]` Retrieve user info
- `[x]` List users

#### Message APIs
- `[x]` Send a message to one or more recipients
- `[x]` View sent messages
- `[x]` View inbox messages
- `[x]` View unread messages
- `[x]` View a message with all recipients
- `[x]` Mark a message as read

### D2. Command Line (Justfile)

All scripts for development and testing must be included in a `Justfile`. The following commands are required:

- `[x]` `just install`
- `[x]` `just dev`
- `[x]` `just migrate`
- `[x]` `just test`
- `[x]` `just down` (optional)
- `[x]` `just up` (optional)
- `[ ]` `just mcp` (optional)
- `[x]` `just format` (optional)

### D3. CI/CD With Github Action
Your repository will be automatically tested using GitHub Actions. To pass this phase, please ensure the following:

Include automated tests in the `/tests` folder using pytest.

Your pipeline must include:

- `[ ]` Sets up Python 3.11
- `[ ]` Installs dependencies using just install
- `[ ]` Runs tests using just test

You must include test cases that cover:

- `[x]` User Management: Create user, get user by ID, list users
- `[x]` Messaging : Send message, get inbox, get sent
- `[x]` Read Status : Mark message as read, get unread messages

### D4. Package API with Docker (Optional)
You must include the following in your project:

- `[x]` Dockerfile
	```
	- Containerizes the FastAPI application.
	- Must expose port 8000.
	- Uses a production-ready base image (e.g. python:3.11-slim).
	- Installs dependencies from requirements.txt.
	```
- `[x]` docker-compose.yml
	```
	- Starts at least:
		- Your FastAPI app container
		- A PostgreSQL container
	- PostgreSQL should:
		- Use a default user, password, and database name
		- Expose port 5432
	- Be accessible to the app via internal hostname (e.g., db)
	```
- `[x]` .env.example
	```
	- Provide an example .env file containing:
		- DATABASE_URL
		- Any other required environment variables
	```

### D5. Advanced: MCP-compatible server (Optional)

- `[ ]` Convert the application to an MCP-compatible server.
- `[ ]` Define a set of MCP tool functions that can interact with the messaging system.
- `[ ]` Provide a `.mcp.json` manifest for Claude Desktop to consume.
- `[ ]` Demonstrate successful interaction between Claude and your MCP server.
