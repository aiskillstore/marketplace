# Patterns Before/After

## Example 1: Project Overview

### Before (156 tokens)

```markdown
# Project Overview

This project is a web application that allows users to manage their
tasks efficiently. It was built using modern technologies and follows
best practices for software development. The application provides a
user-friendly interface that makes it easy to create, update, and
delete tasks. Users can also organize their tasks into different
categories and set due dates for better time management.

## Technologies Used

The project uses React for the frontend, which provides a component-based
architecture that makes the code modular and maintainable. For the backend,
we use Node.js with Express, which handles API requests efficiently.
PostgreSQL is used as the database to store all the task data.
```

### After (42 tokens)

```markdown
# Task Manager

## Stack
| Layer | Tech |
|-------|------|
| Frontend | React |
| Backend | Node/Express |
| DB | PostgreSQL |

## Features
- CRUD tasks
- Categories
- Due dates
```

---

## Example 2: API Documentation

### Before (89 tokens)

```markdown
## Creating a New User

To create a new user in the system, you need to make a POST request
to the /api/users endpoint. The request body should contain a JSON
object with the user's information. The required fields are username
and email. Optionally, you can also include the user's full name.
If the request is successful, the server will return the newly created
user object with a 201 status code.
```

### After (35 tokens)

```markdown
## POST /api/users

```json
// Request
{ "username": "jo", "email": "jo@x.com", "name?": "Jo Doe" }

// Response 201
{ "id": 1, "username": "jo", ... }
```
```

---

## Example 3: Setup Instructions

### Before (67 tokens)

```markdown
## Getting Started

Before you can start working on the project, you'll need to set up
your development environment. First, make sure you have Node.js
version 18 or higher installed on your machine. Then, clone the
repository and navigate to the project directory. Next, install
all the dependencies by running npm install. Finally, you can
start the development server using npm run dev.
```

### After (25 tokens)

```markdown
## Setup

1. Requires: Node 18+
2. `git clone [repo] && cd [project]`
3. `npm install`
4. `npm run dev`
```

---

## Example 4: Architecture Description

### Before (112 tokens)

```markdown
## System Architecture

The system follows a microservices architecture pattern where
different functionalities are separated into independent services.
The API Gateway serves as the entry point for all client requests
and routes them to the appropriate microservice. Each microservice
has its own database to ensure loose coupling. Services communicate
with each other through a message queue (RabbitMQ) for asynchronous
operations and REST APIs for synchronous requests. The authentication
service handles all user authentication and issues JWT tokens.
```

### After (45 tokens)

```markdown
## Architecture

```
Client → API Gateway → Services
                    ├── Auth (JWT)
                    ├── Users
                    └── Orders

Services: Own DB each
Sync: REST | Async: RabbitMQ
```
```

---

## Anti-Patterns to Avoid

| Pattern | Example | Problem |
|---------|---------|---------|
| Meta-commentary | "In this section..." | Wastes tokens |
| Hedging | "You might want to..." | Unclear |
| Obvious statements | "The config file configures..." | Redundant |
| Passive voice | "The file is read by..." | Longer |
| Multiple ways | "You can do X or Y or Z" | Confusing |
