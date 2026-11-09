# LLM Provider Compatibility

DevFlow supports multiple LLM providers through three modes. This document details tested configurations, performance characteristics, and compatibility notes.

## Configuration Modes

DevFlow auto-detects which mode to use based on environment variables (priority order):

1. **Mode B (Generic LLM)** - If `LLM_API_KEY` is set
2. **Mode C (Anthropic API)** - If `ANTHROPIC_API_KEY` is set
3. **Mode A (Claude Code)** - Default if no API keys configured

## Mode A: Claude Code Reviews

**Configuration:**
```bash
# No configuration needed - uses existing Claude Code access
```

**Characteristics:**
- **Cost:** Free (uses your Claude Code subscription)
- **Speed:** Slow (~30-60s per review)
- **Quality:** Excellent (Claude Sonnet 4.5)
- **Availability:** Requires active Claude Code session

**Pros:**
- No API key needed
- Excellent review quality
- No per-review costs

**Cons:**
- Slower than API modes
- Subprocess overhead
- Requires Claude Code to be running

**Best for:**
- Users without API access
- Cost-sensitive projects
- When quality > speed

## Mode B: Generic LLM (OpenAI-compatible API)

**Configuration:**
```bash
# .env
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.provider.com/v1
LLM_MODEL=model-name
```

**Tested Providers:**

### DeepSeek (Recommended)

**Models tested:**
- `deepseek-v4-flash` ✓ Excellent (recommended)
- `deepseek-chat` ✓ Good
- `deepseek-coder` ✓ Good for code-heavy reviews

**Configuration:**
```bash
LLM_API_KEY=sk-your-deepseek-key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-v4-flash
```

**Performance:**
- Speed: Very fast (5-10s per review)
- Cost: Very cheap (~$0.001 per review)
- Quality: Excellent for code review
- JSON mode: ✓ Fully supported

**Notes:**
- Best overall value (speed + cost + quality)
- Excellent at structured output
- Good at security vulnerability detection

### OpenAI

**Models tested:**
- `gpt-4-turbo` ✓ Excellent
- `gpt-4o` ✓ Excellent
- `gpt-3.5-turbo` ✓ Good (faster, cheaper)

**Configuration:**
```bash
LLM_API_KEY=sk-your-openai-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4-turbo
```

**Performance:**
- Speed: Medium (15-25s for GPT-4, 10-15s for GPT-3.5)
- Cost: High (~$0.10 per review for GPT-4, ~$0.01 for GPT-3.5)
- Quality: Excellent (GPT-4), Good (GPT-3.5)
- JSON mode: ✓ Fully supported

**Notes:**
- GPT-4: Best quality but expensive
- GPT-3.5: Good balance for simpler reviews
- Excellent at architectural analysis

### GLM (Zhipu AI)

**Models tested:**
- `glm5.3-flash` ✓ Good (via nan.builders proxy)
- `glm-4` ✓ Good

**Configuration:**
```bash
# Via nan.builders proxy
LLM_API_KEY=sk-your-nanbuilders-key
LLM_BASE_URL=https://api.nan.builders/v1
LLM_MODEL=glm5.3-flash

# Or direct
LLM_API_KEY=your-zhipu-key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4
```

**Performance:**
- Speed: Fast (8-15s per review)
- Cost: Cheap (~$0.002 per review)
- Quality: Good
- JSON mode: ✓ Supported (with occasional formatting issues)

**Notes:**
- Good alternative to DeepSeek
- Occasionally needs response cleanup
- Works well via nan.builders proxy

### Groq

**Models tested:**
- `llama-3.3-70b-versatile` ✓ Good
- `mixtral-8x7b-32768` ✓ Good

**Configuration:**
```bash
LLM_API_KEY=your-groq-key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```

**Performance:**
- Speed: Very fast (3-8s per review)
- Cost: Free tier available, then cheap
- Quality: Good (Llama 3.3), Fair (Mixtral)
- JSON mode: ✓ Mostly supported

**Notes:**
- Fastest inference available
- Free tier: 30 requests/min
- Occasionally truncates long responses

### Other OpenAI-compatible Providers

**Known to work:**
- Together.ai (various models)
- Anyscale Endpoints (Llama, Mistral)
- Fireworks AI (Llama, Mixtral)
- Replicate (various models)

**Configuration pattern:**
```bash
LLM_API_KEY=provider-specific-key
LLM_BASE_URL=https://provider-api-url/v1
LLM_MODEL=model-name
```

**Compatibility check:**
- Must support `/v1/chat/completions` endpoint
- Should support JSON mode (`response_format: {type: "json_object"}`)
- Context window: minimum 8K tokens recommended

## Mode C: Anthropic API

