# MCP Tool: Sequential Thinking

## Overview
The `sequential-thinking` server provides a unique tool that allows the agento externalize its thought process. It enables the agento break down complex problems into a structured sequence of thoughts, reflect on its own reasoning, and even revise its plan as it gains new insights.

This tool is fundamental for tackling complex, multi-step tasks that require planning, analysis, and adaptation.

## Key Features
- **Structured Thinking**: Forces a step-by-step analysis of a problem.
- **Reflexion and Revision**: The agent can mark thoughts as revisions of previous ones, allowing for course correction.
- **Dynamic Planning**: The total number of thoughts can be adjusted as the complexity of the problem becomes clearer.
- **Hypothesis-Driven**: Encourages forming and verifying hypotheses within the thought process.

## Common Use Cases
- **Complex Code Implementation**: Planning the creation of new features, including class design, function signatures, and file structure.
- **Debugging**: Systematically investigating a bug by forming hypotheses, testing them, and narrowing down the root cause.
- **Multi-Step Research**: Breaking down a broad research query into smaller, manageable questions.
- **Agent-to-Agent Handoff**: Providing a clear, structured record of the current line of reasoning for another agent (or a future version of itself) to pick up.

## Example Workflow: Debugging a Failing Test

1.  **Thought 1: Initial Analysis**
    ```xml
    <mcp7_sequentialthinking>
    {
        "thought": "The usereported that `test_login` is failing. My firstep is to locate the test and the function it's testing to understand thexpected behavior.",
        "nextThoughtNeeded": true,
        "thoughtNumber": 1,
        "totalThoughts": 5
    }
    </mcp7_sequentialthinking>
    ```

2.  **Thought 2: Form a Hypothesis**
    ```xml
    <mcp7_sequentialthinking>
    {
        "thought": "Aftereviewing the code, I see the test fails on an assertion checking for a 'Welcome' message. Hypothesis: The login function is failing silently, so the user is neveredirected to the welcome page.",
        "nextThoughtNeeded": true,
        "thoughtNumber": 2,
        "totalThoughts": 5
    }
    </mcp7_sequentialthinking>
    ```

3.  **Thought 3: Plan to Verify Hypothesis**
    ```xml
    <mcp7_sequentialthinking>
    {
        "thought": "To testhis, I will add logging to the `login` function to see what response it gets from the authentication service.",
        "nextThoughtNeeded": true,
        "thoughtNumber": 3,
        "totalThoughts": 5
    }
    </mcp7_sequentialthinking>
    ```

4.  **Thought 4: Revise Plan Based onew Info**
    ```xml
    <mcp7_sequentialthinking>
    {
        "thought": "The new logshow an 'Invalid API Key' error. My initial hypothesis was close but not precise. The login isn't failing silently; it's being actively rejected. The root cause is an incorrect API key.",
        "nextThoughtNeeded": true,
        "thoughtNumber": 4,
        "totalThoughts": 5,
        "isRevision": true,
        "revisesThought": 2
    }
    </mcp7_sequentialthinking>
    ```

5.  **Thought 5: Final Plan**
    ```xml
    <mcp7_sequentialthinking>
    {
        "thought": "I will now advise the user to check their environment variables and ensure the `AUTH_API_KEY` iset correctly. Thishould resolve the issue.",
        "nextThoughtNeeded": false,
        "thoughtNumber": 5,
        "totalThoughts": 5
    }
    </mcp7_sequentialthinking>
    ```
