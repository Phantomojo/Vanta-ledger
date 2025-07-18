#!/usr/bin/env python3
"""
Optimized AI Processor for Vanta Ledger
=======================================

Smart AI document processing that works efficiently alongside Paperless-ngx,
with intelligent resource management and batch processing.
"""

import asyncio
import json
import logging
import requests
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingJob:
    """Document processing job"""
    document_id: int
    title: str
    content: str
    priority: int  # 1=high, 2=medium, 3=low
    created_at: datetime
    retry_count: int = 0

@dataclass
class ProcessingResult:
    """Processing result"""
    document_id: int
    success: bool
    analysis: Optional[Dict[str, Any]]
    error: Optional[str]
    processing_time: float
    timestamp: datetime

class ResourceManager:
    """Intelligent resource management"""
    
    def __init__(self, max_cpu_percent: float = 70, max_memory_percent: float = 80):
        self.max_cpu_percent = max_cpu_percent
        self.max_memory_percent = max_memory_percent
        self.processing_paused = False
        
    def check_system_resources(self) -> Tuple[bool, Dict[str, float]]:
        """Check if system has enough resources for AI processing"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3)
            }
            
            # Check if we should pause processing
            should_pause = (
                cpu_percent > self.max_cpu_percent or 
                memory.percent > self.max_memory_percent
            )
            
            if should_pause and not self.processing_paused:
                logger.info(f"⚠️ Pausing AI processing - CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%")
                self.processing_paused = True
            elif not should_pause and self.processing_paused:
                logger.info("✅ Resuming AI processing - resources available")
                self.processing_paused = False
            
            return not should_pause, metrics
            
        except Exception as e:
            logger.error(f"Error checking resources: {e}")
            return False, {}
    
    def get_optimal_batch_size(self, metrics: Dict[str, float]) -> int:
        """Determine optimal batch size based on system resources"""
        cpu_percent = metrics.get('cpu_percent', 0)
        memory_available = metrics.get('memory_available_gb', 0)
        
        if cpu_percent < 30 and memory_available > 8:
            return 5  # High capacity
        elif cpu_percent < 50 and memory_available > 4:
            return 3  # Medium capacity
        else:
            return 1  # Low capacity

class OptimizedOllamaClient:
    """Optimized Ollama client with connection pooling and retry logic"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.connection_pool = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20
        )
        self.session.mount('http://', self.connection_pool)
        self.session.mount('https://', self.connection_pool)
        
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 500, 
                         temperature: float = 0.3) -> Optional[str]:
        """Generate response with optimized settings"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": 0.9,
                    "max_tokens": max_tokens,
                    "num_predict": max_tokens
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None

class OptimizedAIProcessor:
    """Optimized AI processor with intelligent resource management"""
    
    def __init__(self, paperless_url: str, username: str, password: str,
                 ollama_url: str = "http://localhost:11434", model: str = "llama2"):
        self.paperless_url = paperless_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = None
        
        self.ollama_client = OptimizedOllamaClient(ollama_url, model)
        self.resource_manager = ResourceManager()
        
        self.job_queue = Queue()
        self.result_queue = Queue()
        self.processing_threads = []
        self.max_workers = 3
        self.running = False
        
        # Statistics
        self.stats = {
            'documents_processed': 0,
            'documents_failed': 0,
            'total_processing_time': 0,
            'avg_processing_time': 0,
            'start_time': None
        }
    
    async def authenticate(self) -> bool:
        """Authenticate with Paperless-ngx"""
        try:
            auth_url = f"{self.paperless_url}/api/token/"
            response = requests.post(
                auth_url,
                auth=requests.auth.HTTPBasicAuth(self.username, self.password)
            )
            
            if response.status_code == 200:
                self.token = response.json().get('token')
                logger.info("✅ Authenticated with Paperless-ngx")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def create_optimized_prompt(self, text: str, doc_type: str = "document") -> str:
        """Create an optimized prompt for faster processing"""
        # Truncate text to reduce processing time
        truncated_text = text[:1500] + "..." if len(text) > 1500 else text
        
        prompt = f"""Analyze this {doc_type} and provide a brief analysis in JSON format:

Document: {truncated_text}

