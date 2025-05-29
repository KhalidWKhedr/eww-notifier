#!/bin/bash

# Kill any existing instances
pkill -f "python.*eww_notifier"

# Start the service
python3 -m eww_notifier & 