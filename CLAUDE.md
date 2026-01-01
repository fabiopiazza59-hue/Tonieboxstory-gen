# Claude Code Project Guidelines

## HuggingFace Spaces + Gradio - Critical Lessons

### Error 1: Gradio Schema Serialization Bug
**Error:** `TypeError: argument of type 'bool' is not iterable` at `if "const" in schema:`

**Cause:** Gradio 4.44.0 has a bug when serializing complex nested dictionaries for API schema generation.

**WRONG - Don't do this:**
```python
# Iterating over complex dicts at component creation causes schema errors
language = gr.Dropdown(
    choices=[(v["label"], k) for k, v in LANGUAGES.items()],  # BAD
    ...
)
```

**CORRECT - Do this instead:**
```python
# Pre-compute simple lists BEFORE gr.Blocks()
LANGUAGE_CHOICES = [
    ("English", "en"),
    ("Español (Spanish)", "es"),
    ...
]

# Then use the simple list
language = gr.Dropdown(
    choices=LANGUAGE_CHOICES,  # GOOD
    ...
)
```

### Error 2: Gradio Version Mismatch
**Error:** HuggingFace ignores `requirements.txt` and uses default Gradio version.

**Fix:** Add SDK version to Space's `README.md` header:
```yaml
---
sdk: gradio
sdk_version: 4.19.2
---
```

**Also pin in requirements.txt:**
```
gradio==4.19.2
gradio_client==0.10.1
huggingface_hub==0.21.4
```

### Error 3: app.launch() Parameters
**Error:** `ValueError: When localhost is not accessible, a shareable link must be created`

**WRONG for HuggingFace:**
```python
app.launch(server_name="0.0.0.0", server_port=7865)  # BAD - breaks HF
```

**CORRECT for HuggingFace:**
```python
app.launch()  # GOOD - let HF handle it
```

### Error 4: gr.update() Dynamic Updates
**Error:** Dynamic dropdown updates with `gr.update()` can cause schema errors on newer Gradio versions.

**Risky pattern:**
```python
def update_voices(language):
    return gr.update(choices=new_choices, value=default)  # May break
```

**Safer pattern:** Use static dropdowns with all options, or test thoroughly on target Gradio version.

---

## General Rules for HuggingFace Spaces

1. **Always pin Gradio version** in both `requirements.txt` AND README.md header
2. **Use simple lists for dropdown choices** - never iterate over complex dicts at component creation
3. **Keep `app.launch()` simple** - no custom server_name/port for HF Spaces
4. **Test with the EXACT Gradio version** that HF will use
5. **Factory reboot the Space** after changing requirements.txt to force reinstall

---

## Working Configuration (as of 2024)

**requirements.txt:**
```
gradio==4.19.2
gradio_client==0.10.1
huggingface_hub==0.21.4
groq>=0.4.0
edge-tts>=6.1.0
pydub>=0.25.1
```

**app.py launch:**
```python
if __name__ == "__main__":
    app.launch()
```

**Dropdown choices:** Always pre-computed as simple `list[tuple[str, str]]`
