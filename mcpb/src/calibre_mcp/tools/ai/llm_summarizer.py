"""LLM-powered book summarization for CalibreMCP.

Competing with Google NotebookLM but LOCAL, PRIVATE, and on YOUR 4090!

Features:
- Map-reduce summarization for 600+ page books
- Academic-style summaries with citations
- Cross-book queries ("compare X in books A, B, C")
- Local LLM via Ollama (no cloud sees your Bullshit Library)
"""

import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for local LLM."""
    
    base_url: str = "http://localhost:11434"  # Ollama default
    model: str = "llama3.1:70b-instruct-q4_K_M"  # Good for 4090 24GB
    timeout: int = 300  # 5 min for long generations
    temperature: float = 0.3  # Lower for factual summaries
    max_tokens: int = 4096
    

@dataclass
class ChunkInfo:
    """Information about a text chunk."""
    
    index: int
    text: str
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    chapter: Optional[str] = None


@dataclass
class SummaryResult:
    """Result of a summarization operation."""
    
    success: bool
    summary: str = ""
    chunks_processed: int = 0
    total_tokens: int = 0
    model_used: str = ""
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class LLMSummarizer:
    """LLM-powered summarization using local Ollama.
    
    Austrian efficiency meets 4090 power.
    """
    
    # Prompt templates
    CHUNK_SUMMARY_PROMPT = """You are summarizing a section of an academic book.
Extract the KEY FACTS, EVENTS, DATES, and ARGUMENTS. Be precise and factual.
Do NOT editorialize. Include page references where visible.

SECTION TEXT:
{chunk_text}

Provide a concise summary (3-5 paragraphs) of the key content:"""

    SYNTHESIS_PROMPT = """You are synthesizing multiple chapter summaries into a coherent document.
The goal is an ACADEMIC SUMMARY suitable for educated readers who want historical context.

TARGET AUDIENCE:
- Intelligent laypeople, not historians
- Need accessible language
- European context (may know more than Americans about WWII)

CHAPTER SUMMARIES:
{chapter_summaries}

INSTRUCTIONS:
Create a well-structured summary with:
1. Clear section headers
2. Factual, documented claims
3. No editorializing beyond what sources document
4. Acknowledgment of complexity (no "good guys vs bad guys")

OUTPUT FORMAT: Markdown with headers, ~{target_pages} pages when printed.

FINAL SUMMARY:"""

    ACADEMIC_SUMMARY_TEMPLATE = """# {title}
## Summary of: {source_title}
### Author: {author}

> **Source:** {full_citation}
> **Summary generated:** Local LLM ({model})
> **Note:** This is a condensed summary. Read the full book for complete documentation.

---

{content}

---

## Citation

{full_citation}

*Summary generated locally using {model}. No cloud services accessed.*
*Original work: ~{original_pages} pages → Summary: ~{summary_pages} pages*
"""

    CROSS_BOOK_QUERY_PROMPT = """You have access to content from multiple books.
Answer the query by synthesizing information across all sources.
ALWAYS cite which book each piece of information comes from.

QUERY: {query}

BOOK CONTENTS:
{book_contents}

