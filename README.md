# LLM Conversations API

This project is a backend API to manage conversations with a Language Model (LLM). It provides CRUD operations for conversations and messages, integrates with an LLM service (e.g., OpenAI), and logs interactions for auditing purposes. The backend is built with FastAPI, Beanie (for MongoDB), and Pydantic, and it is fully containerized using Docker and Docker Compose.

---

## Table of Contents

- [LLM Conversations API](#llm-conversations-api)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Technologies](#technologies)
  - [Prerequisites](#prerequisites)
  - [Installation and Setup](#installation-and-setup)
  - [Environment Variables](#environment-variables)
  - [Running the Application](#running-the-application)
    - [Using Docker Compose](#using-docker-compose)
    - [Running Locally Without Docker](#running-locally-without-docker)
  - [API Documentation](#api-documentation)
  - [Running Tests](#running-tests)

---

## Features

- **Conversation & Message Management:**  
  Create, list, retrieve, update, and delete conversations; manage messages within conversations.
- **LLM Integration:**  
  Send prompt queries and receive responses from an LLM service (e.g., OpenAI).
- **Audit Logging:**  
  Anonymize and log prompt and response data for auditing purposes.
- **PII Masking:**  
  Automatically mask common Personally Identifiable Information (PII) in logs.
- **Containerized Deployment:**  
  Run the backend and MongoDB seamlessly using Docker Compose.

---

## Technologies

- **Programming Language:** Python (>= 3.10)
- **Framework:** FastAPI
- **Data Validation/Models:** Pydantic, Beanie
- **Database:** MongoDB (accessed via Motor)
- **Containerization:** Docker & Docker Compose
- **LLM Integration:** OpenAI Python Client

---

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/install/) installed.
- (Optional) [Git](https://git-scm.com/) for cloning the repository.

---

## Installation and Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>


   # LLM Conversations API Backend

This repository contains the backend component of the LLM Conversations API. It is built using **FastAPI**, **Pydantic**, **Beanie** (with Motor), and integrates with the **OpenAI** Python client. The backend provides CRUD operations for conversations (which include a history of user prompts and LLM responses) as well as auditing with anonymization of PII. The project is containerized using **Docker** and uses a **MongoDB** instance running in a Docker container.

---

## Table of Contents

- [LLM Conversations API](#llm-conversations-api)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Technologies](#technologies)
  - [Prerequisites](#prerequisites)
  - [Installation and Setup](#installation-and-setup)
  - [Environment Variables](#environment-variables)
  - [Running the Application](#running-the-application)
    - [Using Docker Compose](#using-docker-compose)
    - [Running Locally Without Docker](#running-locally-without-docker)
  - [API Documentation](#api-documentation)
  - [Running Tests](#running-tests)

---

## Features

- **Conversations CRUD:**  
  Create, read, update, and delete conversations that store a history of messages (user prompts and LLM responses).

- **LLM Integration:**  
  Send a prompt to an LLM (via OpenAI's ChatCompletion API) and receive responses using conversation context.

- **Message Operations:**  
  In addition to conversation-level operations, manage individual messages (creation and update) within a conversation.

- **Audit Logging with PII Masking:**  
  Audit logs are created for each LLM interaction with PII (such as email addresses and phone numbers) masked. Only a portion (e.g., last 2000 characters) is stored.

- **Dockerized Environment:**  
  The backend and MongoDB are fully containerized with Docker and Docker Compose for a consistent and reproducible setup.

---

## Prerequisites

Ensure you have the following installed on your system:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional) [Git](https://git-scm.com/)

---

## Installation and Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/llmapp-backend.git
   cd llmapp-backend
   ```

2. **Create a `.env` File**

    In the project root, create a file named .env (this file should not be committed to version control). See the Environment Variables section for details on what to include.

1. **Build and Run with Docker Compose**
    The repository includes a docker-compose.yml file that sets up both the backend and the MongoDB container. To build and run the application, execute:

    ```bash
    docker-compose up --build
    ```

    This command will:
    - Build the backend Docker image.
    - Pull the official MongoDB 6.0 image.
    - Start both containers and link them on a Docker network.

4. **Verify Containers are Running**

    You should see log output indicating that:
      - The MongoDB container is running (listening on port 27017).
      - The backend container has started and the application has initialized.

## Environment Variables

The backend requires your OpenAI API key. Create a `.env` file in the project root with the following content:
    ```env
    # OpenAI API key (DO NOT commit your real API key)
    OPENAI_API_KEY=your_openai_api_key_here
    ```

Note:
- Use a real API key in your local environment or deployment but keep it secure (do not commit it).
- You can also change other parameters like database name, model to use and the mongoDB URI in the docker-compopse file.

## Running the Application

### Using Docker Compose

After building and running with Docker Compose, the backend will be accessible at:

    http://localhost:8000

### Running Locally Without Docker

If you prefer to run the application directly (for development):
	1.	Ensure MongoDB is running locally (e.g., installed on your machine or via Docker using docker run -p 27017:27017 mongo:6.0).
	2.	Set the required environment variables (or ensure your .env file is loaded). You will need to include all environment variables mentioned in the docker-compose environment section.
	3.	Start the application in the root directory with:
```bash
uvicorn app.main:app --reload
```

The API will then be available at http://localhost:8000.

## API Documentation

FastAPI automatically generates interactive API documentation. Once the application is running, access it at: http://localhost:8000/docs

## Running Tests

Tests are written using pytest and pytest-asyncio. To run the tests:
1. **Install test dependencies:**
    ```bash
    pip install pytest pytest-asyncio
    ```

2. **Run the tests:**

    ```bash
    pytest --cov --cov-report=lcov:lcov.info --cov-report=term
    ```

The test suite covers CRUD operations for conversations, message operations, LLM prompt sending, and error handling.




