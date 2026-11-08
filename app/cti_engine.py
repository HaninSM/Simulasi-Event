import ipaddress
import hashlib
from datetime import datetime, timezone
from typing import Dict, Optional, List

from app.models import ThreatIntelData


class ThreatIntelEngine:
    """
    Cortex-Inspired Threat Intelligence & Observable Analyzer Engine.
    Provides fast, deterministic CTI enrichment for IP observables:
    - Categorization (Tor Exit Node, Bulletproof Hoster, Botnet, Scanner)
    - Abuse Confidence Score (0 - 100%)
    - Geolocation & Country Flags
    - ASN & ISP attribution
    - Threat Actor / Campaign Attribution
    """

    KNOWN_IOC_FEEDS: Dict[str, dict] = {
        # Skenario 2: DDoS / Botnet Flood
        "45.33.32.156": {
            "verdict": "MALICIOUS",
            "abuse_score": 96,
            "threat_actor": "Mirai-Variant Botnet",
            "category": "Known Botnet Cannon & Cloud Scanner",
            "asn": "AS63949 (Linode / Akamai LLC)",
            "country": "United States",
            "country_code": "US",
            "flag": "🇺🇸",
            "indicators": ["DDoS Cannon", "HTTP Flood Node", "Known Scanner"],
        },
        "194.26.29.112": {
            "verdict": "MALICIOUS",
            "abuse_score": 98,
            "threat_actor": "RedLine / Bulletproof Inf",
            "category": "Bulletproof Offshore Hosting",
            "asn": "AS44477 (Stark Industries Solutions / Seychelles)",
            "country": "Seychelles",
            "country_code": "SC",
            "flag": "🇸🇨",
            "indicators": ["Bulletproof Hosting", "Malware C2 Proxy", "Brute Force Source"],
        },
        "185.220.101.45": {
            "verdict": "MALICIOUS",
            "abuse_score": 100,
            "threat_actor": "Tor Anonymization Network",
            "category": "Tor Exit Relay",
            "asn": "AS9009 (M247 Ltd Europe)",
            "country": "Germany",
            "country_code": "DE",
            "flag": "🇩🇪",
            "indicators": ["Tor Exit Node", "Anonymizer", "Credential Abuse"],
        },
        # Skenario 3: Impossible Travel
        "103.111.201.22": {
            "verdict": "BENIGN",
            "abuse_score": 2,
            "threat_actor": None,
            "category": "Corporate Mobile / Fiber Gateway",
            "asn": "AS7713 (Telkom Indonesia)",
            "country": "Indonesia",
            "country_code": "ID",
            "flag": "🇮🇩",
            "indicators": ["Legitimate User Gateway"],
        },
        "194.26.29.50": {
            "verdict": "MALICIOUS",
            "abuse_score": 94,
            "threat_actor": "Tor Exit / Proxy Network",
            "category": "Tor Exit Relay & Anonymizer",
            "asn": "AS200019 (Alexhost SRL / Frankfurt)",
            "country": "Germany",
            "country_code": "DE",
            "flag": "🇩🇪",
            "indicators": ["Tor Exit Node", "Impossible Travel Proxy"],
        },
        "182.253.11.88": {
            "verdict": "BENIGN",
            "abuse_score": 1,
            "threat_actor": None,
            "category": "ISP Broadband Gateway",
            "asn": "AS7713 (Telkom Indonesia - Surabaya)",
            "country": "Indonesia",
            "country_code": "ID",
            "flag": "🇮🇩",
            "indicators": ["Domestic Residential"],
        },
        "198.51.100.22": {
            "verdict": "SUSPICIOUS",
            "abuse_score": 68,
            "threat_actor": "Commercial VPN Service",
            "category": "Commercial Anonymizing VPN",
            "asn": "AS396982 (Google Cloud - Dallas Tier-2)",
            "country": "United States",
            "country_code": "US",
            "flag": "🇺🇸",
            "indicators": ["VPN Gateway", "Geo-spoofing"],
        },
        "118.189.20.14": {
            "verdict": "BENIGN",
            "abuse_score": 0,
            "threat_actor": None,
            "category": "Regional Telecom Gateway",
            "asn": "AS4657 (StarHub Ltd)",
            "country": "Singapore",
            "country_code": "SG",
            "flag": "🇸🇬",
            "indicators": ["Corporate Gateway"],
        },
        "185.220.101.99": {
            "verdict": "MALICIOUS",
            "abuse_score": 97,
            "threat_actor": "Tor Exit Relay",
            "category": "Tor Exit Node",
            "asn": "AS9009 (M247 Ltd)",
            "country": "Russia",
            "country_code": "RU",
            "flag": "🇷🇺",
            "indicators": ["Tor Exit Node", "High-Risk Geovelocity"],
        },
        # Skenario 4: Distributed Brute Force
        "185.220.101.5": {
            "verdict": "MALICIOUS",
            "abuse_score": 99,
            "threat_actor": "Distributed Brute-Force Bot",
            "category": "Tor Exit Node",
            "asn": "AS9009 (M247 Ltd)",
            "country": "Netherlands",
            "country_code": "NL",
            "flag": "🇳🇱",
            "indicators": ["Tor Exit Node", "SSH Brute Forcer"],
        },
        "198.51.100.23": {
            "verdict": "MALICIOUS",
            "abuse_score": 85,
            "threat_actor": "Cloud VPS Sprayer",
            "category": "Hosting / Data Center Abuse",
            "asn": "AS14061 (DigitalOcean LLC)",
            "country": "United States",
            "country_code": "US",
            "flag": "🇺🇸",
            "indicators": ["Automated Sprayer", "SSH Dictionary Attack"],
        },
        "203.0.113.12": {
            "verdict": "SUSPICIOUS",
            "abuse_score": 74,
            "threat_actor": "Public Proxy Node",
            "category": "Open SOCKS5 / HTTP Proxy",
            "asn": "AS45102 (Alibaba Cloud)",
            "country": "Hong Kong",
            "country_code": "HK",
            "flag": "🇭🇰",
            "indicators": ["Open Proxy", "Brute Force Participant"],
        },
        "192.0.2.45": {
            "verdict": "SUSPICIOUS",
            "abuse_score": 72,
            "threat_actor": "Compromised IoT Gateway",
            "category": "Compromised CPE / Router",
            "asn": "AS2497 (IIJ Internet Initiative Japan)",
            "country": "Japan",
            "country_code": "JP",
            "flag": "🇯🇵",
            "indicators": ["Zombie IoT Node", "Sprayer"],
        },
        "45.33.32.88": {
            "verdict": "MALICIOUS",
            "abuse_score": 89,
            "threat_actor": "Automated Vulnerability Prober",
            "category": "Cloud VPS Sprayer",
            "asn": "AS63949 (Linode LLC)",
            "country": "United Kingdom",
            "country_code": "GB",
            "flag": "🇬🇧",
            "indicators": ["Known Scanner", "SSH Password Spray"],
        },
        # Skenario 6: Careless Whitelist
        "203.0.113.88": {
            "verdict": "MALICIOUS",
            "abuse_score": 93,
            "threat_actor": "Shadow Intruder",
            "category": "Disguised External Attacker",
            "asn": "AS4808 (China Unicom Beijing)",
            "country": "China",
            "country_code": "CN",
            "flag": "🇨🇳",
            "indicators": ["Careless Whitelist Exploiter", "Blind Spot Abuse"],
        },
        # Skenario 8: Low & Slow APT
        "198.51.100.77": {
            "verdict": "MALICIOUS",
            "abuse_score": 91,
            "threat_actor": "APT29 / Cozy Bear Affiliate",
            "category": "Nation-State C2 Staging",
            "asn": "AS396982 (Google Cloud Hosting)",
            "country": "United States",
            "country_code": "US",
            "flag": "🇺🇸",
            "indicators": ["Low & Slow Recon", "APT Watchlist Target", "Cold Archive IoC"],
        },
        "203.0.113.144": {
            "verdict": "MALICIOUS",
            "abuse_score": 88,
            "threat_actor": "Lazarus Sub-Cluster",
            "category": "Stealth Infiltration Infrastructure",
            "asn": "AS4134 (Chinanet Backbone)",
            "country": "China",
            "country_code": "CN",
            "flag": "🇨🇳",
            "indicators": ["Multi-stage APT", "Reconnaissance Probe"],
        },
        "192.0.2.199": {
            "verdict": "MALICIOUS",
            "abuse_score": 90,
            "threat_actor": "Volt Typhoon Proxy",
            "category": "Living-off-the-Land C2",
            "asn": "AS7922 (Comcast Cable)",
            "country": "United States",
            "country_code": "US",
            "flag": "🇺🇸",
            "indicators": ["SOHO Router Proxy", "APT Exploit Gateway"],
        },
        # Skenario 9: OT Industrial Sabotage
        "192.168.30.99": {
            "verdict": "MALICIOUS",
            "abuse_score": 82,
            "threat_actor": "Rogue Internal IoT / Physical Intruder",
            "category": "Compromised OT Network Node",
            "asn": "AS-PRIVATE (Internal OT VLAN 30)",
            "country": "Internal OT Datacenter",
            "country_code": "ID",
            "flag": "🏭",
            "indicators": ["Unauthorized MQTT Injection", "Thermal Sabotage Risk"],
        },
    }

    def __init__(self):
        self.lookup_counter: int = 0

    def lookup(self, ip_address: str) -> ThreatIntelData:
        """
        Looks up threat intelligence for an IP observable.
        Returns curated threat intelligence feeds or heuristic classification for unseen IPs.
        """
        self.lookup_counter += 1
        ip_clean = ip_address.strip()

        # 1. Check known IoC feed database
        if ip_clean in self.KNOWN_IOC_FEEDS:
            feed = self.KNOWN_IOC_FEEDS[ip_clean]
            return ThreatIntelData(
                ip_address=ip_clean,
                verdict=feed["verdict"],
                abuse_score=feed["abuse_score"],
                threat_actor=feed.get("threat_actor"),
                category=feed["category"],
                asn=feed["asn"],
                country=feed["country"],
                country_code=feed["country_code"],
                flag=feed["flag"],
                indicators=feed.get("indicators", []),
                last_seen=datetime.now(timezone.utc).isoformat(),
            )

        # 2. Check RFC1918 Private / Loopback IP address
        try:
            addr = ipaddress.ip_address(ip_clean)
            if addr.is_private or addr.is_loopback:
                return ThreatIntelData(
                    ip_address=ip_clean,
                    verdict="BENIGN",
                    abuse_score=0,
                    threat_actor=None,
                    category="Internal Enterprise Network (RFC1918)",
                    asn="AS-INTERNAL (Local Campus / VPC)",
                    country="Internal Network",
                    country_code="LOCAL",
                    flag="🏢",
                    indicators=["Trusted Intranet"],
                    last_seen=datetime.now(timezone.utc).isoformat(),
                )
        except Exception:
            pass

        # 3. Dynamic Heuristic for arbitrary external IP
        # Deterministically derives a realistic CTI profile based on IP hash
        h = int(hashlib.md5(ip_clean.encode()).hexdigest()[:6], 16)
        abuse_score = 40 + (h % 58)  # Score between 40 - 97
        verdict = "MALICIOUS" if abuse_score >= 80 else ("SUSPICIOUS" if abuse_score >= 50 else "BENIGN")
        
        sample_asns = [
            ("AS14061 (DigitalOcean LLC)", "United States", "US", "🇺🇸"),
            ("AS16509 (Amazon AWS Cloud)", "United States", "US", "🇺🇸"),
            ("AS9009 (M247 Ltd Europe)", "Germany", "DE", "🇩🇪"),
            ("AS24940 (Hetzner Online GmbH)", "Germany", "DE", "🇩🇪"),
            ("AS4808 (China Unicom)", "China", "CN", "🇨🇳"),
            ("AS20473 (Choopa / Vultr)", "Netherlands", "NL", "🇳🇱"),
        ]
        asn_pick = sample_asns[h % len(sample_asns)]

        return ThreatIntelData(
            ip_address=ip_clean,
            verdict=verdict,
            abuse_score=abuse_score,
            threat_actor="Unidentified Threat Actor" if verdict == "MALICIOUS" else None,
            category="External Autonomous System" if verdict != "MALICIOUS" else "Suspected Malicious Scanner",
            asn=asn_pick[0],
            country=asn_pick[1],
            country_code=asn_pick[2],
            flag=asn_pick[3],
            indicators=["Unrecognized External IP", f"Heuristic Score: {abuse_score}%"],
            last_seen=datetime.now(timezone.utc).isoformat(),
        )

    def enrich(self, ip_address: Optional[str]) -> Optional[ThreatIntelData]:
        """Enriches an IP observable if provided, otherwise returns None."""
        if not ip_address:
            return None
        return self.lookup(ip_address)
