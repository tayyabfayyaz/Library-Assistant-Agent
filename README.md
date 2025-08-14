Goal: Make a Library Assistant using the OpenAI Agents SDK.

It should:

Search for books
Check book availability (only for registered members)
Give library timings
Ignore non-library questions
Must Use:

Agent
Runner.run / Runner.run_sync
@function_tool
@input_guardrail
RunContextWrapper
dynamic_instruction
BaseModel
ModelSettings
Steps:

User Context → Pydantic model with name and member_id.
Guardrail Agent → Stops non-library queries.
Input Guardrail Function → Uses guardrail agent.
Member Check Function → Allows availability tool only if user is valid.
Function Tools:

Search Book Tool → Returns if the book exists.
Check Availability Tool → Returns how many copies are available.
Dynamic Instructions → Personalize based on user name.
Library Agent → Add tools, guardrails, and model settings.
Book Database → Store book names and copies in a Python dictionary; tools must use this data.
Multiple Tools Handling → Make sure agent can search and check availability in one query.
Test with at least 3 queries and print results.






-------------------- Workflow Explanation ----------------------

Dynamic Instructions Setup

The dynamic_instructions function generates a string of instructions for the agent, customizing responses based on the user's context (e.g., name).
It guides the agent to:
Authenticate the user first.
Greet the user.
Handle book availability queries.
Restrict responses to library-related topics.
Agent Initialization

In main(), a UserInfo object is created for the current user.
An Agent is instantiated with:
A name ("Library Assistant").
The instructions from dynamic_instructions.
A list of tools/functions it can use (e.g., greeting, authentication, book data).
Input guardrails for validating user input.
Model settings for controlling response style.
User Interaction Loop

The program enters a loop, prompting the user for queries.
If the user types "exit", the loop breaks and the program ends.
Processing User Queries

For each query:
The agent processes the input using its tools and instructions.
The Runner.run method is called asynchronously, passing the agent, user input, configuration, and user context.
The agent:
Authenticates the user.
Greets the user.
Handles book-related queries using the appropriate tool.
Responds with a restriction message for unrelated queries.
Output

The agent’s final output is printed to the console.
Program Termination

When the user exits, a goodbye message is displayed.
Key Points
Authentication First: Every session starts by checking if the user is authenticated.
Context-Aware Responses: The agent uses the user's name and context for personalized messages.
Tool-Based Actions: The agent calls specific functions based on the query type.
Guardrails: Input is validated before processing.
Async Execution: The main function and agent run asynchronously for responsiveness.