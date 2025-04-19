Create a Python module for a coding agent that does the following:

1. **Inputs**
   - `repo_path`: local path to a cloned GitHub repository
   - `prompt`: user-provided natural language instruction (e.g., “Add type annotations to all functions in utils/”)

2. **Step 1: Collect Code Context**
   - Recursively load `.py` files from the repo (limit to 5 files max or 2000 lines total for initial version)
   - Bundle them into a single input string with clear file separation, like:

     ```
     === FILE: path/to/file.py ===
     (file contents)
     ```

3. **Step 2: Prompt OpenAI**
   - Use the OpenAI Chat API to send a message with:
     - System prompt: “You are a code editor assistant. You receive source code and instructions for code improvements.”
     - User message: includes the file bundle and the user instruction
   - Ask OpenAI to respond with grouped file diffs in the format:

     ```
     === FILE: path/to/file.py ===
     (modified code for that file)
     ```

4. **Step 3**
