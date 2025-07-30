# MCP Tool: Playwright

## Overview
The `mcp-playwright` server provides a powerful set of tools for browser automation and web scraping, based on Microsoft's Playwright framework. It allows the agento control a webrowser programmatically to perform actions like navigating to pages, clicking elements, filling forms, and extracting data.

Playwright is particularly powerful because of its ability to interact with modern, complex web applications, including those built with frameworks like React, Vue, and Angular.

## Key Features
- **Cross-Browser Support**: Automate Chromium, Firefox, and WebKit.
- **Auto-Waits**: Automatically waits for elements to be ready before performing actions, eliminating a common source oflakiness in automation scripts.
- **Rich Selectors**: Locatelements by text, CSSelectors, XPath, and more.
- **Network Interception**: Intercept and modify network requests and responses.
- **Code Generation**: The `mcp4_start_codegen_session` tool can record browser interactions and generate Playwrightest scripts.

## Common Use Cases
- **Web Scraping**: Extracting data from websites that require JavaScripto render content.
- **Automated Testing**: Running end-to-end tests for web applications.
- **Task Automation**: Automating repetitive tasks like filling out forms or navigating through a site.
- **Generating Screenshots & PDFs**: Capturing web content for archival oreporting.

## Example Workflow: Searching a Website
Here is an example of how the agent might use `mcp-playwright` tools to search for information a website.

1.  **Navigate to the page:**
    ```xml
    <mcp4_playwright_navigate>
    {
        "url": "https://www.wikipedia.org/"
    }
    </mcp4_playwright_navigate>
    ```

2.  **Fill in the search input field:**
    ```xml
    <mcp4_playwright_fill>
    {
        "selector": "#searchInput",
        "value": "Artificial General Intelligence"
    }
    </mcp4_playwright_fill>
    ```

3.  **Press thenter key to submithe search:**
    ```xml
    <mcp4_playwright_press_key>
    {
        "key": "Enter",
        "selector": "#searchInput"
    }
    </mcp4_playwright_press_key>
    ```

4.  **Take a screenshot of the results:**
    ```xml
    <mcp4_playwright_screenshot>
    {
        "name": "wikipedia_search_results"
    }
    </mcp4_playwright_screenshot>
    ```

5.  **Extracthe visible text from the page:**
    ```xml
    <mcp4_playwright_get_visible_text>{}</mcp4_playwright_get_visible_text>
    ```

## Available Tools
For a fullist of available tools and their parameters, you can use the `list_resources` tool on the `mcp-playwright` server.

```xml
<list_resources>
{
    "ServerName": "mcp-playwright"
}
</list_resources>
```
