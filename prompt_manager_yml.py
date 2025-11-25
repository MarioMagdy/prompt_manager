"""
prompt_manager_yml.py

A utility module for managing dynamic prompt templates stored as individual YAML
files inside a folder. This class provides a clean interface for loading,
caching, and rendering prompt templates with parameter substitution.

The module is designed for use in applications that rely on LLM prompts,
automation flows, or any system where text templates need to be maintained in a
structured, external, and version-controllable format.

--------------------------------------------------------------------------------
Key Features
--------------------------------------------------------------------------------
1. Folder-based Prompt Storage
   - Each prompt lives in its own .yml/.yaml file inside a specified directory.
   - File names (without extension) act as prompt identifiers.
     Example:
         prompts/
             welcome.yml
             email_verification.yaml
             simple_prompt.yml

2. Flexible YAML Structure
   Prompt files support two formats:
     A) Plain string:
         ---
         Hello {name}, welcome to our platform!
     B) YAML mapping with metadata:
         ---
         template: "Hello {name}, welcome to {app_name}!"
         description: "Greeting message used after signup"

3. Parameter Substitution
   - Render prompts using `template.format(**params)`.
   - Supports strict mode:
       * strict=True  → missing parameters raise PromptRenderError
       * strict=False → missing placeholders remain as {placeholder}

4. Caching
   - Loaded templates are cached in memory to avoid repeated disk reads.
   - Cache can be invalidated using `clear_cache()`.

5. Error Handling
   - PromptNotFoundError: file does not exist
   - PromptRenderError: missing parameters or formatting issues
   - Helpful validation for malformed prompt files

--------------------------------------------------------------------------------
Usage Example
--------------------------------------------------------------------------------

    pm = PromptManager("prompts")

    pm.render("welcome", name="Mario", app_name="Skill Navigator")

This will load prompts/welcome.yml, substitute the parameters, and return
the rendered string.

--------------------------------------------------------------------------------
Intended Use Cases
--------------------------------------------------------------------------------
- LLM agents and multi-step pipelines
- Re-usable system/user prompts in AI workflows
- Email templates, system messages, or chatbot intents
- Any project needing structured external text templates

"""



from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class PromptNotFoundError(FileNotFoundError):
    """Raised when a prompt file is not found."""


class PromptRenderError(ValueError):
    """Raised when there is an error rendering a prompt (e.g., missing params)."""


class PromptManager:
    """
    Manages loading prompt templates from a folder of YAML files and rendering them.

    Folder structure example:

        prompts/
          welcome.yml
          email_verification.yaml
          simple_prompt.yml

    Each file can be:

    1) A plain string:
        ---
        This one has no parameters.

    2) A mapping with 'template':
        ---
        template: "Hello {name}, welcome to {app_name}!"
        description: "Basic welcome message"
    """

    def __init__(self, folder: str | Path, strict: bool = True) -> None:
        """
        :param folder: Path to the folder containing prompt YAML files.
        :param strict: If True, missing parameters raise errors.
                       If False, missing params are left as {placeholder}.
        """
        self._folder = Path(folder)
        self._strict = strict

        if not self._folder.exists() or not self._folder.is_dir():
            raise NotADirectoryError(f"Prompt folder not found or not a directory: {self._folder}")

        # Cache: name -> template string
        self._cache: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def list_prompts(self) -> List[str]:
        """
        List available prompt names (based on .yml /.yaml files in the folder).
        """
        names = set()
        for path in self._folder.iterdir():
            if path.is_file() and path.suffix in {".yml", ".yaml"}:
                names.add(path.stem)
        return sorted(names)

    def has_prompt(self, name: str) -> bool:
        """
        Check if a prompt with this name has a corresponding file.
        """
        return self._resolve_path(name) is not None

    def get_template(self, name: str, use_cache: bool = True) -> str:
        """
        Get the raw template string for a given prompt name (without formatting).
        Loads from disk (and caches) if needed.
        """
        if use_cache and name in self._cache:
            return self._cache[name]

        path = self._resolve_path(name)
        if path is None:
            raise PromptNotFoundError(f"Prompt '{name}' not found in folder {self._folder}")

        template = self._load_template_from_file(path)
        self._cache[name] = template
        return template

    def render(self, prompt_name: str, **params: Any) -> str:
        """
        Render a prompt by name with given parameters.

        :param name: Prompt file name (without extension).
        :param params: Parameters to fill in `{placeholders}`.
        :return: Rendered string.
        """
        template = self.get_template(prompt_name)

        if self._strict:
            # Strict mode: missing params raise KeyError -> PromptRenderError
            try:
                return template.format(**params)
            except KeyError as e:
                missing = e.args[0]
                raise PromptRenderError(
                    f"Missing parameter '{missing}' for prompt '{prompt_name}'"
                ) from e
            except Exception as e:
                raise PromptRenderError(
                    f"Error rendering prompt '{prompt_name}': {e}"
                ) from e
        else:
            # Non-strict: leave missing placeholders as-is
            class DefaultDict(dict):
                def __missing__(self, key: str) -> str:
                    return "{%s}" % key

            return template.format_map(DefaultDict(**params))

    def clear_cache(self) -> None:
        """Clear the in-memory template cache (forces reload from disk next time)."""
        self._cache.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_path(self, name: str) -> Optional[Path]:
        """
        Resolve a prompt name to a concrete file path (.yml or .yaml).
        Returns None if no such file exists.
        """
        candidates = [
            self._folder / f"{name}.yml",
            self._folder / f"{name}.yaml",
        ]
        for c in candidates:
            if c.exists() and c.is_file():
                return c
        return None

    @staticmethod
    def _load_template_from_file(path: Path) -> str:
        """
        Load the template string from a YAML file.
        Supports either:
          - raw string
          - mapping with 'template' key
        """
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Case 1: file is just a string
        if isinstance(data, str):
            return data

        # Case 2: file is a mapping with 'template'
        if isinstance(data, dict):
            if "template" not in data:
                raise ValueError(
                    f"File '{path}' must contain either a plain string or a 'template' key."
                )
            template = data["template"]
            if not isinstance(template, str):
                raise ValueError(
                    f"'template' in file '{path}' must be a string."
                )
            return template

        raise ValueError(
            f"Unsupported YAML content type in '{path}': {type(data).__name__}"
        )
