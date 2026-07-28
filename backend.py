"""
COSMODEX // Core Backend & Local Ledger Engine
Integra la fisica aperiodica, la persistenza su SQLite e la logica di Smart Contract.
"""

import sqlite3
import hashlib
import json
import time
from typing import Dict, List, Any

# --- STEP 2 & 3: LEDGER & BLOCK MANAGEMENT ---
class AperiodicLedger:
    def __init__(self, db_name: str = "cosmodex_galaxy_map.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocks (
                block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                phason_coordinates TEXT,
                coherence REAL,
                l2_error REAL,
                prev_hash TEXT,
                block_hash TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def create_block(self, phason_coords: List[float], coherence: float, l2_error: float) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Recupera l'hash del blocco precedente per la concatenazione crittografica
        cursor.execute("SELECT block_hash FROM blocks ORDER BY block_id DESC LIMIT 1")
        row = cursor.fetchone()
        prev_hash = row[0] if row else "0" * 64
        
        timestamp = time.time()
        coords_str = json.dumps(phason_coords)
        
        # Calcolo del Bragg Spectrum S(k) (Hash crittografico del blocco)
        raw_data = f"{timestamp}{coords_str}{coherence}{l2_error}{prev_hash}"
        block_hash = hashlib.sha256(raw_data.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO blocks (timestamp, phason_coordinates, coherence, l2_error, prev_hash, block_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, coords_str, coherence, l2_error, prev_hash, block_hash))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "SEALED",
            "block_hash": block_hash,
            "prev_hash": prev_hash,
            "coherence": coherence,
            "l2_error": l2_error
        }

# --- STEP 4: SMART CONTRACT & MISSION EVALUATION ---
class MissionSmartContract:
    @staticmethod
    def evaluate_mission(coherence: float, l2_error: float) -> str:
        """
        Esegue le regole deterministiche on-chain:
        Se coerenza >= 98.0 e L2_error < 0.02 -> COMPLETE
        Altrimenti -> IN_PROGRESS
        """
        if coherence >= 98.0 and l2_error < 0.02:
            return "COMPLETE (REWARD UNLOCKED)"
        return "IN_PROGRESS (COHERENCE BUILDING)"

if __name__ == "__main__":
    ledger = AperiodicLedger()
    
    # Simulazione di un settore scansionato con coordinate fasoniche basate sulla sezione aurea
    sample_coords = [1.618033, 0.618033, 0.000000]
    result = ledger.create_block(sample_coords, coherence=98.5, l2_error=0.015)
    
    # Valutazione dello Smart Contract
    mission_status = MissionSmartContract.evaluate_mission(result["coherence"], result["l2_error"])
    
    print("--- COSMODEX BLOCKCHAIN LEDGER TEST ---")
    print(json.dumps(result, indent=2))
    print(f"Mission Status: {mission_status}")
