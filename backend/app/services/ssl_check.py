"""
SSL/TLS inspection using Python's stdlib ssl module directly against the
socket (no external tool needed for cert expiry, issuer, protocol, ciphers).
"""
import ssl
import socket
from datetime import datetime, timezone

WEAK_PROTOCOLS = {"SSLv2", "SSLv3", "TLSv1", "TLSv1.1"}


async def inspect_ssl(hostname: str, port: int = 443) -> dict:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # inspecting, not validating

    result = {"hostname": hostname, "port": port, "reachable": False}

    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                protocol = ssock.version()

                not_after = cert.get("notAfter")
                expires_at = None
                days_remaining = None
                if not_after:
                    expires_at = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                    days_remaining = (expires_at - datetime.now(timezone.utc)).days

                issuer = dict(x[0] for x in cert.get("issuer", []))

                result.update({
                    "reachable": True,
                    "protocol": protocol,
                    "cipher_suite": cipher[0] if cipher else None,
                    "issuer": issuer.get("organizationName") or issuer.get("commonName"),
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "days_remaining": days_remaining,
                    "is_expired": days_remaining is not None and days_remaining < 0,
                    "is_expiring_soon": days_remaining is not None and 0 <= days_remaining <= 30,
                    "weak_protocol": protocol in WEAK_PROTOCOLS,
                })
    except (socket.timeout, ConnectionRefusedError, ssl.SSLError, OSError) as e:
        result["error"] = str(e)

    return result
