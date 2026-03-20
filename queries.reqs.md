input and output are totally unneeded

```yaml
queries: yaml
    get_recipe_text:
        description: Retrieves raw recipe text given a source identifier (URL, file path, or inline text)
        input: source_ref
        output: raw_text
    llm_completion:
        description: Retrieve an LLM completion
        input: raw_text
        output: raw_text
```

we specifically just need input and output models to be generated - the names like `raw_text` are totally unnecessary


```yaml
// + to llm_completion.yaml
classes:
  LlmCompletionInput:
    description: Input for llm_completion
    attributes:
      raw_text:
        range: string
        required: true

  LlmCompletionOutput:
    description: Output for llm_completion
    attributes:
      raw_text:
        range: string
        required: true
```