#!/usr/bin/env python3
"""
Project Document Generator
Generates structured requirements, design, and task documents for new projects
"""

import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional
import os

class ProjectDocumentGenerator:
    def __init__(self, project_name: str, project_type: str = "web-app"):
        self.project_name = project_name
        self.project_type = project_type
        self.timestamp = datetime.now().strftime("%Y-%m-%d")
        
    def generate_requirements_template(self, features: List[str]) -> str:
        """Generate requirements document template"""
        
        template = f"""# Requirements Document

## Introduction

{self.project_name} is a [DESCRIPTION OF SYSTEM PURPOSE]. The system is designed for [TARGET USERS] and will be deployed as [DEPLOYMENT MODEL].

## Glossary

- **[Term]**: [Definition specific to this system]
- **User**: [Define user types]
- **System**: The {self.project_name} platform

## Requirements
"""
        
        for i, feature in enumerate(features, 1):
            template += f"""
### Requirement {i}

**User Story:** As a [USER TYPE], I want {feature}, so that [BENEFIT]

#### Acceptance Criteria

1. WHEN [trigger/condition], THE system SHALL [behavior]
2. WHERE [context applies], THE system SHALL [behavior]
3. THE system SHALL [capability] within [time limit]
4. IF [error condition], THEN THE system SHALL [handle gracefully]
5. THE system SHALL persist [data] with [attributes]
"""
        
        return template
    
    def generate_design_template(self, components: List[str]) -> str:
        """Generate design document template with comprehensive architecture"""
        
        template = f"""# Design Document

## Overview

The {self.project_name} system is built as a [ARCHITECTURE PATTERN] with [KEY COMPONENTS]. The design prioritizes [KEY PRIORITIES].

## System Architecture

### Component Map

| Component ID | Name | Type | Responsibility | Interfaces With |
|-------------|------|------|----------------|-----------------|
| COMP-1 | Frontend | UI | User interface and interaction | COMP-2 |
| COMP-2 | API Gateway | Service | Request routing and authentication | COMP-3, COMP-4 |"""
        
        for i, component in enumerate(components, 3):
            template += f"""
| COMP-{i} | {component} | Service | [Responsibility] | [Components] |"""
        
        template += """

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   [UI Framework] Application                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                    API (REST/GraphQL/WebSocket)
                            │
┌─────────────────────────────────────────────────────────────┐
│                        Backend Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   [Backend Framework] Application                    │  │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐        │  │
│  │   │ Service  │  │ Service  │  │ Service  │        │  │
│  │   └──────────┘  └──────────┘  └──────────┘        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                      Database Access
                            │
┌─────────────────────────────────────────────────────────────┐
│                         Data Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   [Database Type]                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Specifications

### Primary Data Flows

#### 1. User Authentication Flow

```
1. User → Frontend: Login credentials
2. Frontend → API Gateway: Encrypted credentials
3. API Gateway → Auth Service: Validation request
4. Auth Service → User Database: Query user record
5. User Database → Auth Service: User data
6. Auth Service → API Gateway: JWT token
7. API Gateway → Frontend: Auth response with token
```

**Data Transformations:**
- Step 2: Credentials encrypted with HTTPS
- Step 3: Rate limiting applied
- Step 6: JWT token generated with claims

[Add other critical data flows]

## Integration Points

### Internal Integration Points

| Source | Target | Protocol | Data Format | Purpose |
|--------|--------|----------|-------------|---------|
| Frontend | API Gateway | HTTPS/REST | JSON | API calls |
| API Gateway | Services | HTTP/gRPC | JSON/Protobuf | Service calls |
| Services | Database | TCP | SQL | Data persistence |

### External Integration Points

#### [External Service Name]

**Type:** REST API / Database / Message Queue
**Purpose:** [What this integration provides]
**Endpoint:** [URL pattern or connection details]
**Authentication:** [OAuth2, API Key, etc.]
**Rate Limits:** [Any constraints]

**Interface Contract:**
```
POST /api/endpoint
Headers: { "Authorization": "Bearer token" }
Body: { "field": "value" }
Response: { "result": "value" }
```

**Error Handling:**
- Retry strategy: Exponential backoff with jitter
- Circuit breaker: Opens after 5 consecutive failures
- Fallback: [Degraded functionality or cached response]

## System Boundaries

### In Scope
- [Core functionality included]
- [Features to be implemented]

### Out of Scope  
- [Features not included]
- [Delegated to external systems]

### Assumptions
- [External services available]
- [Infrastructure provided]

## Components and Interfaces
"""
        
        for component in components:
            template += f"""
### {component}

**Responsibility:** [Single sentence description of what this component does]

**Key Classes:**
- `{component}Service`: Main service class for {component.lower()} operations
- `{component}Controller`: Handles API requests for {component.lower()}
- `{component}Repository`: Data access layer for {component.lower()}

**Interfaces:**
```python
class {component}Service:
    async def create(self, data: Dict) -> {component}
    async def get(self, id: str) -> Optional[{component}]
    async def update(self, id: str, data: Dict) -> {component}
    async def delete(self, id: str) -> bool
    async def list(self, filters: Dict) -> List[{component}]
```

**Data Flow:**
- Receives requests from [API layer/other service]
- Validates input using [validation rules]
- Processes business logic
- Persists to database
- Returns response

**Performance:**
- Target response time: <200ms for queries
- Target response time: <500ms for mutations
- Maximum concurrent operations: 100
"""
        
        template += """
## Data Models

### User
```python
@dataclass
class User:
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: datetime
```

[Add other data models]

## Error Handling

### API Errors
**Types:** 
- 400 Bad Request - Invalid input
- 401 Unauthorized - Missing/invalid authentication
- 403 Forbidden - Insufficient permissions
- 404 Not Found - Resource doesn't exist
- 500 Internal Server Error - Unexpected error

**Handling:** 
- Return consistent error format with code, message, and details
- Log all errors with context
- Implement retry logic for transient failures

### Database Errors
**Types:**
- Connection failures
- Query timeouts
- Constraint violations

**Handling:**
- Retry with exponential backoff
- Graceful degradation where possible
- Transaction rollback on failure

## Testing Strategy

### Unit Tests
- Service layer: Test business logic with mocked dependencies
- Repository layer: Test database operations
- API layer: Test request/response handling
- Coverage target: 80%

### Integration Tests
- End-to-end API tests
- Database integration tests
- External service integration tests

### Performance Tests
- Load testing: 100 concurrent users
- Response time: p95 < 500ms
- Throughput: >100 requests/second

## Deployment

### Docker Configuration
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - database
      
  database:
    image: postgres:15
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}

volumes:
  db_data:
```

### Environment Variables
```
DATABASE_URL=postgresql://user:pass@localhost/dbname
API_KEY=your-api-key
JWT_SECRET=your-secret-key
NODE_ENV=production
```

## Performance Targets

- API response time: <200ms (p95)
- Database query time: <50ms (p95)
- Frontend load time: <2s
- Time to interactive: <3s
- Memory usage: <512MB per instance

## Security Considerations

- JWT-based authentication
- Rate limiting on all endpoints
- Input validation and sanitization
- SQL injection prevention via parameterized queries
- XSS prevention via output encoding
- HTTPS only in production
"""
        
        return template
    
    def generate_tasks_template(self, phases: List[Dict]) -> str:
        """Generate implementation plan template with boundaries and deliverables"""
        
        template = f"""# Implementation Plan

Generated: {self.timestamp}
Project: {self.project_name}
Type: {self.project_type}

## Project Boundaries

### Must Have (MVP)
- [Core feature 1]
- [Core feature 2]
- [Core feature 3]

### Nice to Have (Enhancements)
- [Enhancement feature 1]
- [Enhancement feature 2]

### Out of Scope
- [Explicitly excluded feature 1]
- [Deferred to future phase]

### Technical Constraints
- [Framework limitations]
- [Resource constraints]

## Deliverables by Phase

| Phase | Deliverables | Success Criteria |
|-------|-------------|------------------|
| 1. Infrastructure | Working development environment | All developers can run locally |
| 2. Data Layer | Database schema, models | CRUD operations functional |
| 3. Business Logic | Core services implemented | All requirements fulfilled |
| 4. API Layer | REST/GraphQL endpoints | API tests passing |
| 5. Frontend | User interface | End-to-end workflows complete |
| 6. Testing | Test coverage >80% | All tests passing |
| 7. Deployment | Production environment | System accessible and stable |

## Task Breakdown

"""
        
        for phase_num, phase in enumerate(phases, 1):
            template += f"- [ ] {phase_num}. {phase['name']}\n\n"
            
            for task_num, task in enumerate(phase.get('tasks', []), 1):
                template += f"  - [ ] {phase_num}.{task_num} {task['name']}\n"
                
                if 'subtasks' in task:
                    for subtask in task['subtasks']:
                        template += f"    - {subtask}\n"
                
                if 'requirements' in task:
                    template += f"    - _Requirements: {', '.join(task['requirements'])}_\n"
                    
                if 'dependencies' in task and task['dependencies']:
                    template += f"    - _Dependencies: {', '.join(task['dependencies'])}_\n"
                
                template += "\n"
            
        return template
    
    def get_default_phases(self) -> List[Dict]:
        """Get default phases based on project type"""
        
        if self.project_type == "web-app":
            return [
                {
                    "name": "Infrastructure Setup",
                    "tasks": [
                        {
                            "name": "Initialize project structure",
                            "subtasks": [
                                "Create directory structure",
                                "Initialize package managers",
                                "Set up version control"
                            ],
                            "requirements": ["REQ-12.1"]
                        },
                        {
                            "name": "Set up database",
                            "subtasks": [
                                "Create database schema",
                                "Write migrations",
                                "Set up connection pooling"
                            ],
                            "requirements": ["REQ-9.1", "REQ-9.2"]
                        },
                        {
                            "name": "Configure Docker",
                            "subtasks": [
                                "Create Dockerfiles",
                                "Write docker-compose.yml",
                                "Set up volumes and networks"
                            ],
                            "requirements": ["REQ-12.2", "REQ-12.3"]
                        }
                    ]
                },
                {
                    "name": "Backend Implementation",
                    "tasks": [
                        {
                            "name": "Create data models",
                            "subtasks": [
                                "Define entities",
                                "Create validation schemas",
                                "Implement serialization"
                            ],
                            "requirements": ["REQ-3.1"],
                            "dependencies": ["1.2"]
                        },
                        {
                            "name": "Implement service layer",
                            "subtasks": [
                                "Create business logic services",
                                "Implement validation rules",
                                "Add error handling"
                            ],
                            "requirements": ["REQ-4.1"],
                            "dependencies": ["2.1"]
                        },
                        {
                            "name": "Build API endpoints",
                            "subtasks": [
                                "Create REST/GraphQL routes",
                                "Add authentication middleware",
                                "Implement request validation"
                            ],
                            "requirements": ["REQ-5.1"],
                            "dependencies": ["2.2"]
                        }
                    ]
                },
                {
                    "name": "Frontend Implementation",
                    "tasks": [
                        {
                            "name": "Set up frontend framework",
                            "subtasks": [
                                "Initialize React/Vue/Angular app",
                                "Configure build tools",
                                "Set up routing"
                            ],
                            "requirements": ["REQ-7.1"]
                        },
                        {
                            "name": "Create UI components",
                            "subtasks": [
                                "Build reusable components",
                                "Implement responsive design",
                                "Add styling/theming"
                            ],
                            "requirements": ["REQ-7.2"],
                            "dependencies": ["3.1"]
                        },
                        {
                            "name": "Integrate with backend",
                            "subtasks": [
                                "Set up API client",
                                "Implement state management",
                                "Add error handling"
                            ],
                            "requirements": ["REQ-7.3"],
                            "dependencies": ["2.3", "3.2"]
                        }
                    ]
                },
                {
                    "name": "Testing and Quality Assurance",
                    "tasks": [
                        {
                            "name": "Write unit tests",
                            "subtasks": [
                                "Test services",
                                "Test components",
                                "Test utilities"
                            ],
                            "requirements": ["REQ-13.1"],
                            "dependencies": ["2.2", "3.2"]
                        },
                        {
                            "name": "Create integration tests",
                            "subtasks": [
                                "Test API endpoints",
                                "Test database operations",
                                "Test external integrations"
                            ],
                            "requirements": ["REQ-13.2"],
                            "dependencies": ["4.1"]
                        },
                        {
                            "name": "Perform end-to-end testing",
                            "subtasks": [
                                "Test user workflows",
                                "Test error scenarios",
                                "Performance testing"
                            ],
                            "requirements": ["REQ-13.3"],
                            "dependencies": ["4.2"]
                        }
                    ]
                },
                {
                    "name": "Deployment and Documentation",
                    "tasks": [
                        {
                            "name": "Set up CI/CD pipeline",
                            "subtasks": [
                                "Configure build automation",
                                "Set up test automation",
                                "Configure deployment"
                            ],
                            "requirements": ["REQ-14.1"],
                            "dependencies": ["4.3"]
                        },
                        {
                            "name": "Write documentation",
                            "subtasks": [
                                "API documentation",
                                "User guide",
                                "Deployment guide"
                            ],
                            "requirements": ["REQ-15.1"],
                            "dependencies": ["5.1"]
                        },
                        {
                            "name": "Deploy to production",
                            "subtasks": [
                                "Set up production environment",
                                "Configure monitoring",
                                "Perform deployment"
                            ],
                            "requirements": ["REQ-14.2"],
                            "dependencies": ["5.2"]
                        }
                    ]
                }
            ]
        
        elif self.project_type == "cli-tool":
            return [
                {
                    "name": "Project Setup",
                    "tasks": [
                        {
                            "name": "Initialize project",
                            "subtasks": [
                                "Set up package structure",
                                "Configure build system",
                                "Add dependencies"
                            ]
                        },
                        {
                            "name": "Design command structure",
                            "subtasks": [
                                "Define commands and subcommands",
                                "Plan argument parsing",
                                "Design configuration schema"
                            ]
                        }
                    ]
                },
                {
                    "name": "Core Implementation",
                    "tasks": [
                        {
                            "name": "Implement command parser",
                            "subtasks": [
                                "Create argument parser",
                                "Add command handlers",
                                "Implement help system"
                            ],
                            "dependencies": ["1.2"]
                        },
                        {
                            "name": "Build core logic",
                            "subtasks": [
                                "Implement business logic",
                                "Add validation",
                                "Handle errors"
                            ],
                            "dependencies": ["2.1"]
                        }
                    ]
                },
                {
                    "name": "Testing and Packaging",
                    "tasks": [
                        {
                            "name": "Write tests",
                            "subtasks": [
                                "Unit tests",
                                "Integration tests",
                                "CLI tests"
                            ],
                            "dependencies": ["2.2"]
                        },
                        {
                            "name": "Package and distribute",
                            "subtasks": [
                                "Create package",
                                "Write documentation",
                                "Publish"
                            ],
                            "dependencies": ["3.1"]
                        }
                    ]
                }
            ]
        
        elif self.project_type == "api-service":
            return [
                {
                    "name": "Service Setup",
                    "tasks": [
                        {
                            "name": "Initialize API project",
                            "subtasks": [
                                "Set up framework",
                                "Configure database",
                                "Add middleware"
                            ]
                        },
                        {
                            "name": "Design API schema",
                            "subtasks": [
                                "Define endpoints",
                                "Create OpenAPI spec",
                                "Plan authentication"
                            ]
                        }
                    ]
                },
                {
                    "name": "API Implementation",
                    "tasks": [
                        {
                            "name": "Create endpoints",
                            "subtasks": [
                                "Implement routes",
                                "Add validation",
                                "Handle errors"
                            ],
                            "dependencies": ["1.2"]
                        },
                        {
                            "name": "Add authentication",
                            "subtasks": [
                                "Implement auth middleware",
                                "Add JWT/OAuth",
                                "Set up permissions"
                            ],
                            "dependencies": ["2.1"]
                        }
                    ]
                }
            ]
        
        else:  # Generic project
            return [
                {
                    "name": "Project Setup",
                    "tasks": [
                        {
                            "name": "Initialize project",
                            "subtasks": ["Create structure", "Set up tools"]
                        }
                    ]
                },
                {
                    "name": "Implementation",
                    "tasks": [
                        {
                            "name": "Build core features",
                            "subtasks": ["Implement logic", "Add tests"]
                        }
                    ]
                },
                {
                    "name": "Deployment",
                    "tasks": [
                        {
                            "name": "Prepare for production",
                            "subtasks": ["Test", "Document", "Deploy"]
                        }
                    ]
                }
            ]
    
    def generate_all_documents(self, 
                              features: List[str] = None,
                              components: List[str] = None,
                              output_dir: str = ".") -> Dict[str, str]:
        """Generate all three documents"""
        
        # Use defaults if not provided
        if not features:
            features = [
                "to authenticate and manage my account",
                "to create and manage resources",
                "to view analytics and reports",
                "to configure system settings",
                "to receive notifications"
            ]
        
        if not components:
            components = [
                "Authentication Service",
                "User Management",
                "Resource Manager",
                "Analytics Engine",
                "Notification Service"
            ]
        
        # Generate documents
        docs = {
            "requirements.md": self.generate_requirements_template(features),
            "design.md": self.generate_design_template(components),
            "tasks.md": self.generate_tasks_template(self.get_default_phases())
        }
        
        # Save to files
        os.makedirs(output_dir, exist_ok=True)
        
        for filename, content in docs.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Generated: {filepath}")
        
        return docs


def main():
    parser = argparse.ArgumentParser(description="Generate project planning documents")
    parser.add_argument("project_name", help="Name of the project")
    parser.add_argument("--type", default="web-app", 
                      choices=["web-app", "cli-tool", "api-service", "generic"],
                      help="Type of project")
    parser.add_argument("--features", nargs="+", 
                      help="List of features for requirements")
    parser.add_argument("--components", nargs="+",
                      help="List of components for design")
    parser.add_argument("--output", default=".", 
                      help="Output directory for documents")
    
    args = parser.parse_args()
    
    generator = ProjectDocumentGenerator(args.project_name, args.type)
    generator.generate_all_documents(
        features=args.features,
        components=args.components,
        output_dir=args.output
    )
    
    print(f"\n✅ Successfully generated project documents for '{args.project_name}'")
    print(f"   Type: {args.type}")
    print(f"   Location: {args.output}/")
    print("\nNext steps:")
    print("1. Review and customize the generated documents")
    print("2. Fill in the [PLACEHOLDER] sections")
    print("3. Add project-specific requirements and design details")
    print("4. Use these documents as input for AI-assisted implementation")


if __name__ == "__main__":
    main()
