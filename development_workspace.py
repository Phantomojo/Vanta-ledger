#!/usr/bin/env python3
"""
Development Workspace for Vanta Ledger
======================================

Interactive development environment for building the AI system
while Paperless-ngx processes documents in the background.
"""

import asyncio
import json
import time
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

class DevelopmentWorkspace:
    """Interactive development workspace"""
    
    def __init__(self):
        self.running = True
        self.monitoring_active = False
        self.ai_processor_active = False
        
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*80)
        print("🚀 VANTA LEDGER - DEVELOPMENT WORKSPACE")
        print("="*80)
        print("📄 Paperless-ngx is processing documents in the background")
        print("🤖 AI system is ready for development and testing")
        print("="*80)
        print()
        print("🔧 DEVELOPMENT TOOLS:")
        print("  1. 📊 Start Real-Time Monitoring Dashboard")
        print("  2. 🤖 Test AI Document Processing")
        print("  3. 📈 View System Statistics")
        print("  4. 🔍 Check Paperless Processing Status")
        print("  5. 🧪 Run AI Integration Tests")
        print("  6. 📋 View Available Documents")
        print("  7. ⚙️  System Resource Check")
        print("  8. 🛠️  Development Utilities")
        print("  9. 📚 Documentation & Guides")
        print("  0. 🚪 Exit")
        print()
    
    def check_system_status(self) -> Dict[str, Any]:
        """Check overall system status"""
        status = {
            'paperless_running': False,
            'ollama_running': False,
            'llama2_available': False,
            'system_resources': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check Paperless
        try:
            response = requests.get("http://localhost:8000/api/", timeout=5)
            status['paperless_running'] = response.status_code == 200
        except:
            pass
        
        # Check Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            status['ollama_running'] = response.status_code == 200
            if status['ollama_running']:
                models = response.json().get('models', [])
                status['llama2_available'] = any('llama2' in model.get('name', '') for model in models)
        except:
            pass
        
        # Check system resources
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status['system_resources'] = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_usage_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
        except:
            pass
        
        return status
    
    def display_system_status(self):
        """Display current system status"""
        print("\n📊 SYSTEM STATUS CHECK")
        print("-" * 50)
        
        status = self.check_system_status()
        
        # Paperless Status
        print(f"📄 Paperless-ngx: {'✅ Running' if status['paperless_running'] else '❌ Stopped'}")
        
        # AI System Status
        print(f"🤖 Ollama: {'✅ Running' if status['ollama_running'] else '❌ Stopped'}")
        print(f"🦙 Llama2: {'✅ Available' if status['llama2_available'] else '❌ Unavailable'}")
        
        # System Resources
        resources = status.get('system_resources', {})
        if resources:
            print(f"\n💻 System Resources:")
            print(f"   CPU: {resources.get('cpu_percent', 0):.1f}%")
            print(f"   Memory: {resources.get('memory_percent', 0):.1f}% ({resources.get('memory_available_gb', 0):.1f} GB available)")
            print(f"   Disk: {resources.get('disk_usage_percent', 0):.1f}% ({resources.get('disk_free_gb', 0):.1f} GB free)")
        
        print(f"\n⏰ Last Check: {status['timestamp']}")
    
    def start_monitoring_dashboard(self):
        """Start the real-time monitoring dashboard"""
        print("\n📊 Starting Real-Time Monitoring Dashboard...")
        print("💡 This will show live updates of system resources and processing status")
        print("💡 Press Ctrl+C in the monitoring window to return here")
        print()
        
        try:
            # Start monitoring in a new process
            subprocess.run([sys.executable, "real_time_monitor.py", "--refresh", "5"])
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
        except Exception as e:
            print(f"❌ Error starting monitoring: {e}")
    
    def test_ai_processing(self):
        """Test AI document processing"""
        print("\n🤖 Testing AI Document Processing...")
        print("💡 This will test the optimized AI processor with sample documents")
        
        try:
            # Run the optimized AI processor test
            subprocess.run([sys.executable, "optimized_ai_processor.py"])
        except Exception as e:
            print(f"❌ Error testing AI processing: {e}")
    
    def check_paperless_status(self):
        """Check Paperless processing status"""
        print("\n📄 Checking Paperless-ngx Processing Status...")
        
        try:
            # Get document count
            response = requests.get("http://localhost:8000/api/documents/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                total_docs = data.get('count', 0)
                
                # Get recent documents
                recent_response = requests.get(
                    "http://localhost:8000/api/documents/",
                    params={'ordering': '-created', 'page_size': 10},
                    timeout=5
                )
                
                recent_count = 0
                if recent_response.status_code == 200:
                    recent_data = recent_response.json()
                    recent_count = len(recent_data.get('results', []))
                
                print(f"📊 Total Documents: {total_docs:,}")
                print(f"📊 Recent Documents: {recent_count}")
                print(f"📊 Processing Status: Active")
                
                # Show recent document titles
                if recent_response.status_code == 200:
                    recent_docs = recent_data.get('results', [])
                    if recent_docs:
                        print(f"\n📋 Recent Documents:")
                        for i, doc in enumerate(recent_docs[:5], 1):
                            title = doc.get('title', 'Untitled')
                            created = doc.get('created', '')[:10] if doc.get('created') else 'Unknown'
                            print(f"   {i}. {title} ({created})")
            else:
                print("❌ Could not connect to Paperless-ngx")
                
        except Exception as e:
            print(f"❌ Error checking Paperless status: {e}")
    
    def run_ai_tests(self):
        """Run AI integration tests"""
        print("\n🧪 Running AI Integration Tests...")
        
        try:
            # Test Ollama connection
            print("🔍 Testing Ollama connection...")
            subprocess.run([sys.executable, "test_ollama_integration.py"])
            
        except Exception as e:
            print(f"❌ Error running AI tests: {e}")
    
    def view_available_documents(self):
        """View available documents for processing"""
        print("\n📋 Available Documents for AI Processing...")
        
        try:
            response = requests.get("http://localhost:8000/api/documents/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                documents = data.get('results', [])
                
                if documents:
                    print(f"📊 Found {len(documents)} documents:")
                    print()
                    
                    for i, doc in enumerate(documents[:10], 1):
                        title = doc.get('title', 'Untitled')
                        doc_type = doc.get('document_type', 'Unknown')
                        created = doc.get('created', '')[:10] if doc.get('created') else 'Unknown'
                        file_size = doc.get('file_size', 0)
                        
                        print(f"   {i}. {title}")
                        print(f"      Type: {doc_type} | Created: {created} | Size: {file_size:,} bytes")
                        print()
                    
                    if len(documents) > 10:
                        print(f"   ... and {len(documents) - 10} more documents")
                else:
                    print("📭 No documents found")
            else:
                print("❌ Could not fetch documents")
                
        except Exception as e:
            print(f"❌ Error viewing documents: {e}")
    
    def system_resource_check(self):
        """Detailed system resource check"""
        print("\n⚙️ Detailed System Resource Check...")
        
        try:
            import psutil
            
            # CPU Information
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            print(f"💻 CPU Information:")
            print(f"   Usage: {cpu_percent:.1f}%")
            print(f"   Cores: {cpu_count}")
            if cpu_freq:
                print(f"   Frequency: {cpu_freq.current:.0f} MHz")
            
            # Memory Information
            memory = psutil.virtual_memory()
            print(f"\n🧠 Memory Information:")
            print(f"   Total: {memory.total / (1024**3):.1f} GB")
            print(f"   Used: {memory.used / (1024**3):.1f} GB ({memory.percent:.1f}%)")
            print(f"   Available: {memory.available / (1024**3):.1f} GB")
            
            # Disk Information
            disk = psutil.disk_usage('/')
            print(f"\n💾 Disk Information:")
            print(f"   Total: {disk.total / (1024**3):.1f} GB")
            print(f"   Used: {disk.used / (1024**3):.1f} GB ({disk.percent:.1f}%)")
            print(f"   Free: {disk.free / (1024**3):.1f} GB")
            
            # Process Information
            print(f"\n🔄 Active Processes:")
            paperless_processes = 0
            ollama_processes = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = proc.info['name'].lower()
                    if 'paperless' in name:
                        paperless_processes += 1
                    elif 'ollama' in name:
                        ollama_processes += 1
                except:
                    pass
            
            print(f"   Paperless processes: {paperless_processes}")
            print(f"   Ollama processes: {ollama_processes}")
            
        except Exception as e:
            print(f"❌ Error checking system resources: {e}")
    
    def development_utilities(self):
        """Development utilities menu"""
        while True:
            print("\n🛠️ DEVELOPMENT UTILITIES")
            print("-" * 30)
            print("  1. 🔧 Install Dependencies")
            print("  2. 🧹 Clean Cache Files")
            print("  3. 📊 Generate System Report")
            print("  4. 🔄 Restart Services")
            print("  5. 📁 View Project Structure")
            print("  0. ↩️  Back to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                print("\n🔧 Installing dependencies...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "ai_requirements.txt"])
                
            elif choice == "2":
                print("\n🧹 Cleaning cache files...")
                if os.path.exists("cache"):
                    subprocess.run(["rm", "-rf", "cache/*"])
                    print("✅ Cache cleaned")
                
            elif choice == "3":
                print("\n📊 Generating system report...")
                status = self.check_system_status()
                report_file = f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(report_file, 'w') as f:
                    json.dump(status, f, indent=2)
                print(f"✅ Report saved to: {report_file}")
                
            elif choice == "4":
                print("\n🔄 Restarting services...")
                print("💡 This will restart Paperless-ngx and Ollama")
                confirm = input("Are you sure? (y/N): ").lower()
                if confirm == 'y':
                    subprocess.run(["sudo", "docker", "restart", "paperless-ngx"])
                    subprocess.run(["sudo", "systemctl", "restart", "ollama"])
                    print("✅ Services restarted")
                
            elif choice == "5":
                print("\n📁 Project Structure:")
                subprocess.run(["tree", "-L", "2", "-I", "__pycache__|*.pyc|.git"])
                
            elif choice == "0":
                break
    
    def documentation_guides(self):
        """Show documentation and guides"""
        print("\n📚 DOCUMENTATION & GUIDES")
        print("-" * 30)
        print("📖 Available Documentation:")
        print("  • MAXIMIZATION_GUIDE.md - Complete system optimization guide")
        print("  • PAPERLESS_RESEARCH.md - Paperless-ngx API research")
        print("  • AI_SYSTEM_README.md - AI system documentation")
        print("  • README.md - Project overview")
        print()
        print("🔗 Quick Links:")
        print("  • Paperless-ngx Web UI: http://localhost:8000")
        print("  • Ollama API: http://localhost:11434")
        print("  • Project Directory: /home/phantomojo/Vanta-ledger")
        print()
        print("💡 Development Tips:")
        print("  • Let Paperless finish processing before heavy AI analysis")
        print("  • Monitor system resources during development")
        print("  • Use the real-time monitor to track progress")
        print("  • Test AI features with small document batches first")
    
    def run(self):
        """Run the development workspace"""
        print("🚀 Welcome to Vanta Ledger Development Workspace!")
        print("💡 Paperless-ngx is processing documents in the background")
        print("💡 You can continue development while it works")
        
        while self.running:
            try:
                self.display_menu()
                choice = input("Select option: ").strip()
                
                if choice == "1":
                    self.start_monitoring_dashboard()
                elif choice == "2":
                    self.test_ai_processing()
                elif choice == "3":
                    self.display_system_status()
                elif choice == "4":
                    self.check_paperless_status()
                elif choice == "5":
                    self.run_ai_tests()
                elif choice == "6":
                    self.view_available_documents()
                elif choice == "7":
                    self.system_resource_check()
                elif choice == "8":
                    self.development_utilities()
                elif choice == "9":
                    self.documentation_guides()
                elif choice == "0":
                    print("\n👋 Goodbye! Happy coding!")
                    self.running = False
                else:
                    print("❌ Invalid option. Please try again.")
                
                if self.running:
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Happy coding!")
                self.running = False
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")

def main():
    """Main function"""
    # Import requests here to avoid import issues
    global requests
    import requests
    
    workspace = DevelopmentWorkspace()
    workspace.run()

if __name__ == "__main__":
    main() 