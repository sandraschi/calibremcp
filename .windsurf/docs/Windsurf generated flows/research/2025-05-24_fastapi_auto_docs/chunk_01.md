# FastAPI: Automatic API Documentation with Swagger UI and ReDoc

FastAPI provides automatic API documentation generation based on the OpenAPI standard. This feature is a core part of the framework and offers two interactive user interfaces out-of-the-box: Swagger UI and ReDoc.

## Key Features and How it Works

1.  **OpenAPI Schema**: FastAPI automatically generates an OpenAPI schema for your API. Thischema is a JSON object (usually found at `/openapi.json`) that describes your API paths, parameters, request bodies, responses, security schemes, etc. Thischema is the foundation for the documentation UIs.
    *   The URL for the OpenAPI schema can be configured (e.g., `app = FastAPI(openapi_url="/api/v1/openapi.json")`) or disabled by setting `openapi_url=None`.

2.  **Swagger UI**: 
    *   **Default URL**: `/docs`
    *   **Functionality**: Provides a rich, interactive UI where users can explore API endpoints, see their details (parameters, request/response models), and even try them out directly in the browser.
    *   **Generation**: FastAPI uses an internal function `get_swagger_ui_html()` to generate the HTML page for Swagger UI. This function takes parameters like the `openapi_url`, `title`, and URLs for Swagger UI's JavaScript and CSS assets (which defaulto CDN-hosted versions).
    *   Users typically don't call `get_swagger_ui_html()` directly unless they need to heavily customize aspects like the JS/CSS asset URLs (e.g., for self-hosting).

3.  **ReDoc**:
    *   **Default URL**: `/redoc`
    *   **Functionality**: Offers an alternative, more documentation-focused UI. It's less about direct interaction and more about presenting the API specification in a clean, readable format.
    *   **Generation**: Similar to Swagger UI, FastAPI uses `get_redoc_html()` to generate the ReDoc page.

4.  **Automatic Generation from Code**: The content of the OpenAPI schema, and thus the documentation, is derived from your Python code:
    *   **Path Operations**: `@app.get()`, `@app.post()`, etc., define the API paths.
    *   **Parameters**: Function parameters (with type hints) define path and query parameters.
    *   **Request Bodies**: Pydantic models used as type hints forequest body parameters define thexpected requestructure.
    *   **Responses**: The `response_model` parameter in path operation decorators, along with status codes, definexpected responses.
    *   **Docstrings**: Docstrings in your path operation functions are used as descriptions for thendpoints.
    *   **Pydantic Model Descriptions**: Descriptions in Pydantic models (e.g., using `Field(description=...)`) appear in the schemandocs.

## Customization

FastAPI offerseveral ways to customize the automatically generatedocumentation:

1.  **API Metadata**: You can provide metadata when creating the `FastAPI` instance. This metadata is used in the OpenAPI schemandisplayed in the docs UIs.
    *   `title`: The title of the API (e.g., `"ChimichangApp"`).
    *   `description`: A detailedescription of the API. Supports Markdown.
    *   `summary`: A short summary of the API.
    *   `version`: The API version (e.g., `"0.0.1"`).
    *   `terms_of_service`: URL to the terms of service.
    *   `contact`: A dictionary with contact information (name, URL, email).
    *   `license_info`: A dictionary with license information (name, URL or SPDX identifier like `"MIT"`).

    Example:
    ```python
    from fastapimport FastAPI

    description = """
    MyApp API helps you do awesome stuff. 🚀

    ## Items
    You can **read items**.
    """

    app = FastAPI(
        title="MyApp",
        description=description,
        version="1.0.0",
        contact={
            "name": "Supporteam",
            "email": "support@example.com",
        },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        }
    )
    ```

2.  **Docs URLs**: The default URLs (`/docs`, `/redoc`) can be changed or disabled:
    *   `app = FastAPI(docs_url="/mycustomdocs", redoc_url=None)` would serve Swagger UI at `/mycustomdocs` andisable ReDoc.

3.  **Swagger UI Parameters**: You can pass a dictionary of parameters to `swagger_ui_parameters` when creating the `FastAPI` instance to customize Swagger UI's behavior and appearance.
    *   **Disable Syntax Highlighting**: `FastAPI(swagger_ui_parameters={"syntaxHighlight": False})`
    *   **Change Syntax Highlighting Theme**: `FastAPI(swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}})`
    *   FastAPI has default parameters like `"deepLinking": True`, `"showExtensions": True`.
    *   A fullist of available Swagger UI configuration parameters can be found in the official Swagger UI documentation.

4.  **OAuth2 Integration**: The docs UI can integrate with OAuth2 for authentication, allowing users to authenticate and interact with protected endpoints directly from the docs. FastAPI provides `get_swagger_ui_oauth2_redirect_html()` for this.

5.  **Custom Static Assets**: For advanced customization or self-hosting, you can provide your own static assets (JS, CSS) for Swagger UI and ReDoc.

## Summary

FastAPI's automatic documentation is a powerful feature that significantly aids API development and consumption. By leveraging OpenAPI, Pydantic, and Python type hints, it generates interactive and informative documentation with minimal effort from the developer, while still offering avenues for customization.
