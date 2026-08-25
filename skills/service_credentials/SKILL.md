---
name: service_credentials
version: 1.0.0
description: Manages service-specific user credentials for NU portals (EMS, Form Fill-up, Certificate, Marksheet, etc.) with strict encryption and zero password exposure.
---

# Service-Specific User Credentials Skill

## Purpose
Allow students and users to manage their service-specific credentials for National University portals (EMS, Form Fill-up, Certificate, Marksheet, Rescrutiny, Admission, Registration).

## Trigger Conditions
Activate this skill whenever:
1. User asks to save, configure, update, test, or delete login credentials (e.g. "Save my EMS credentials", "Configure Form Fill-up login", "ক্রেডেনশিয়াল সংরক্ষণ").
2. User asks to test or verify whether their saved portal login is working.
3. User opens the "🔐 My Service Credentials" interface.
4. During Token Creation for a service where credentials are not yet configured, the system asks if the user wants to add credentials before creating the token.

## Available MCP Tools
- `get_user_services`: Lists services and credential configuration status.
- `get_credential_status`: Checks if a specific service has configured credentials.
- `save_service_credential`: Securely encrypts and stores credentials.
- `verify_service_credential`: Tests validity of stored credentials.
- `delete_service_credential`: Permanently removes saved credentials.

## Strict Security & Privacy Rules
- **NEVER** ask for, receive, or display plain-text passwords in conversational messages whenever possible.
- When credential configuration is requested, guide the user to the interactive secure credential modal (`openCredentialsModal()`).
- **NEVER** output plain-text passwords or secret keys in AI responses.
- The AI only receives and outputs configuration statuses (`ACTIVE`, `NOT_VERIFIED`, `INVALID`, `NOT_CONFIGURED`).
- Decryption is handled strictly in-memory by backend services when executing authorized verification.

## Conversational Workflow
1. User asks to manage credentials for a service (e.g. "Save my EMS login").
2. AI checks `get_credential_status(user_id, service_code="EMS")`.
3. If already configured, show current status and offer options: `[ Test Credentials ]`, `[ Update Credentials ]`, `[ Delete ]`.
4. If not configured, guide user to click the secure input form: `[ 🔐 Configure EMS Credentials ]`.
5. When user asks to test credentials, invoke `verify_service_credential(user_id, service_code)` and display the result (`🟢 Verified Active` or `🔴 Verification Failed`).
