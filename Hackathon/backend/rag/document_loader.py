import re
from pathlib import Path
from backend.config import DOCUMENTS_DIR

class DocumentLoader:
    """
    Loads and chunks institutional policy documents from disk with structural metadata.
    """
    def __init__(self, docs_dir=None):
        self.docs_dir = docs_dir or DOCUMENTS_DIR

    def load_documents(self) -> list:
        chunks = []
        doc_files = list(self.docs_dir.glob("*.md")) + list(self.docs_dir.glob("*.txt"))
        
        for file_path in doc_files:
            text = file_path.read_text(encoding="utf-8")
            doc_title = file_path.stem.replace("_", " ").title()
            
            # Split by markdown headers
            sections = re.split(r'\n(?=##?\s+)', text)
            for i, sec in enumerate(sections):
                sec = sec.strip()
                if not sec:
                    continue
                
                # Extract header title if present
                first_line = sec.split("\n")[0].replace("#", "").strip()
                chunks.append({
                    "id": f"{file_path.stem}_{i}",
                    "source": file_path.name,
                    "doc_title": doc_title,
                    "section": first_line,
                    "content": sec
                })
        return chunks
