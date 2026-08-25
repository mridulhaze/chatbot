import sqlite3
import logging
from pathlib import Path
from backend.config import settings

logger = logging.getLogger("NU_TOKEN_DB")

TOKEN_DB_PATH = settings.DATA_DIR / "nu_tokens.db"

def get_token_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection to the separate Token database."""
    TOKEN_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(TOKEN_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_token_database():
    """Initializes schema and seeds default service types and solver teams."""
    conn = get_token_db_connection()
    try:
        with conn:
            conn.executescript("""
            -- 1. Service Types Table
            CREATE TABLE IF NOT EXISTS token_service_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_code TEXT UNIQUE NOT NULL,
                service_name TEXT NOT NULL,
                service_name_bn TEXT NOT NULL,
                description TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                sort_order INTEGER NOT NULL DEFAULT 0
            );

            -- 2. Solvers / Support Teams Table
            CREATE TABLE IF NOT EXISTS token_solvers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solver_name TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                active INTEGER NOT NULL DEFAULT 1
            );

            -- 3. Token Requests Table
            CREATE TABLE IF NOT EXISTS token_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id TEXT UNIQUE NOT NULL,
                problem TEXT NOT NULL,
                service_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                solver_id INTEGER,
                solver_name TEXT,
                solve_message TEXT,
                created_date TEXT NOT NULL,
                updated_date TEXT NOT NULL,
                solved_date TEXT,
                estimated_solve_date TEXT,
                user_id TEXT,
                user_name TEXT,
                user_email TEXT,
                user_phone TEXT,
                registration_no TEXT,
                college_code TEXT,
                priority TEXT NOT NULL DEFAULT 'NORMAL',
                admin_note TEXT,
                attachment_path TEXT,
                FOREIGN KEY (solver_id) REFERENCES token_solvers(id)
            );

            -- 4. Token Status History
            CREATE TABLE IF NOT EXISTS token_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_id TEXT NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                changed_by TEXT NOT NULL DEFAULT 'SYSTEM',
                message TEXT,
                created_date TEXT NOT NULL,
                FOREIGN KEY (token_id) REFERENCES token_requests(token_id) ON DELETE CASCADE
            );

            -- 5. Atomic Sequence Counter Table
            CREATE TABLE IF NOT EXISTS token_sequences (
                year INTEGER PRIMARY KEY,
                last_seq INTEGER NOT NULL DEFAULT 0
            );

            -- 6. User Service Credentials Table (Separate from tokens)
            CREATE TABLE IF NOT EXISTS user_service_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                service_code TEXT NOT NULL,
                username TEXT NOT NULL,
                encrypted_password TEXT NOT NULL,
                additional_data_encrypted TEXT,
                credential_label TEXT,
                service_url TEXT,
                credential_status TEXT NOT NULL DEFAULT 'ACTIVE',
                failed_login_count INTEGER NOT NULL DEFAULT 0,
                last_verified_at TEXT,
                last_used_at TEXT,
                notes TEXT,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, service_code)
            );

            -- 7. Service Credential Dynamic Fields
            CREATE TABLE IF NOT EXISTS service_credential_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_code TEXT NOT NULL,
                field_name TEXT NOT NULL,
                field_label TEXT NOT NULL,
                field_type TEXT NOT NULL DEFAULT 'TEXT',
                required INTEGER NOT NULL DEFAULT 1,
                encrypted INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0,
                UNIQUE(service_code, field_name)
            );

            -- Indexes for fast search
            CREATE INDEX IF NOT EXISTS idx_tokens_token_id ON token_requests(token_id);
            CREATE INDEX IF NOT EXISTS idx_tokens_status ON token_requests(status);
            CREATE INDEX IF NOT EXISTS idx_tokens_service ON token_requests(service_type);
            CREATE INDEX IF NOT EXISTS idx_token_history_id ON token_history(token_id);
            CREATE INDEX IF NOT EXISTS idx_user_cred_lookup ON user_service_credentials(user_id, service_code);
            """)

            # Seed Default Service Types
            default_services = [
                ("FORM_FILLUP", "Form Fill-up", "ফরম পূরণ", "Examination form fill-up, payment, and submission issues", 1, 1),
                ("TC", "TC / Transfer Certificate", "টিসি / ছাড়পত্র", "College transfer certificate application and approval", 1, 2),
                ("RESCRUTINY", "Rescrutiny / Re-check", "খাতা পুনঃনিরীক্ষণ", "Board examination answer sheet re-scrutiny applications", 1, 3),
                ("EMS", "EMS (Exam Management System)", "ইএমএস পোর্টাল", "EMS portal login, account credentials, and college access", 1, 4),
                ("CERTIFICATE", "Original / Provisional Certificate", "মূল ও সাময়িক সনদপত্র", "Certificate application, processing delay, and correction", 1, 5),
                ("MARKSHEET", "Marksheet / Transcript", "নম্বরপত্র / একাডেমিক ট্রান্সক্রিপ্ট", "Marksheet verification, correction, and duplicate copy", 1, 6),
                ("REGISTRATION", "Registration Card", "রেজিস্ট্রেশন কার্ড", "Student registration card correction, dual admission issues", 1, 7),
                ("ADMISSION", "Admission Portal", "ভর্তি সংক্রান্ত", "App1 admission release slip, quota, and merit list issues", 1, 8),
                ("RESULT", "Result Correction / Withheld", "ফলাফল ও স্থগিত রেজাল্ট", "Withheld results, CGPA recalculation, and promotion rules", 1, 9),
                ("OTHER", "Other General Inquiry", "অন্যান্য সাধারণ সমস্যা", "General academic or administrative assistance", 1, 10),
            ]
            conn.executemany("""
                INSERT OR IGNORE INTO token_service_types (service_code, service_name, service_name_bn, description, active, sort_order)
                VALUES (?, ?, ?, ?, ?, ?)
            """, default_services)

            # Seed Dynamic Service Credential Fields
            default_fields = [
                # EMS: User ID + Password
                ("EMS", "username", "EMS User ID / Roll", "TEXT", 1, 0, 1),
                ("EMS", "password", "EMS Password", "PASSWORD", 1, 1, 2),
                # Form Fillup: Registration Number + Session/Password
                ("FORM_FILLUP", "username", "Registration Number (রেজিস্ট্রেশন নম্বর)", "TEXT", 1, 0, 1),
                ("FORM_FILLUP", "password", "Password / Session Key", "PASSWORD", 1, 1, 2),
                # Certificate: Application / Serial ID + PIN
                ("CERTIFICATE", "username", "Certificate Application ID", "TEXT", 1, 0, 1),
                ("CERTIFICATE", "password", "Security PIN", "PASSWORD", 1, 1, 2),
                # Marksheet: Reg No + DOB / PIN
                ("MARKSHEET", "username", "Registration Number", "TEXT", 1, 0, 1),
                ("MARKSHEET", "password", "Student Password / PIN", "PASSWORD", 1, 1, 2),
                # Rescrutiny: Roll + Application Track ID
                ("RESCRUTINY", "username", "Exam Roll / Reg No", "TEXT", 1, 0, 1),
                ("RESCRUTINY", "password", "Tracking Passcode", "PASSWORD", 1, 1, 2),
                # Admission: Admission Roll + PIN
                ("ADMISSION", "username", "Admission Roll (ভর্তি রোল)", "TEXT", 1, 0, 1),
                ("ADMISSION", "password", "Admission PIN", "PASSWORD", 1, 1, 2),
                # Registration: Student ID + Key
                ("REGISTRATION", "username", "Student / College ID", "TEXT", 1, 0, 1),
                ("REGISTRATION", "password", "Access Key", "PASSWORD", 1, 1, 2)
            ]
            conn.executemany("""
                INSERT OR IGNORE INTO service_credential_fields (service_code, field_name, field_label, field_type, required, encrypted, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, default_fields)

            # Seed Default Solvers
            default_solvers = [
                ("ICT Support Team", "ICT Department (Academic Building 12th/13th Floor)", "ict-support@nu.ac.bd", "+88029291011", 1),
                ("Controller of Examination Section", "Examination Department", "exam-controller@nu.ac.bd", "+88029291012", 1),
                ("Certificate & Academic Records Cell", "Registrar Office", "certificate@nu.ac.bd", "+88029291013", 1),
                ("Admission & Registration Cell", "Admission Office", "admission@nu.ac.bd", "+88029291014", 1),
                ("Accounts & Sonali Seba Desk", "Finance & Accounts", "finance@nu.ac.bd", "+88029291015", 1)
            ]
            conn.executemany("""
                INSERT OR IGNORE INTO token_solvers (solver_name, department, email, phone, active)
                VALUES (?, ?, ?, ?, ?)
            """, default_solvers)

            # Check and migrate columns if needed
            cols = [r["name"] for r in conn.execute("PRAGMA table_info(token_requests)").fetchall()]
            if "estimated_solve_date" not in cols:
                conn.execute("ALTER TABLE token_requests ADD COLUMN estimated_solve_date TEXT")
            if "credential_id" not in cols:
                conn.execute("ALTER TABLE token_requests ADD COLUMN credential_id INTEGER")

        logger.info("Token and Credential databases initialized and verified successfully.")
    except Exception as e:
        logger.error(f"Error initializing token database: {e}", exc_info=True)
        raise
    finally:
        conn.close()
