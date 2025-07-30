from typing import Dict, List


def chunk_text(
    text: str, url: str, title: str, max_chunk_size: int = 1000, overlap_size: int = 100
) -> List[Dict]:
    """
    긴 텍스트를 지정된 크기와 오버랩으로 청크로 나눕니다.
    """
    chunks = []
    current_position = 0

    while current_position < len(text):
        end_position = min(current_position + max_chunk_size, len(text))
        chunk = text[current_position:end_position]

        if end_position < len(text):
            last_space = chunk.rfind(" ")
            last_newline = chunk.rfind("\n")

            if last_newline != -1 and (len(chunk) - last_newline) < overlap_size:
                end_position = current_position + last_newline + 1
                chunk = text[current_position:end_position]
            elif last_space != -1 and (len(chunk) - last_space) < overlap_size:
                end_position = current_position + last_space + 1
                chunk = text[current_position:end_position]

        chunks.append(
            {
                "content": chunk.strip(),
                "metadata": {
                    "url": url,
                    "title": title,
                    "start_index": current_position,
                    "end_index": end_position,
                },
            }
        )

        current_position = (
            end_position - overlap_size if end_position < len(text) else end_position
        )
        if current_position < 0:
            current_position = 0

    return chunks
