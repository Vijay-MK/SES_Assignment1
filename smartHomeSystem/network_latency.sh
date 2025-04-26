#!/bin/bash

IFACE="eth0"
VALUE=$1
MODE=$2
LOGFILE="./logs/simulatorLatency.log"

# Clear existing rules
tc qdisc del dev $IFACE root 2>/dev/null

if [ "$MODE" == "loss" ]; then
    echo "[`date`] Applying packet loss of ${VALUE}% on $IFACE" >> "$LOGFILE"
    tc qdisc add dev $IFACE root netem loss "${VALUE}%"
elif [ "$MODE" == "delay" ]; then
    echo "[`date`] Applying delay of ${VALUE}ms on $IFACE" >> "$LOGFILE"
    tc qdisc add dev $IFACE root netem delay "${VALUE}ms"
elif [ "$MODE" == "reset" ]; then
    echo "[`date`] Removing all network conditions on $IFACE" >> "$LOGFILE"
else
    echo "[`date`] Invalid mode: $MODE. Please use 'delay', 'loss', or 'reset'." >> "$LOGFILE"
fi
