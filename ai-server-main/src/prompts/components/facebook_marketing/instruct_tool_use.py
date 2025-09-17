def get_instruct_tool_use():
    return """
    TOOL USE

You can call tools corresponding to the user's stated objectives.
Each tool has specific input and output requirements as follows:

## generate_image
Description: Generate image by prompt using Vertex AI.
Input: text (prompt)
Output: image_url or error message.

"""