Provide a comprehensive answer with citations to specific books:"""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the LLM summarizer.
        
        Args:
            config: LLM configuration. Defaults to local Ollama.
        """
        self.config = config or LLMConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._cache: dict[str, str] = {}
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
            )
        return self._client
        
    async def _generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate text using Ollama API.
        
        Args:
            prompt: The user prompt
            system: Optional system prompt
            
        Returns:
            Generated text
        """
        client = await self._get_client()
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await client.post(
                "/api/chat",
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e.response.status_code}")
            raise
        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama. Is it running?")
            raise RuntimeError(
                "Cannot connect to Ollama at {self.config.base_url}. "
                "Start it with: ollama serve"
            )
            
    async def check_ollama_status(self) -> dict[str, Any]:
        """Check if Ollama is running and which models are available.
        
        Returns:
            Status dict with available models
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            
            models = [m["name"] for m in data.get("models", [])]
            return {
                "status": "online",
                "models": models,
                "configured_model": self.config.model,
                "model_available": self.config.model in models or 
                                   any(self.config.model.split(":")[0] in m for m in models),
            }
        except Exception as e:
            return {
                "status": "offline",
                "error": str(e),
                "hint": "Start Ollama with: ollama serve",
            }
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 6000,
        overlap: int = 500,
    ) -> list[ChunkInfo]:
        """Split text into chunks for processing.
        
        Args:
            text: Full text to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of ChunkInfo objects
        """
        chunks = []
        
        # Try to split on chapter boundaries first
        chapter_pattern = r'(Chapter \d+|CHAPTER \d+|Part \d+|PART \d+|\n#{1,2} [^\n]+)'
        chapters = re.split(chapter_pattern, text)
        
        if len(chapters) > 3:
            # We found chapter markers - use them
            current_chunk = ""
            current_chapter = "Introduction"
            chunk_index = 0
            
            for i, part in enumerate(chapters):
                if re.match(chapter_pattern, part):
                    current_chapter = part.strip()
                    continue
                    
                if len(current_chunk) + len(part) > chunk_size:
                    if current_chunk:
                        chunks.append(ChunkInfo(
                            index=chunk_index,
                            text=current_chunk,
                            chapter=current_chapter,
                        ))
                        chunk_index += 1
                    current_chunk = part[-overlap:] if overlap else ""
                    
                current_chunk += part
                
            if current_chunk:
                chunks.append(ChunkInfo(
                    index=chunk_index,
                    text=current_chunk,
                    chapter=current_chapter,
                ))
        else:
            # No clear chapters - split by size with sentence boundaries
            sentences = re.split(r'(?<=[.!?])\s+', text)
            current_chunk = ""
            chunk_index = 0
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > chunk_size:
                    if current_chunk:
                        chunks.append(ChunkInfo(
                            index=chunk_index,
                            text=current_chunk,
                        ))
                        chunk_index += 1
                    # Keep overlap from previous chunk
                    current_chunk = current_chunk[-overlap:] if overlap else ""
                    
                current_chunk += sentence + " "
                
            if current_chunk.strip():
                chunks.append(ChunkInfo(
                    index=chunk_index,
                    text=current_chunk,
                ))
                
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    async def summarize_chunk(self, chunk: ChunkInfo) -> str:
        """Summarize a single chunk.
        
        Args:
            chunk: The chunk to summarize
            
        Returns:
            Summary text
        """
        # Check cache
        cache_key = hashlib.md5(chunk.text.encode()).hexdigest()
        if cache_key in self._cache:
            logger.debug(f"Cache hit for chunk {chunk.index}")
            return self._cache[cache_key]
            
        prompt = self.CHUNK_SUMMARY_PROMPT.format(chunk_text=chunk.text[:8000])
        
        chapter_context = f"Chapter: {chunk.chapter}\n" if chunk.chapter else ""
        system = f"""You are a precise academic summarizer.
{chapter_context}Extract facts, dates, names, and key arguments.
Be concise but thorough. Preserve important quotes."""
        
        summary = await self._generate(prompt, system)
        self._cache[cache_key] = summary
        
        return summary
    
    async def summarize_book(
        self,
        text: str,
        title: str,
        author: str,
        target_pages: int = 15,
        citation: Optional[str] = None,
    ) -> SummaryResult:
        """Summarize an entire book using map-reduce.
        
        This is the NotebookLM-killer feature!
        
        Args:
            text: Full book text
            title: Book title
            author: Book author
            target_pages: Target summary length in pages
            citation: Full citation for the book
            
        Returns:
            SummaryResult with the summary
        """
        try:
            # Check Ollama status first
            status = await self.check_ollama_status()
            if status["status"] != "online":
                return SummaryResult(
                    success=False,
                    error=f"Ollama not available: {status.get('error', 'Unknown error')}",
                )
                
            if not status.get("model_available"):
                return SummaryResult(
                    success=False,
                    error=f"Model {self.config.model} not found. Available: {status.get('models', [])}",
                )
            
            # Step 1: Chunk the text
            logger.info(f"Chunking '{title}' for summarization...")
            chunks = self.chunk_text(text)
            
            # Step 2: Map - summarize each chunk
            logger.info(f"Summarizing {len(chunks)} chunks (this may take a while)...")
            chunk_summaries = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}...")
                summary = await self.summarize_chunk(chunk)
                
                chapter_label = f"### {chunk.chapter}\n" if chunk.chapter else f"### Section {i+1}\n"
                chunk_summaries.append(f"{chapter_label}{summary}")
                
            # Step 3: Reduce - synthesize into final document
            logger.info("Synthesizing final summary...")
            combined_summaries = "\n\n---\n\n".join(chunk_summaries)
            
            synthesis_prompt = self.SYNTHESIS_PROMPT.format(
                chapter_summaries=combined_summaries,
                target_pages=target_pages,
            )
            
            system = f"""You are creating an academic summary of "{title}" by {author}.
Target audience: Educated laypeople seeking historical context.
Style: Academic but accessible. No propaganda. Let facts speak."""
            
            final_content = await self._generate(synthesis_prompt, system)
            
            # Step 4: Format with template
            full_citation = citation or f"{author}. {title}."
            
            final_summary = self.ACADEMIC_SUMMARY_TEMPLATE.format(
                title=f"Summary: {title}",
                source_title=title,
                author=author,
                full_citation=full_citation,
                model=self.config.model,
                content=final_content,
                original_pages=len(text) // 2500,  # Rough estimate
                summary_pages=target_pages,
            )
            
            return SummaryResult(
                success=True,
                summary=final_summary,
                chunks_processed=len(chunks),
                model_used=self.config.model,
                metadata={
                    "title": title,
                    "author": author,
                    "original_chars": len(text),
                    "summary_chars": len(final_summary),
                    "compression_ratio": len(text) / len(final_summary) if final_summary else 0,
                },
            )
            
        except Exception as e:
            logger.exception("Book summarization failed")
            return SummaryResult(
                success=False,
                error=str(e),
            )
    
    async def query_across_books(
        self,
        query: str,
        book_contents: dict[str, str],
    ) -> str:
        """Query across multiple books - the RAG dream!
        
        Args:
            query: User's question
            book_contents: Dict of {book_title: relevant_content}
            
        Returns:
            Answer with citations
        """
        formatted_contents = "\n\n".join(
            f"### {title}\n{content[:4000]}"  # Truncate per book
            for title, content in book_contents.items()
        )
        
        prompt = self.CROSS_BOOK_QUERY_PROMPT.format(
            query=query,
            book_contents=formatted_contents,
        )
        
        system = """You are a research assistant with access to multiple books.
Always cite which book information comes from.
Acknowledge when sources disagree.
Be precise and factual."""
        
        return await self._generate(prompt, system)
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Convenience functions for MCP tools

