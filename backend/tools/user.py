from langchain_core.tools import tool


@tool
def get_user_age(name: str) -> str:
    """
    Use this tool to get the user's age based on their name.
    """
    if "bob" in name.lower():
        return "42 years old"
    return "41 years old"
