#!/bin/bash

# Default values
INTERFACE="eth0"
DEFAULT_DELAY=100  # Default delay value if no argument is passed

# Check if the user wants to stop the delay
if [ "$1" == "stop" ]; then
    echo "Removing network delay from ${INTERFACE}..."
    sudo tc qdisc del dev $INTERFACE root
    echo "Network delay removed."
    exit 0
fi

# Check if a delay argument was passed
if [ $# -eq 1 ]; then
    DELAY=$1
else
    DELAY=$DEFAULT_DELAY
fi

# Validate if the delay is a valid number
if ! [[ "$DELAY" =~ ^[0-9]+$ ]]; then
    echo "Error: Delay must be a positive integer."
    exit 1
fi

# Show the current configuration
echo "Applying a delay of ${DELAY}ms to the network interface ${INTERFACE}."

# Clear existing qdisc if any
echo "Removing existing qdisc..."
sudo tc qdisc del dev $INTERFACE root 2>/dev/null

# Add netem qdisc to introduce delay
echo "Adding netem delay..."
sudo tc qdisc add dev $INTERFACE root netem delay ${DELAY}ms

# Verify the change
echo "Network delay set to ${DELAY}ms."
sudo tc -s qdisc show dev $INTERFACE

exit 0

