# Framework Adapters

## FastAPI

Set `APP_IMPORT_PATH` to the module and application variable, such as `my_app.main:app`. Configure the routes in `.env.test` to match the application rather than relying on defaults.

## Django

Point `APP_IMPORT_PATH` to the ASGI application, commonly `project.asgi:application`. Set the Django settings environment before running pytest when the project does not establish it during import. Use dedicated accounts in a test database.

## Flask

Flask is a WSGI application by default. Wrap the Flask application with a maintained ASGI adapter, then point `APP_IMPORT_PATH` at that ASGI callable. Do not expose a development server simply to run this suite.

## Other services

Use any application that can be imported as an ASGI callable. If the service cannot be loaded in process, record that boundary and use a separately authorized integration test approach.
