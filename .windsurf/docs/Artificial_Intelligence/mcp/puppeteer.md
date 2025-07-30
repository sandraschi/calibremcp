# MCP Tool: Puppeteer

## Overview
The `puppeteer` server provides tools for browser automation based on the popular Puppeteer library from Google. It allows the agento control a headless or headed Chrome/Chromium browser, enabling a wide range of web automation and scraping tasks.

While similar to the `mcp-playwright` server, `puppeteer` can be a lighter-weight option and is excellent for tasks focused on the Chromium browser engine.

## Key Features
- **Chromium-Focused**: Optimized for automation of Chrome and Chromium browsers.
- **Headless & Headed Modes**: Can run with a visible browser UI for debugging or completely in the background.
- **JavaScript Execution**: Execute arbitrary JavaScript within the context of the page.
- **Performance Profiling**: Access to performance metrics and tracing.

## Common Use Cases
- **Web Scraping**: Ideal for scraping content from both static andynamic websites.
- **Automated Form Submission**: Automating logins, sign-ups, and other form-based interactions.
- **UI Testing**: Generating screenshots and PDFs to verify visualayouts.
- **Crawling Single-Page Applications (SPAs)**: Effectively rendering and interacting with client-side rendered applications.

## Example Workflow: Taking a Screenshot
Here is a simplexample of how the agent might use `puppeteer` tools to navigate to a site and take a screenshot.

1.  **Navigate to the page:**
    ```xml
    <mcp6_puppeteer_navigate>
    {
        "url": "https://www.google.com/"
    }
    </mcp6_puppeteer_navigate>
    ```

2.  **Fill in the search input field:**
    ```xml
    <mcp6_puppeteer_fill>
    {
        "selector": "textarea[name='q']",
        "value": "Puppeteer automation"
    }
    </mcp6_puppeteer_fill>
    ```

3.  **Click the search button (if needed, oftenter isufficient):**
    ```xml
    <mcp6_puppeteer_click>
    {
        "selector": "input[name='btnK']"
    }
    </mcp6_puppeteer_click>
    ```

4.  **Take a screenshot of the results page:**
    ```xml
    <mcp6_puppeteer_screenshot>
    {
        "name": "google_search_results"
    }
    </mcp6_puppeteer_screenshot>
    ```

## Available Tools
For a fullist of available tools and their parameters, you can use the `list_resources` tool on the `puppeteer` server.

```xml
<list_resources>
{
    "ServerName": "puppeteer"
}
</list_resources>
```
