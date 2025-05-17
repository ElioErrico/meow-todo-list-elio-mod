from pydantic import BaseModel
from ast import literal_eval
import time

from cat.mad_hatter.decorators import tool, hook
from cat.log import log

from .todo import get_todos, save_todos, stringify_todos


@tool(return_direct=True)
def add_todo(todo, cat):
    """Add item or multiple items to the todo list. User may say "Remeber to..." or similar. Input is an array of items."""

    try:
        todo = literal_eval(todo)
    except Exception as e:
        log(e, "ERROR")
        return f"Sorry there was an error: {e}. Can you ask in a different way?"
    todos = get_todos()
    for elem in todo:
        todos.append({
            "created": time.time(),
            "description": str(elem),
            "user": cat.user_id  # Add user_id to track which user created the todo
        })

    save_todos(todos)

    return f"Todo list updated with: *{', '.join(todo)}*"


@tool(return_direct=True)
def remove_todo(todo, cat):
    """Remove / delete item or multiple items from the todo list. Input is the array of items to remove."""
    todos = get_todos()
    
    # Filter todos for current user if user_id is available
    user_id = cat.user_id
    user_todos = todos
    if user_id:
        # Create a list with index and description for user's todos only
        user_todos_with_index = [(idx, t) for idx, t in enumerate(todos) 
                                if 'user' not in t or t['user'] == user_id]
        
        if not user_todos_with_index:
            return "You don't have any todos in the list."
            
        # TODO: should we use embeddings?
        prompt = "Given this list of items:"
        for i, (t_index, t) in enumerate(user_todos_with_index):
            prompt += f"\n {i}. {t['description']}"
        prompt += f"\n\nThe most similar items to `{todo}` are items number... (reply ONLY with an array with the number or numbers, no letters or points)"
        
        try:
            to_remove = cat.llm(prompt)
            selected_indices = literal_eval(to_remove)
            # Map the selected indices back to the original indices
            index_to_remove = [user_todos_with_index[i][0] for i in selected_indices if i < len(user_todos_with_index)]
            todos = [el for idx, el in enumerate(todos) if idx not in index_to_remove]
            save_todos(todos)
        except Exception as e:
            log(e, "ERROR")
            return f"Sorry there was an error: {e}. Can you ask in a different way?"
    
    return stringify_todos(todos, user_id)


@tool(return_direct=True)
def list_todo(query, cat):
    """List what is in the todo list. Input is a string used to filter the list."""
    
    todos = get_todos()
    # Pass the user_id to stringify_todos to filter by user
    return stringify_todos(todos, cat.user_id)


@tool(return_direct=True)
def clear_user_todos(confirmation, cat):
    """Delete all todo items for the current user. Input should be 'delete all' to confirm deletion."""
    
    if confirmation.lower() not in ['yes', 'confirm', 'delete all', 'clear all']:
        return "To delete all your todo items, please confirm by saying 'yes'."
    
    user_id = cat.user_id
    if not user_id:
        return "Unable to identify your user ID. Cannot clear todos."
    
    todos = get_todos()
    initial_count = len(todos)
    
    # Keep only todos that don't belong to the current user
    filtered_todos = [t for t in todos if 'user' in t and t['user'] != user_id]
    
    # Calculate how many items were removed
    removed_count = initial_count - len(filtered_todos)
    
    # Save the filtered list
    save_todos(filtered_todos)
    
    if removed_count > 0:
        return f"Successfully deleted all your todo items. {removed_count} item(s) removed."
    else:
        return "You don't have any todo items to delete."
