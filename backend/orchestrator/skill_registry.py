import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from backend.core.config import settings

logger = logging.getLogger("NU_SKILL_REGISTRY")

class SkillDefinition:
    def __init__(self, name: str, description: str, markdown_content: str):
        self.name = name
        self.description = description
        self.markdown_content = markdown_content

class SkillRegistry:
    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = skills_dir or settings.SKILLS_DIR
        self._skills: Dict[str, SkillDefinition] = {}
        self.load_skills()

    def load_skills(self):
        """Scans skills/ directory and parses all SKILL.md specifications."""
        self._skills.clear()
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory {self.skills_dir} not found.")
            return

        for skill_folder in self.skills_dir.iterdir():
            if skill_folder.is_dir():
                skill_md_file = skill_folder / "SKILL.md"
                if skill_md_file.exists():
                    try:
                        content = skill_md_file.read_text(encoding="utf-8")
                        name = skill_folder.name
                        desc = f"{name} skill"
                        
                        # Extract description if present
                        if "description:" in content:
                            for line in content.splitlines():
                                if line.strip().startswith("description:"):
                                    desc = line.split(":", 1)[1].strip()
                                    break

                        self._skills[name] = SkillDefinition(
                            name=name,
                            description=desc,
                            markdown_content=content
                        )
                        logger.info(f"Loaded Skill: {name}")
                    except Exception as e:
                        logger.error(f"Error loading skill from {skill_md_file}: {e}")

    def get_skill(self, skill_name: str) -> Optional[SkillDefinition]:
        return self._skills.get(skill_name)

    def list_skills(self) -> Dict[str, str]:
        return {name: s.description for name, s in self._skills.items()}

_skill_registry_instance: Optional[SkillRegistry] = None

def get_skill_registry() -> SkillRegistry:
    global _skill_registry_instance
    if _skill_registry_instance is None:
        _skill_registry_instance = SkillRegistry()
    return _skill_registry_instance