_summarizer: Optional[LLMSummarizer] = None


def get_summarizer() -> LLMSummarizer:
    """Get or create the global summarizer instance."""
    global _summarizer
    if _summarizer is None:
        _summarizer = LLMSummarizer()
    return _summarizer


async def summarize_book_content(
    text: str,
    title: str,
    author: str,
    target_pages: int = 15,
    citation: Optional[str] = None,
    model: Optional[str] = None,
) -> dict[str, Any]:
    """Summarize a book - MCP tool interface.
    
    Args:
        text: Full book text
        title: Book title  
        author: Book author
        target_pages: Target summary length
        citation: Full citation
        model: Override default model
        
    Returns:
        Dict with summary and metadata
    """
    summarizer = get_summarizer()
    
    if model:
        summarizer.config.model = model
        
    result = await summarizer.summarize_book(
        text=text,
        title=title,
        author=author,
        target_pages=target_pages,
        citation=citation,
    )
    
    return {
        "success": result.success,
        "summary": result.summary,
        "chunks_processed": result.chunks_processed,
        "model_used": result.model_used,
        "error": result.error,
        "metadata": result.metadata,
    }


async def check_llm_status() -> dict[str, Any]:
    """Check LLM availability - MCP tool interface."""
    summarizer = get_summarizer()
    return await summarizer.check_ollama_status()


async def query_books(
    query: str,
    book_contents: dict[str, str],
) -> dict[str, Any]:
    """Query across multiple books - MCP tool interface.
    
    This is the NotebookLM-killer!
    
    Args:
        query: User's question
        book_contents: Dict of {title: relevant_content}
        
    Returns:
        Dict with answer and sources
    """
    summarizer = get_summarizer()
    
    try:
        answer = await summarizer.query_across_books(query, book_contents)
        return {
            "success": True,
            "answer": answer,
            "sources": list(book_contents.keys()),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

