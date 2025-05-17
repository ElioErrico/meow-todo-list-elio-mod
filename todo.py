
import os
import pandas as pd


todo_csv_path = os.path.join(
    os.path.dirname(__file__), "todo.csv"
)


def stringify_todos(todos, user_id=None):
    # Filter todos by user if user_id is provided
    if user_id:
        user_todos = [t for t in todos if 'user' not in t or t['user'] == user_id]
    else:
        user_todos = todos
        
    if len(user_todos) == 0:
        return "Your todo is empty."
    
    out = "### Todo list:"
    for t in user_todos:
        # Add user info if available and not filtering by user
        user_info = f" (by {t['user']})" if 'user' in t and not user_id else ""
        out += f"\n - {t['description']}{user_info}"

    return out


def get_todos():
    if not os.path.exists(todo_csv_path):
        # Create empty dataframe with the correct columns
        df = pd.DataFrame(columns=["created", "description", "user"])
        df.to_csv(todo_csv_path, index=False)
        return []
    else:
        try:
            df = pd.read_csv(todo_csv_path)
            # Handle case where file exists but is empty
            if df.empty or len(df.columns) == 0:
                df = pd.DataFrame(columns=["created", "description", "user"])
                df.to_csv(todo_csv_path, index=False)
            return df.to_dict(orient="records")
        except pd.errors.EmptyDataError:
            # Handle empty file error
            df = pd.DataFrame(columns=["created", "description", "user"])
            df.to_csv(todo_csv_path, index=False)
            return []

    
def save_todos(todos):
    if len(todos) == 0:
        os.remove(todo_csv_path)
    else:
        pd.DataFrame(todos).to_csv(todo_csv_path, index=False)