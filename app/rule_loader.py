import os
import glob
import logging
from typing import Dict, Optional
import yaml

from app.models import DetectionRule

logger = logging.getLogger("mini_siem.rule_loader")


class RuleLoader:
    """
    Detection as Code Engine:
    Loads, validates, and manages YAML-based detection rules (Sigma-like syntax).
    Allows hot-reloading rules without restarting the SIEM server.
    """

    @classmethod
    def load_from_directory(cls, dir_path: Optional[str] = None) -> Dict[str, DetectionRule]:
        if dir_path is None:
            dir_path = os.path.join(os.path.dirname(__file__), "rules")

        if not os.path.exists(dir_path):
            logger.warning("Rules directory '%s' does not exist.", dir_path)
            return {}

        rules: Dict[str, DetectionRule] = {}
        pattern = os.path.join(dir_path, "*.y*ml")
        files = glob.glob(pattern)

        for file_path in sorted(files):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if not data or not isinstance(data, dict):
                        continue
                    rule = DetectionRule(**data)
                    rules[rule.id] = rule
            except Exception as e:
                logger.error("Failed to load detection rule from '%s': %s", file_path, e)

        logger.info("Loaded %d detection rules from '%s'.", len(rules), dir_path)
        return rules
