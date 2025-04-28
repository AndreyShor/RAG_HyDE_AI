import os
import time
from typing import List, Optional
from datetime import datetime

class SystemLogger:
    def __init__(self, basic_log_path: str, rag_log_path: str, hyde_log_path: str):
        self.basic_log_path = basic_log_path
        self.rag_log_path = rag_log_path
        self.hyde_log_path = hyde_log_path
        self.basic_counter = 0
        self.rag_counter = 0
        self.hyde_counter = 0

        self._initialize_log_file(self.basic_log_path, 'basic')
        self._initialize_log_file(self.rag_log_path, 'rag')
        self._initialize_log_file(self.hyde_log_path, 'hyde')

    def _initialize_log_file(self, path: str, mode: str):
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write('')
        else:
            with open(path, 'r') as f:
                content = f.read()
                if mode == 'basic':
                    self.basic_counter = content.count('///////// Record')
                elif mode == 'rag':
                    self.rag_counter = content.count('///////// Record')
                elif mode == 'hyde':
                    self.hyde_counter = content.count('///////// Record')

    def _format_text(self, text: str, max_length: int = 500) -> str:
        text = text.replace('\n', ' ').strip()
        words = text.split()
        lines = []
        line = ''
        for word in words:
            if len(line) + len(word) + 1 <= max_length:
                line += (' ' if line else '') + word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return '\n'.join(lines)

    def _current_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def log_basic(self, query: str, response: str, durationResponse: float):
        self.basic_counter += 1
        formatted_query = self._format_text(query)
        formatted_response = self._format_text(response)
        timestamp = self._current_timestamp()
        log_entry = (
            f"///////// Record {self.basic_counter} ////////////\n"
            f"Timestamp: {timestamp}\n\n"
            f"//////// Query:\n\n"
            f"{formatted_query}\n\n"
            f"//////// System Response:\n\n"
            f"{formatted_response}\n\n"
            f"//////// Time Taken to Response: {durationResponse:.2f} seconds\n\n"
        )
        with open(self.basic_log_path, 'a') as f:
            f.write(log_entry)

    def log_rag(self, query: str, vectors: Optional[List[str]], response: str, durationResponse: float, durationRAG: float):
        self.rag_counter += 1
        formatted_query = self._format_text(query)
        formatted_response = self._format_text(response)
        timestamp = self._current_timestamp()
        log_entry = (
            f"///////// Record {self.rag_counter} ////////////\n"
            f"Timestamp: {timestamp}\n\n"
            f"//////// Query:\n\n"
            f"{formatted_query}\n\n"
            f"//////// Vector Addition\n\n"
        )
        if vectors:
            for idx, vector_text in enumerate(vectors, 1):
                formatted_vector = self._format_text(vector_text)
                log_entry += f"//// Vector Addition {idx} \n\n{formatted_vector}\n\n"
        else:
            log_entry += "(No vector additions)\n\n"

        
        totalTime = durationResponse + durationRAG

        log_entry += (
            f"//////// System Response:\n\n"
            f"{formatted_response}\n\n"
            f"//////// Time for RAG generation: {durationRAG:.2f} seconds\n\n"
            f"//////// Time Taken to Response: {durationResponse:.2f} seconds\n\n"
            f"//////// Total Time: {totalTime:.2f} seconds\n\n"

        )
        with open(self.rag_log_path, 'a') as f:
            f.write(log_entry)

    def log_hyde(self, query: str, agent_addition: str, vectors: Optional[List[str]], response: str, durationResponse: float, durationRAG: float, durationAgent):
        self.hyde_counter += 1
        formatted_query = self._format_text(query)
        formatted_agent = self._format_text(agent_addition)
        formatted_response = self._format_text(response)
        timestamp = self._current_timestamp()
        log_entry = (
            f"///////// Record {self.hyde_counter} ////////////\n"
            f"Timestamp: {timestamp}\n\n"
            f"//////// Query:\n\n"
            f"{formatted_query}\n\n"
            f"//////// Agent Addition:\n\n"
            f"{formatted_agent}\n\n"
            f"//////// Vector Addition\n\n"
        )
        if vectors:
            for idx, vector_text in enumerate(vectors, 1):
                formatted_vector = self._format_text(vector_text)
                log_entry += f"//// Vector Addition {idx} \n\n{formatted_vector}\n\n"
        else:
            log_entry += "(No vector additions)\n\n"

        totalTime = durationResponse + durationAgent + durationRAG

        log_entry += (
            f"//////// System Response:\n\n"
            f"{formatted_response}\n\n"
            f"//////// Time for Agent Answering: {durationAgent:.2f} seconds\n\n"
            f"//////// Time for RAG generation: {durationRAG:.2f} seconds\n\n"
            f"//////// Time Taken to respond: {durationResponse:.2f} seconds\n\n"
            f"//////// Total Time: {totalTime:.2f} seconds\n\n"
        )
        with open(self.hyde_log_path, 'a') as f:
            f.write(log_entry)

# Example Usage:
if __name__ == "__main__":
    logger = SystemLogger('basic_log.txt', 'rag_log.txt', 'hyde_log.txt')

    # Basic log
    start_time = time.time()
    response = "Physics is the study of matter and energy – how they interact with each other and how the universe works. It's a broad field that investigates fundamental principles governing everything around us, from the smallest particles to the largest structures in the cosmos."
    duration = time.time() - start_time
    logger.log_basic("What is physics?", response, duration)

    # RAG log
    vectors = [
        "Physics is the most fundamental and all-inclusive of the sciences, and has had a profound effect on all scientific development...",
        "Physics is a foundational science for many other disciplines and plays a critical role in understanding the world."
    ]
    start_time = time.time()
    response = "Physics is the study of matter and energy – how they interact with each other and how the universe works."
    duration = time.time() - start_time
    logger.log_rag("What is physics?", vectors, response, duration)

    # HyDE log
    start_time = time.time()
    response = "Physics is the study of matter and energy – how they interact with each other and how the universe works."
    duration = time.time() - start_time
    logger.log_hyde("What is physics?", "Extension of user query explaining the broader aspects of physics.", vectors, response, duration)
