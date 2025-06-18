from python.utils.enums.dialog_style import DialogStyle

SAMP_DLIALOG_MAX_FULL_TEXT_LENGHT = 4096
SAMP_DIALOG_MAX_ROW_CHAR = 256

NEXT: str = ">>>"
NEXT_AND_BACK: str = ">>>\n<<<"
BACK: str = "<<<"
NEW_ROW: str = "\n"

# Total length of markers used in the chunk pagination
MARKER_LENGTH_TOTAL = len(NEXT) + len(NEXT_AND_BACK) + len(BACK)

def calculate_effective_length(text: str) -> int:
    """Calculate length excluding tabs and newline characters."""
    return len(text) - text.count("\t") - text.count("\n")

def __chunk_and_trim_lines(content: str, max_item: int) -> list[str]:
    """Chunk content into groups of max_item lines and trim if over character limit."""
    lines = content.split("\n")
    chunks = []
    i = 0
    
    while i < len(lines):
        # Create an initial chunk of up to `max_item` lines, truncating each line to `SAMP_DIALOG_MAX_ROW_CHAR`
        chunk_lines = [line[:SAMP_DIALOG_MAX_ROW_CHAR] for line in lines[i:i + max_item]]
        chunk = '\n'.join(chunk_lines)
        
        # Calculate chunk length excluding tab and newline characters
        effective_length = calculate_effective_length(chunk)
        
        # Trim lines from the chunk if it exceeds the character limit
        while effective_length > SAMP_DLIALOG_MAX_FULL_TEXT_LENGHT - MARKER_LENGTH_TOTAL and len(chunk_lines) > 1:
            chunk_lines.pop()  # Remove the last line to fit limit
            chunk = '\n'.join(chunk_lines)
            effective_length = calculate_effective_length(chunk)
        
        chunks.append(chunk)  # Finalized chunk
        i += len(chunk_lines)  # Move to next set of lines
    
    return chunks

def paginate_or_trim_content(dialog_style, content: str, max_list_item_per_page: int) -> list[str]:
    """Paginate or trim content based on dialog style and max items per page."""
    # Return trimmed content if dialog_style is unsupported
    if dialog_style not in [DialogStyle.LIST, DialogStyle.TABLIST, DialogStyle.TABLIST_HEADERS]:
        return [content[:SAMP_DLIALOG_MAX_FULL_TEXT_LENGHT]]
    
    # Chunk and trim content, then add appropriate markers to each chunk
    splitup = __chunk_and_trim_lines(content, max_list_item_per_page)
    pages = len(splitup)
    
    if pages == 1:
        return splitup

    paged_conent = [
        # Trim any trailing \n and reapply NEW_ROW and markers for correct pagination display
        chunk.rstrip(NEW_ROW) + NEW_ROW + 
        (NEXT if i == 0 else BACK if i == pages - 1 else NEXT_AND_BACK)
        for i, chunk in enumerate(splitup)
    ]
    
    return paged_conent
