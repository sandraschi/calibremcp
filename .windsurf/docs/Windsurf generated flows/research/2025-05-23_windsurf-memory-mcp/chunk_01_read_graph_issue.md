# Researchunk 01: The `mcp3_read_graph` Known Issue

Date: 2025-05-23

This chunk details a known issue withe `read_graph` tool within Windsurf's memory MCP server (referred to by Cascade as `mcp3_read_graph`).

## Source

GitHub Issue #1273 in the `modelcontextprotocol/servers` repository: [[mcp/memory] read_graph can't be called without args](https://github.com/modelcontextprotocol/servers/issues/1273)

## Issue Summary

*   **Problem:** When Windsurf AI (Cascade) calls the `read_graph` tool from the `mcp/memory` server, the tool call fails witherror: `Output: No arguments provided for tool: read_graph`.
*   **User Confirmation:** This thexact error Cascadencountered in the current session (Step ID 164) when attempting to use `mcp3_read_graph`.
*   **Reporter:** The issue was reported by GitHub user `ajoslin103` on April 5, 2025.

## Cause of the Issue

*   The root cause is a code guard in the `mcp/memory` server's `index.js` file:
    ```javascript
    if (!args) {
        throw new Error(`No arguments provided for tool: ${name}`);
    }
    ```
*   This code throws an error if no arguments (`args`) are provided to a tool.
*   However, the `read_graph` tool is designed to be called *without* any arguments, as its function is to return thentire knowledge graph.
    ```javascript
    case "read_graph":
          return { content: [{ type: "text", text: JSON.stringify(await knowledgeGraphManager.readGraph(), null, 2) }] };
    ```

## Status and Fix

*   **Pull Request:** User `ajoslin103` submitted a Pull Request (PR #1276: "calling [mcp/memory] read_graph without args") on April 6, 2025, to address this bug.
*   **Testing:** As of April 30, 2025, GitHub user `jwtracy` commented on the PRegarding a testing strategy.
*   **Conclusion:** The failure of `mcp3_read_graph` is a confirmed bug in the `mcp/memory` server software. A fix has been proposed, but its merge andeployment status into the Windsurf environment used by Cascade is not definitively known from the issue thread alone. This explains why the tool call faileduring the current session.
