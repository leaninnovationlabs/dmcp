#!/bin/bash

# Script to kill all running Python processes
# Author: Generated for DBMCP project
# Usage: ./kill_python.sh

echo "🔍 Searching for running Python processes..."

# Get all Python processes
python_processes=$(ps aux | grep python | grep -v grep | grep -v "kill_python.sh")

if [ -z "$python_processes" ]; then
    echo "✅ No Python processes found running."
    exit 0
fi

echo "📋 Found the following Python processes:"
echo "----------------------------------------"
echo "$python_processes"
echo "----------------------------------------"

# Count processes
process_count=$(echo "$python_processes" | wc -l)
echo "Total Python processes: $process_count"

# Ask for confirmation
read -p "⚠️  Do you want to kill all these Python processes? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Killing Python processes..."
    
    # Kill processes gracefully first (SIGTERM)
    pkill -f python
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Check if any processes are still running
    remaining=$(ps aux | grep python | grep -v grep | grep -v "kill_python.sh")
    
    if [ -n "$remaining" ]; then
        echo "⚠️  Some processes didn't stop gracefully. Force killing..."
        pkill -9 -f python
        sleep 1
    fi
    
    # Final check
    final_check=$(ps aux | grep python | grep -v grep | grep -v "kill_python.sh")
    
    if [ -z "$final_check" ]; then
        echo "✅ All Python processes have been terminated successfully."
    else
        echo "❌ Some processes may still be running:"
        echo "$final_check"
    fi
else
    echo "❌ Operation cancelled. No processes were killed."
fi
