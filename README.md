
# Prompt Manager (YAML Templates)

A lightweight utility for loading and rendering text prompts stored as **individual YAML files**.
Useful for LLM workflows, automation scripts, or any project that needs externalized text templates.

---

## 📁 How It Works

* Store each prompt in its own `.yml`/`.yaml` file:

```
prompts/
  welcome.yml
  email_verification.yml
  simple.yml
```

* The file **name** (without extension) becomes the prompt ID.
* YAML files may contain:

  * A **plain string**, or
  * A mapping with `"template"` and optional metadata.

Examples:

**Plain:**

```yaml
Hello {name}, welcome!
```

**Structured:**

```yaml
template: "Hello {name}, welcome to {app}!"
description: "Greeting message"
```

---

## 🚀 Basic Usage

```python
from prompt_manager_yml import PromptManager

pm = PromptManager("prompts", strict=True)
```

### List available prompts

```python
pm.list_prompts()
```

### Render a prompt

```python
pm.render("welcome", name="Mario", app="Skill Navigator")
```

### Handle missing params

* `strict=True` → error
* `strict=False` → leaves `{placeholder}` untouched

---

## ✔️ Features

* Simple folder-based prompt management
* YAML or raw string templates
* Parameter substitution using `.format()`
* Optional strict mode
* File caching for performance
* Clear error handling:

  * `PromptNotFoundError`
  * `PromptRenderError`

---

## 📦 Install Dependencies

```bash
pip install pyyaml
```

---

## 💡 When to Use

* LLM system/user prompts
* Automated message generation
* Email & notification templates
* Configurable text pipelines

