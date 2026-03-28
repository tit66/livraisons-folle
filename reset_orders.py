import sys
import os

# Set working directory to load app correctly
os.chdir('/home/thierry/workspace/livraisons-app')
sys.path.append('.')

from app import run_query

# Remettre toutes les commandes "planned" en "pending" et vider les chauffeurs/camions
query = """
UPDATE orders 
SET status = 'pending', driver_id = NULL, vehicle_id = NULL, trailer_id = NULL 
WHERE status IN ('planned', 'assigned')
"""
run_query(query)
print("Toutes les commandes assignées ont été remises en attente.")
