# Configuration Files

This directory contains easy-to-modify YAML configuration files for the application.

## Files

### 1. `themes.yaml`
**Purpose**: Define available themes for user selection

**How to modify**:
- Add/remove/edit theme entries
- Each theme needs:
  - `id`: Unique identifier (lowercase, underscores)
  - `name`: Display name for users
  - `description`: Brief description

**Example**:
```yaml
themes:
  - id: my_new_theme
    name: My New Theme
    description: Description of what this theme does
```

**After modification**: Restart the backend to pick up changes

---

### 2. `audiences.yaml`
**Purpose**: Define target audience types for response tailoring

**How to modify**:
- Add/remove/edit audience entries
- Each audience needs:
  - `id`: Unique identifier (lowercase, underscores)
  - `name`: Display name for users
  - `age_range`: Optional age range (e.g., "18-25")
  - `description`: Brief description

**Example**:
```yaml
audiences:
  - id: new_audience
    name: New Audience
    age_range: "30-50"
    description: Description of this audience
```

**After modification**: Restart the backend to pick up changes

---

### 3. `response_styles.yaml`
**Purpose**: Define response formatting and length styles

**How to modify**:
- Add/remove/edit response style entries
- Each style needs:
  - `id`: Unique identifier (lowercase, underscores)
  - `name`: Display name for users
  - `output_length`: short | long | very_long
  - `description`: Brief description

**Example**:
```yaml
response_styles:
  - id: bullet_points
    name: Bullet Points
    output_length: short
    description: Concise bullet-point format
```

**After modification**: Restart the backend to pick up changes

---

### 4. `models.yaml`
**Purpose**: Define available models and their pricing

**How to modify**:
- Edit model entries in different sections:
  - `quick_mode_default`: Default model for quick responses
  - `enhanced_mode_tiers`: Budget/Balanced/Premium model tiers
  - `free_models`: List of zero-cost models
  - `thinking_models`: Models with reasoning capabilities

**To UPDATE pricing from OpenRouter**:
```bash
python scripts/update_model_pricing.py
```
This will automatically fetch the latest pricing and update `models.yaml`

**Manual modification example**:
```yaml
enhanced_mode_tiers:
  balanced:
    - model_id: new-model/model-name
      provider: openrouter
      prompt_cost_per_1k: 0.001
      completion_cost_per_1k: 0.002
      context_length: 100000
      use_cases: ["general purpose"]
```

**After modification**: Restart the backend to pick up changes

---

## Important Notes

1. **YAML Syntax**: Be careful with indentation (use 2 spaces, not tabs)
2. **IDs must be unique**: Don't duplicate IDs within the same file
3. **IDs use underscores**: Use `snake_case` for IDs (e.g., `my_theme` not `my-theme` or `myTheme`)
4. **Restart required**: Backend must be restarted to load configuration changes
5. **Validation**: Invalid YAML will cause backend startup to fail - check logs for errors

## Testing Changes

After modifying any config file:

1. Stop the backend
2. Start the backend
3. Check logs for "Loaded config: filename.yaml" messages
4. Test that your changes appear in the application

## Troubleshooting

**Config not loading?**
- Check YAML syntax with an online validator
- Look for backend error logs
- Ensure file is in the correct `config/` directory
- Verify no duplicate IDs

**Pricing outdated?**
- Run `python scripts/update_model_pricing.py`
- This updates all model pricing from OpenRouter API