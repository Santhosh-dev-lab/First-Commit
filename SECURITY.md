# PHYSICA Security Architecture & Threat Model

This document outlines the threat model and security mitigations implemented across the PHYSICA platform.

## 1. Threat Model & Overview
PHYSICA bridges physical infrastructure (sensors, pumps, valves) with automated execution (agents) and a digital twin. Due to the physical nature of these systems, security vulnerabilities could lead to equipment damage or crop loss. 
The threat model assumes:
- The internal network (local SQLite) is trusted, but the frontend and edge payloads (MQTT/IoT) are untrusted.
- Users can be malicious and may attempt to access cross-farm resources (IDOR) or inject malicious telemetry.
- Agents are untrusted. Prompt injection could occur via telemetry data.

## 2. Mitigations

### 2.1 Authentication & Session Security
- **Passwords**: Hashed using Argon2id. Enforced strict complexity (12-128 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special).
- **Email Validation**: Strictly validated using `email_validator` to prevent CRLF injection and malformed inputs.
- **Sessions**: Stored in SQLite with a 30-day expiration. The session cookie is protected with `HttpOnly`, `Secure` (in prod), and `SameSite=Lax`.

### 2.2 Authorization & Farm Isolation
- **Role-Based Access Control (RBAC)**: Supports `OWNER`, `OPERATOR`, and `VIEWER` roles. 
- **IDOR Protection**: Every authenticated API request validates the user's role against the targeted `farm_id`. Cross-farm access returns an opaque `404 Not Found` or `403 Forbidden` to prevent enumeration.

### 2.3 Input Validation & Injection Prevention
- **Pydantic**: All request bodies enforce explicit bounded schemas (`min`/`max`).
- **SQL Injection**: Exclusively mitigated by using parameterized SQLite queries (`?` binding).
- **XSS**: Handled defensively in the Next.js frontend by using safe React rendering.
- **Path Traversal**: No arbitrary user-defined paths are used.

### 2.4 Rate Limiting & DoS Protection
- **Rate Limiting**: `slowapi` enforces strict limits on authentication (login/register) and sensible limits on standard endpoints.
- **Payload Limits**: Large JSON bodies are rejected. Maximum simulation iterations/duration are bounded.

### 2.5 Security Headers & CORS
- **CORS**: Avoids wildcard origins. Only explicitly allowed origins via `PHYSICA_ALLOWED_ORIGINS` are accepted.
- **Headers**: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, and `Referrer-Policy` are enforced via middleware.

### 2.6 Edge & Command Security
- **Command Allowlist**: Only predefined capabilities (`PUMP_ON`, `VALVE_OPEN`, etc.) are permitted.
- **Telemetry Replay Protection**: Verified using `timestamp` and `sequence_number`. Telemetry older than 24 hours is rejected.
- **Farm Isolation (Edge)**: Telemetry is explicitly validated against authorized gateway/device identities belonging to the Farm.

### 2.7 Agent & LLM Security
- **Tool Restrictions**: Agents do not possess direct `EXECUTION` authority. They generate `PROPOSAL` plans.
- **Safety Engine**: An authoritative Safety Engine sits before the physical execution boundary. It cannot be bypassed by Agents, Operators, or UI.

## 3. Incident Response
In the event of compromise:
1. Revoke all active sessions via the database.
2. Cycle Edge Gateway credentials (AWS IoT certificates).
3. Halt execution to prevent automated physical damage.

## 4. Responsible Disclosure
If you find a security vulnerability, please do not disclose it publicly. Email the maintainers directly.
