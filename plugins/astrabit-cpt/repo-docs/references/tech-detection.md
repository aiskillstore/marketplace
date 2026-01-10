# Technology Detection

Patterns for identifying technologies, frameworks, and build tools from repository structure.

## Language Indicators

| Language | Indicators |
|----------|------------|
| JavaScript/TypeScript | `package.json`, `tsconfig.json`, `.ts`/`.tsx` files |
| Python | `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile`, `.py` files |
| Go | `go.mod`, `go.sum`, `.go` files |
| Rust | `Cargo.toml`, `Cargo.lock`, `.rs` files |
| Java | `pom.xml` (Maven), `build.gradle` (Gradle), `.java` files |
| Ruby | `Gemfile`, `Rakefile`, `.rb` files |
| C# | `.csproj`, `package.json`, `.cs` files |
| PHP | `composer.json`, `.php` files |

## Framework Indicators

### JavaScript/TypeScript

| Framework | Indicator Files |
|-----------|-----------------|
| React | `package.json` contains `react`, JSX/TSX files |
| Vue | `package.json` contains `vue`, `.vue` files |
| Angular | `angular.json`, `package.json` contains `@angular/` |
| Next.js | `next.config.js`, `pages/` or `app/` directory |
| Express | `package.json` contains `express` |
| NestJS | `nest-cli.json`, decorators in code |
| Remix | `remix.config.js`, `app/` directory |

### Python

| Framework | Indicator Files |
|-----------|-----------------|
| Django | `manage.py`, `settings.py`, `urls.py` |
| FastAPI | `main.py` with `FastAPI()`, `pyproject.toml` with `fastapi` |
| Flask | `app.py` with `Flask()`, `requirements.txt` with `Flask` |
| SQLAlchemy | `models.py`, SQLAlchemy imports |

### Go

| Framework | Indicator Files |
|-----------|-----------------|
| Gin | `go.mod` contains `gin-gonic/gin` |
| Echo | `go.mod` contains `labstack/echo` |
| gRPC | `.proto` files, `go.mod` contains `google.golang.org/grpc` |

### Java

| Framework | Indicator Files |
|-----------|-----------------|
| Spring Boot | `pom.xml` with `spring-boot-starter`, `@SpringBootApplication` |
| Micronaut | `micronaut.yml` |
| Quarkus | `application.properties` with Quarkus config |

## Build Tool Indicators

| Tool | Indicator |
|------|-----------|
| npm/yarn/pnpm | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Maven | `pom.xml` |
| Gradle | `build.gradle`, `build.gradle.kts`, `settings.gradle` |
| Make | `Makefile` |
| CMake | `CMakeLists.txt` |
| Docker Compose | `docker-compose.yml`, `compose.yaml` |
| Bazel | `WORKSPACE`, `BUILD` files |
| webpack | `webpack.config.js` |
| Vite | `vite.config.js` |
| esbuild | `esbuild.config.js` |
| Turbopack | `turbo/` directory, `turbo.json` |

## CI/CD Indicators

| Platform | Indicator Files/Directories |
|----------|----------------------------|
| GitHub Actions | `.github/workflows/` |
| GitLab CI | `.gitlab-ci.yml` |
| CircleCI | `.circleci/config.yml` |
| Travis CI | `.travis.yml` |
| Jenkins | `Jenkinsfile` |
| Azure Pipelines | `azure-pipelines.yml` |
| Bitbucket | `bitbucket-pipelines.yml` |

## Testing Framework Indicators

| Language | Framework | Indicator |
|----------|-----------|-----------|
| JS/TS | Jest | `jest.config.js`, `.spec.js`/`.test.js` files |
| JS/TS | Vitest | `vitest.config.ts` |
| JS/TS | Mocha | `mocha.opts`, `.test.js` files |
| Python | pytest | `pytest.ini`, `conftest.py`, `test_*.py` files |
| Python | unittest | `unittest` imports, `test_*.py` files |
| Go | testing | `*_test.go` files |
| Java | JUnit | `@Test` annotations, `*Test.java` files |
| Rust | built-in | `*_test.rs` files, `cfg(test)` |

## Dependency Detection Patterns

### Internal Package References

When scanning for integration points, look for:

| Language | Pattern | Example |
|----------|---------|---------|
| JS/TS | `@org/` | `import { Button } from '@org/ui'` |
| JS/TS | `@scope/` | `import { api } from '@company/api-client'` |
| Python | `internal.` | `from company.internal import auth` |
| Go | `github.com/org/` | `import "github.com/company/service"` |
| Java | `company.` | `import com.company.shared.` |
| C# | `Company.` | `using Company.Shared.` |

### External Service Client Indicators

| Pattern | Indicates |
|---------|-----------|
| `*Client`, `*ApiClient` | Likely external API client |
| `fetch`, `axios`, `http` | HTTP calls to services |
| `RestTemplate`, `WebClient` | Java HTTP clients |
| `requests`, `httpx` | Python HTTP libraries |
| `grpc.` | gRPC service calls |
| `kafka.` | Kafka message producer/consumer |
| `sqs`, `sns` | AWS messaging |
| `pubsub` | Google Pub/Sub |
| `amqp` | RabbitMQ |
| `redis.` | Redis cache/client |
| `*.mongo*` | MongoDB client |
| `*.prisma` | Prisma ORM |

## Configuration File Patterns

| Config Type | Common Locations |
|-------------|------------------|
| Environment | `.env`, `.env.example`, `.env.local` |
| Docker | `Dockerfile`, `docker-compose.yml` |
| Kubernetes | `k8s/`, `kube/`, `.yaml` manifests |
| Terraform | `*.tf` files |
| Helm | `helm/`, `Chart.yaml` |
| API specs | `openapi.yaml`, `swagger.yaml`, `*.graphql` |
| Schema | `schema.graphql`, `schema.prisma` |

## Search Commands

Use these grep patterns to find integrations:

```bash
# JavaScript/TypeScript internal imports
rg '@company/' --type js --type ts

# Python internal imports
rg 'from company\.internal' --type py
rg 'import company\.' --type py

# Go module references
rg 'github\.com/company/' --type go

# Java internal imports
rg 'import com\.company\.' --type java

# HTTP calls (potential service calls)
rg '\b(fetch|axios|request)\(' --type js --type ts

# Database clients
rg '\b(prisma|mongoose|sequelize|typeorm|knex)\b' --type js
rg '\b(sqlalchemy|psycopg|pymongo)\b' --type py

# Message queue clients
rg '\b(kafka|sqs|sns|pubsub|amqp)\b' --type js --type py
```
