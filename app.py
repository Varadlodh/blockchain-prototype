import streamlit as st
import time
import json
import os
from blockchain import Blockchain, Block

# --- Setup Page Styling ---
st.set_page_config(page_title="Blockchain Verification System", page_icon="🔐", layout="wide")

# --- Local File Persistence Functions ---
DATA_FILE = "chain_data.json"

def load_stored_chain():
    """Loads the blockchain from a local JSON file or builds a new one if missing."""
    bc = Blockchain()
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                saved_blocks = json.load(f)
                
            # Reconstruct our blockchain instance from the raw JSON file data
            bc.chain = []
            for b_data in saved_blocks:
                reconstructed_block = Block(
                    index=b_data["index"],
                    timestamp=b_data["timestamp"],
                    data=b_data["data"],
                    previous_hash=b_data["previous_hash"],
                    nonce=b_data["nonce"]
                )
                reconstructed_block.hash = b_data["hash"]
                bc.chain.append(reconstructed_block)
        except Exception:
            bc = Blockchain()
            save_chain_to_disk(bc)
    else:
        # Generate initial sample data for demonstration if file doesn't exist yet
        bc.add_block({"student_name": "Amit Patel", "course": "B.E. Computer Science", "issuer": "Mumbai University", "cert_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"})
        bc.add_block({"student_name": "Neha Sharma", "course": "B.Tech Cyber Security", "issuer": "IIT Bombay", "cert_hash": "9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a10f9e8d7c6b5a4f3e2d1c0b9a8f7"})
        save_chain_to_disk(bc)
    return bc

def save_chain_to_disk(bc):
    """Saves the active session chain down onto the disk."""
    serializable_chain = []
    for b in bc.chain:
        serializable_chain.append({
            "index": b.index,
            "timestamp": b.timestamp,
            "data": b.data,
            "previous_hash": b.previous_hash,
            "nonce": b.nonce,
            "hash": b.hash
        })
    with open(DATA_FILE, "w") as f:
        json.dump(serializable_chain, f, indent=4)

# --- State Management Initialization ---
if "blockchain" not in st.session_state:
    st.session_state.blockchain = load_stored_chain()

bc = st.session_state.blockchain

# --- Title Header ---
st.title("🔐 Academic Credential Verification System")
st.markdown("A lightweight standalone functional simulation showing cryptographic immutability and data tampering detection.")
st.divider()

# --- Layout Navigation Setup ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📥 Issue New Certificate", 
    "📋 View Blockchain Ledger", 
    "🔍 Integrity Validation Check", 
    "⚠️ Tamper Demonstration Lab"
])

# --- TAB 1: ENTRY INTERFACE ---
with tab1:
    st.header("Issue Secure Credential Block")
    with st.form("issuance_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            stu_name = st.text_input("Student Full Name", placeholder="e.g. Rajesh Kumar")
            course_title = st.text_input("Course / Degree", placeholder="e.g. B.E. Information Technology")
        with col2:
            issuer_org = st.text_input("Issuing Institution", placeholder="e.g. University of Mumbai")
            doc_hash = st.text_input("Certificate Document SHA-256 Hash", placeholder="Paste files raw signature hash")
            
        submit_btn = st.form_submit_button("Sign & Deploy to Ledger")
        
        if submit_btn:
            if stu_name and course_title and issuer_org and doc_hash:
                payload = {
                    "student_name": stu_name,
                    "course": course_title,
                    "issuer": issuer_org,
                    "cert_hash": doc_hash
                }
                with st.spinner("Executing Proof-of-Work Mining Consensus..."):
                    bc.add_block(payload)
                    save_chain_to_disk(bc)
                st.success(f"Success! Block #{bc.get_latest_block().index} has been securely mined and added to the ledger.")
            else:
                st.error("All form inputs are required to construct a valid block.")

# --- TAB 2: EXPLORER LEDGER VIEW ---
with tab2:
    st.header("Distributed Ledger Records")
    for block in bc.chain:
        with st.expander(f"📦 Block #{block.index} — Hash: {block.hash[:20]}..."):
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Nonce (Mining Loop)", block.nonce)
                st.caption(f"Timestamp: {time.ctime(block.timestamp)}")
            with c2:
                st.text_area("Block Content Payload", value=json.dumps(block.data, indent=4), height=110, disabled=True, key=f"payload_{block.index}")
                st.code(f"Previous Block Link Hash: {block.previous_hash}\nCurrent Block Check Hash : {block.hash}", language="markdown")

# --- TAB 3: INTEGRITY VALIDATION ---
with tab3:
    st.header("Cryptographic Audit Terminal")
    st.markdown("Recomputes all block content signatures sequentially to confirm history remains pristine.")
    
    if st.button("Execute System Audit Check", type="primary"):
        is_valid, error_msg, broken_idx = bc.is_chain_valid()
        
        if is_valid:
            st.success("✅ Verification Pass: Ledger hashes match perfectly. System is untampered.")
        else:
            st.error(f"🚨 System Integrity Compromised! {error_msg}")
            st.warning(f"Break detected starting at Block #{broken_idx}. Cryptographic chain is invalid.")

# --- TAB 4: TAMPER DEMO EXPERIMENT ---
with tab4:
    st.header("The Vulnerability Playground")
    st.markdown("Simulate an unauthorized database modification. Alter records directly to see how blockchain prevents data forgery.")
    
    if len(bc.chain) <= 1:
        st.warning("Please add at least one custom record block via the first tab before experimenting.")
    else:
        target_idx = st.selectbox("Select Block Target to Alter Data:", range(1, len(bc.chain)))
        malicious_input = st.text_input("Malicious Modification Data Injection:", value="Attacker Altered Name")
        
        if st.button("Inject Tampered Data", type="secondary"):
            bc.chain[target_idx].data["student_name"] = malicious_input
            save_chain_to_disk(bc)
            st.warning(f"Data inside Block #{target_idx} has been covertly changed on system storage.")
            st.info("Now, move over to the 'Integrity Validation Check' tab and run the validation routine to watch the system catch this modification!")

        if st.button("Reset Chain to Original State", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.session_state.blockchain = load_stored_chain()
            st.rerun()
