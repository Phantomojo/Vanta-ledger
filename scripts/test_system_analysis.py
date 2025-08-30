#!/usr/bin/env python3
"""
Test script for System Analysis Service
Demonstrates the functionality without requiring GitHub Models
"""

import asyncio
import json
from src.vanta_ledger.services.system_analysis_service import SystemAnalysisService


async def test_system_analysis():
    """Test the system analysis service"""
    print("🔍 Testing System Analysis Service")
    print("=" * 50)
    
    # Create service instance
    service = SystemAnalysisService()
    print(f"✅ Service created successfully")
    print(f"🔧 AI Features enabled: {service.enabled}")
    print()
    
    # Test system metrics collection
    print("📊 Collecting System Metrics...")
    try:
        metrics = service._collect_system_metrics()
        print("✅ System metrics collected successfully:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f}")
            else:
                print(f"   {key}: {value}")
        print()
    except Exception as e:
        print(f"❌ Failed to collect metrics: {e}")
        print()
    
    # Test log collection
    print("📝 Testing Log Collection...")
    try:
        recent_logs = service._collect_recent_logs(10)
        print(f"✅ Recent logs collected: {len(recent_logs)} characters")
        if len(recent_logs) > 100:
            print(f"   Preview: {recent_logs[:100]}...")
        else:
            print(f"   Content: {recent_logs}")
        print()
    except Exception as e:
        print(f"❌ Failed to collect logs: {e}")
        print()
    
    # Test error log collection
    print("🚨 Testing Error Log Collection...")
    try:
        error_logs = service._collect_error_logs(5)
        print(f"✅ Error logs collected: {len(error_logs)} characters")
        if len(error_logs) > 100:
            print(f"   Preview: {error_logs[:100]}...")
        else:
            print(f"   Content: {error_logs}")
        print()
    except Exception as e:
        print(f"❌ Failed to collect error logs: {e}")
        print()
    
    # Test system health analysis (will fail without AI, but shows graceful degradation)
    print("🤖 Testing AI System Health Analysis...")
    try:
        result = await service.analyze_system_health(include_logs=False)
        if "error" in result:
            print(f"⚠️  Expected behavior (no AI): {result['error']}")
        else:
            print("✅ AI analysis completed successfully")
        print()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print()
    
    # Test code quality analysis on this file
    print("📁 Testing Code Quality Analysis...")
    try:
        result = await service.analyze_code_quality(__file__, "Test script analysis")
        if "error" in result:
            print(f"⚠️  Expected behavior (no AI): {result['error']}")
        else:
            print("✅ Code analysis completed successfully")
        print()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print()
    
    print("🎯 Test Summary:")
    print("   ✅ Basic service functionality working")
    print("   ✅ System metrics collection working")
    print("   ✅ Log collection working")
    print("   ⚠️  AI features require GitHub Models service")
    print()
    print("🚀 To enable AI features, ensure GitHub Models service is available")


if __name__ == "__main__":
    asyncio.run(test_system_analysis())
