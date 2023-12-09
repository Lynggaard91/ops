#!/bin/bash

#Reduce Epoch time by seconds, do so by changing '- 60'
$(date -d "@$(( $(date +%s) - 60 ))" +%s )