**Configuration:**
```bash
# .env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Models available:**
- Claude 3.5 Sonnet (default)
- Claude 3 Opus
- Claude 3 Haiku

**Performance:**
- Speed: Medium (15-30s per review)
- Cost: Medium (~$0.03 per review)
- Quality: Excellent
- JSON mode: ✓ Fully supported (via tool use)

**Pros:**
- Official Anthropic models
- Excellent reasoning quality
- Strong at security analysis
- Good at architectural review

**Cons:**
- More expensive than Mode B alternatives
- Slower than DeepSeek/Groq
- Requires API key purchase

**Best for:**
- Users who want official Claude API
- Critical security reviews
- Complex architectural analysis

## Performance Comparison

| Provider | Model | Speed | Cost/Review | Quality | JSON Support |
|----------|-------|-------|-------------|---------|--------------|
| **DeepSeek** | v4-flash | ⚡⚡⚡ 5-10s | 💰 $0.001 | ⭐⭐⭐⭐ | ✓ Excellent |
| Groq | Llama 3.3 | ⚡⚡⚡ 3-8s | 💰 Free/cheap | ⭐⭐⭐ | ✓ Good |
| OpenAI | GPT-3.5 | ⚡⚡ 10-15s | 💰💰 $0.01 | ⭐⭐⭐ | ✓ Excellent |
| GLM | glm5.3-flash | ⚡⚡ 8-15s | 💰 $0.002 | ⭐⭐⭐ | ✓ Good |
| OpenAI | GPT-4 | ⚡ 15-25s | 💰💰💰 $0.10 | ⭐⭐⭐⭐⭐ | ✓ Excellent |
| Anthropic | Sonnet 3.5 | ⚡ 15-30s | 💰💰 $0.03 | ⭐⭐⭐⭐⭐ | ✓ Excellent |
| Claude Code | Sonnet 4.5 | 30-60s | Free | ⭐⭐⭐⭐⭐ | ✓ Excellent |

**Legend:**
- Speed: ⚡⚡⚡ Very fast, ⚡⚡ Fast, ⚡ Medium
- Cost: 💰 Very cheap, 💰💰 Medium, 💰💰💰 Expensive
- Quality: ⭐⭐⭐⭐⭐ Excellent, ⭐⭐⭐⭐ Very good, ⭐⭐⭐ Good

## Recommendations by Use Case

### For daily development (speed matters)
```bash
LLM_API_KEY=sk-your-key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-v4-flash
```
**Why:** Fast (5-10s), cheap, good quality for routine reviews.

### For critical reviews (quality matters)
```bash
ANTHROPIC_API_KEY=sk-ant-your-key
# Uses Claude 3.5 Sonnet
```
**Why:** Best reasoning, excellent at security/architecture analysis.

### For cost-sensitive projects
```bash
# No configuration - uses Claude Code mode
```
**Why:** Free, no per-review costs, excellent quality.

### For maximum speed
```bash
LLM_API_KEY=your-groq-key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```
**Why:** Fastest inference (3-8s), free tier available.

### For best balance
```bash
LLM_API_KEY=sk-your-key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-v4-flash
```
**Why:** Excellent speed + cost + quality combination.

## Common Issues

### Model doesn't support JSON mode

**Symptoms:**
- Reviews return plain text instead of structured issues
- Parsing errors

**Solution:**
Switch to a model with JSON support:
```bash
# Tested models with excellent JSON support:
LLM_MODEL=deepseek-v4-flash     # DeepSeek
LLM_MODEL=gpt-4-turbo           # OpenAI
LLM_MODEL=glm5.3-flash          # GLM
```

### Rate limits hit

**Symptoms:**
- 429 errors
- "Rate limit exceeded"

**Solutions:**

1. **Free tier limits:**
   - Groq: 30 req/min → Wait or upgrade
   - OpenAI free tier: 3 req/min → Upgrade to paid

2. **Paid tier limits:**
   - Add delays between reviews
   - Use cheaper model (higher limits)

### Response truncation

**Symptoms:**
- Incomplete reviews
- Missing issues in large diffs

**Solutions:**

1. **Context window too small:**
   - Use model with larger context:
     - Mixtral: 32K tokens
     - GPT-4 Turbo: 128K tokens
     - Claude 3.5: 200K tokens

2. **Split large diffs:**
   ```bash
   # Review files separately
   git diff -- file1.py | devflow review
   git diff -- file2.py | devflow review
   ```

## Testing Your Configuration

Use the test script to verify your setup:

```bash
cd /home/joseal/projects/joaltocu/framework
python test_generic_llm.py
```

Expected output:
```
Environment Check:
✓ LLM_API_KEY: sk-0jeOox... (set)
✓ LLM_BASE_URL: https://api.nan.builders/v1
✓ LLM_MODEL: deepseek-v4-flash

Running code review test...
Review completed successfully!

Found 2 issues:
- CRITICAL: Hardcoded API key in config file
- HIGH: Missing input validation
```

## Adding New Providers

To use an unlisted OpenAI-compatible provider:

1. **Find API endpoint:**
   - Should be `https://provider.com/v1` or similar
   - Must support `/chat/completions`

2. **Configure .env:**
   ```bash
   LLM_API_KEY=your-key
   LLM_BASE_URL=https://provider.com/v1
   LLM_MODEL=model-name
   ```

3. **Test:**
   ```bash
   python test_generic_llm.py
   ```

4. **Verify JSON support:**
   - Check if reviews return structured issues
   - If not, provider may not support `response_format`

5. **Report compatibility:**
   - If it works well, please share in GitHub issues
   - Helps other users find good providers
