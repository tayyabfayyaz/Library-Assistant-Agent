import os
from dotenv import load_dotenv
from agents import Agent, RunConfig, RunContextWrapper, OpenAIChatCompletionsModel, function_tool, Runner, GuardrailFunctionOutput, input_guardrail, InputGuardrailTripwireTriggered, TResponseInputItem, ModelSettings
from pydantic import BaseModel
from openai import AsyncOpenAI
import asyncio

load_dotenv()

gemeini_api_key = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key = gemeini_api_key,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client,
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled = True,
)

class InputGuardrail(BaseModel):
    query_is_not_related: bool
    resoning: str

class UserInfo(BaseModel):
    name: str
    user_id: int

class BookInfo(BaseModel):
    book_name: str
    book_id: int
    quantity: int

guardrail_agent = Agent[InputGuardrail](
    name="Guardrail Agent",
    instructions="You are a guardrail agent that checks if the user query is related to library or not. If the query is related to library then return `query_is_related` as True and `resoning` as 'The query is related to library'. If the query is not related to library then return `query_is_related` as False and `resoning` as 'The query is not related to library'.",
    output_type=InputGuardrail,
)


@input_guardrail()
async def check_user_input(ctx: RunContextWrapper[InputGuardrail], agent: Agent, user_input)-> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, user_input, run_config=config, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.query_is_not_related,
    )

# BOOK'S DATABASE FUNCTION TOOL
def _book_database() -> list[dict]:
    """
    Returns a list of available books in the library.
    """
    return [
        {"book_name": "Python Programming", "book_id": 1, "quantity": 5},
        {"book_name": "Learning JavaScript", "book_id": 2, "quantity": 3},
        {"book_name": "Introduction to Machine Learning", "book_id": 3, "quantity": 0},
        {"book_name": "Data Science Handbook", "book_id": 4, "quantity": 2},
    ]

@function_tool()
def book_data() -> list[dict]:
    """ return the book's data """
    return _book_database()


# USER AUTHENTICATION FUNCTION TOOL
@function_tool
async def check_user_authentication(ctx: RunContextWrapper[UserInfo]) -> str:
    """Check if the user is authenticated based on context data."""
    if ctx.context.name == "Tayyab" and ctx.context.user_id == 12345:
        return f"✅ User {ctx.context.name} is authenticated."
    else:
        return f"❌ User {ctx.context.name} is not authenticated. Please check your credentials."

# BOOK SEARCHING FUNCTION TOOL
@function_tool
async def search_book_tool(book_name: str) -> str:
    """Search for a book in the library database."""

    if not book_name or not book_name.strip():
        return "⚠ Please provide a valid book name."
    
    books = _book_database()
    target = book_name.strip().lower()

    for book in books:
        if book["book_name"].lower() == target:
            return f'The book "{book["book_name"]} is available.'
        else:
            return f'The book "{book_name}" is not found in our database.'
    return f'❌ The book "{book_name}" is not found in our database.'


# BOOK AVAILABILITY CHECK FUNCTION TOOL
@function_tool()
async def check_book_availability(book_name: str) -> str:
    """
    Check how many copies of a book are available.
    NOTE: We do NOT call another tool here. We use the helper _books_data().
    """
    if not book_name or not book_name.strip():
        return "⚠ Please provide a valid book name."

    books = _book_database()  # <-- use helper, not the tool
    target = book_name.strip().lower()

    for book in books:
        if book["book_name"].lower() == target:
            qty = book["quantity"]
            if qty > 0:
                return f"✅ The book '{book['book_name']}' is available with {qty} copies."
            else:
                return f"❌ The book '{book['book_name']}' is currently out of stock."

    return f"❌ The book '{book_name}' is not found in our database."    

@function_tool
async def greeting(ctx: RunContextWrapper[UserInfo]) -> str:
    """A simple greeting function."""
    return f"Hello {ctx.context.name}, How can I assist you today?"

# DYNAMIC INSTRUCTIONS FUNCTION
def dynamic_instructions(ctx: RunContextWrapper[UserInfo], agent=Agent) -> str:
    return f"You are a helpful library assistant. when you run firstly call the user authetication function if user is autheticated so go to next step otherwise shows `{ctx.context.name} Please enter valid details`, then call the greeting function. When user asks for the available copies of books you call the `check_book_availability` function with the book name. if user asks about the book available or not you access the `search_book_tool` function with the name of book. If a user asks about any unrelated query of book library you shows `{ctx.context.name} I am only library assistant I can't talk about any other topic.` "

async def main():
    user_info = UserInfo(name="Tayyab", user_id=12345)
    agent = Agent[UserInfo](
        name="Library Assistant",
        instructions=dynamic_instructions,
        tools=[greeting, check_user_authentication ,book_data, check_book_availability],
        input_guardrails=[check_user_input],
        model_settings=ModelSettings(temperature=0.2, max_tokens=200, tool_choice="auto")
    )
    while True:
        user_input = input("Enter your query related to library (type 'exit' to quit): ")
        if user_input.strip().lower() == "exit":
            print("Exiting Library Assistant. Goodbye!")
            break
        result = await Runner.run(agent, user_input, run_config=config, context=user_info)
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())