Respond with JSON only:
{{
    "summary": "2-3 sentence summary",
    "key_points": ["point1", "point2"],
    "business_value": "low/medium/high",
    "action_required": "yes/no"
}}"""
        
        return prompt
    
    def process_document(self, job: ProcessingJob) -> ProcessingResult:
        """Process a single document"""
        start_time = time.time()
        
        try:
            # Check if we should pause processing
            can_process, metrics = self.resource_manager.check_system_resources()
            if not can_process:
                return ProcessingResult(
                    document_id=job.document_id,
                    success=False,
                    analysis=None,
                    error="System resources too high",
                    processing_time=time.time() - start_time,
                    timestamp=datetime.now()
                )
            
            # Create optimized prompt
            prompt = self.create_optimized_prompt(job.content, "document")
            
            # Generate AI response
            response = self.ollama_client.generate_response(prompt, max_tokens=300)
            
            if response:
                # Parse response
                try:
                    # Extract JSON from response
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                    else:
                        analysis = {
                            "summary": response[:200] + "..." if len(response) > 200 else response,
                            "key_points": [],
                            "business_value": "medium",
                            "action_required": "no"
                        }
                    
                    processing_time = time.time() - start_time
                    
                    return ProcessingResult(
                        document_id=job.document_id,
                        success=True,
                        analysis=analysis,
                        error=None,
                        processing_time=processing_time,
                        timestamp=datetime.now()
                    )
                    
                except Exception as e:
                    return ProcessingResult(
                        document_id=job.document_id,
                        success=False,
                        analysis=None,
                        error=f"Response parsing error: {e}",
                        processing_time=time.time() - start_time,
                        timestamp=datetime.now()
                    )
            else:
                return ProcessingResult(
                    document_id=job.document_id,
                    success=False,
                    analysis=None,
                    error="AI response generation failed",
                    processing_time=time.time() - start_time,
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return ProcessingResult(
                document_id=job.document_id,
                success=False,
                analysis=None,
                error=f"Processing error: {e}",
                processing_time=time.time() - start_time,
                timestamp=datetime.now()
            )
    
    def worker_thread(self):
        """Worker thread for processing documents"""
        while self.running:
            try:
                # Get job from queue with timeout
                job = self.job_queue.get(timeout=1)
                
                # Process the document
                result = self.process_document(job)
                
                # Put result in result queue
                self.result_queue.put(result)
                
                # Update statistics
                if result.success:
                    self.stats['documents_processed'] += 1
                else:
                    self.stats['documents_failed'] += 1
                
                self.stats['total_processing_time'] += result.processing_time
                self.stats['avg_processing_time'] = (
                    self.stats['total_processing_time'] / 
                    (self.stats['documents_processed'] + self.stats['documents_failed'])
                )
                
                # Mark job as done
                self.job_queue.task_done()
                
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    logger.error(f"Worker thread error: {e}")
    
    def start_processing(self):
        """Start the processing system"""
        if self.running:
            return
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Start worker threads
        for i in range(self.max_workers):
            thread = threading.Thread(target=self.worker_thread, daemon=True)
            thread.start()
            self.processing_threads.append(thread)
        
        logger.info(f"🚀 Started AI processing with {self.max_workers} workers")
    
    def stop_processing(self):
        """Stop the processing system"""
        self.running = False
        
        # Wait for threads to finish
        for thread in self.processing_threads:
            thread.join(timeout=5)
        
        self.processing_threads.clear()
        logger.info("🛑 Stopped AI processing")
    
    def add_job(self, document_id: int, title: str, content: str, priority: int = 2):
        """Add a document processing job"""
        job = ProcessingJob(
            document_id=document_id,
            title=title,
            content=content,
            priority=priority,
            created_at=datetime.now()
        )
        self.job_queue.put(job)
    
    def get_results(self) -> List[ProcessingResult]:
        """Get all available results"""
        results = []
        while not self.result_queue.empty():
            try:
                result = self.result_queue.get_nowait()
                results.append(result)
            except:
                break
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.stats.copy()
        if stats['start_time']:
            uptime = datetime.now() - stats['start_time']
            stats['uptime_seconds'] = uptime.total_seconds()
            stats['documents_per_hour'] = (
                (stats['documents_processed'] + stats['documents_failed']) / 
                (uptime.total_seconds() / 3600)
            ) if uptime.total_seconds() > 0 else 0
        
        stats['queue_size'] = self.job_queue.qsize()
        stats['results_available'] = self.result_queue.qsize()
        
        return stats

async def main():
    """Main function for testing"""
    processor = OptimizedAIProcessor(
        paperless_url="http://localhost:8000",
        username="Mike",
        password="your_password_here"  # You'll need to provide this
    )
    
    # Authenticate
    if not await processor.authenticate():
        print("❌ Authentication failed")
        return
    
    # Check if Ollama is available
    if not processor.ollama_client.is_available():
        print("❌ Ollama not available")
        return
    
    print("✅ AI processor ready")
    
    # Start processing
    processor.start_processing()
    
    # Add some test jobs
    test_documents = [
        {
            "id": 1,
            "title": "Test Invoice",
            "content": "This is a test invoice for construction materials worth KES 500,000."
        },
        {
            "id": 2,
            "title": "Test Contract",
            "content": "Construction contract for road maintenance project in Nairobi County."
        }
    ]
    
    for doc in test_documents:
        processor.add_job(doc["id"], doc["title"], doc["content"])
    
    # Process for a few seconds
    await asyncio.sleep(10)
    
    # Get results
    results = processor.get_results()
    print(f"\n📊 Processed {len(results)} documents:")
    
    for result in results:
        if result.success:
            print(f"✅ Document {result.document_id}: {result.analysis.get('summary', 'No summary')}")
        else:
            print(f"❌ Document {result.document_id}: {result.error}")
    
    # Get statistics
    stats = processor.get_statistics()
    print(f"\n📈 Statistics:")
    print(f"   Documents processed: {stats['documents_processed']}")
    print(f"   Documents failed: {stats['documents_failed']}")
    print(f"   Average processing time: {stats['avg_processing_time']:.2f}s")
    print(f"   Documents per hour: {stats['documents_per_hour']:.1f}")
    
    # Stop processing
    processor.stop_processing()

if __name__ == "__main__":
    asyncio.run(main()) 