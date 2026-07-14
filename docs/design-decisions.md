# Design Decisions

## Overview

The Code Review Assistant was designed with the goal of combining deterministic static analysis with Large Language Models (LLMs) to provide accurate, explainable, and actionable code reviews.

Throughout development, several architectural and technology decisions were made to balance simplicity, maintainability, privacy, extensibility, and testing.

This document explains the reasoning behind those decisions and discusses the associated trade-offs.

---

# Decision 1: Python as the Initial Target Language

## Decision

Support only Python in Version 1.

## Reason

Supporting multiple languages would require:

- Multiple parsers
- Multiple static analyzers
- Different prompt strategies
- Language-specific report handling

Focusing on a single language allowed the architecture to mature before introducing additional complexity.

## Trade-offs

Advantages:

- Faster development
- Simpler testing
- Better code quality

Disadvantages:

- No multi-language support
- Smaller initial user base

## Future Work

Introduce language plugins for Java, JavaScript, C++, and Go.

---

# Decision 2: Ruff Instead of Flake8

## Decision

Use Ruff as the primary static analyzer.

## Reason

Ruff offers:

- Very high performance
- JSON output
- Compatibility with many Flake8 rules
- Active development

## Trade-offs

Advantages:

- Fast execution
- Easy integration
- Modern ecosystem

Disadvantages:

- Python-only
- Some rule mappings require normalization

---

# Decision 3: Bandit for Security Analysis

## Decision

Use Bandit alongside Ruff.

## Reason

Ruff focuses primarily on code quality.

Bandit specializes in Python security vulnerabilities such as:

- shell=True
- hardcoded credentials
- unsafe deserialization

Using both tools increases review coverage.

## Trade-offs

Advantages:

- Better security detection
- Complements Ruff

Disadvantages:

- Additional dependency
- Occasional overlapping findings

---

# Decision 4: Local LLM Using Ollama

## Decision

Use Ollama instead of cloud-hosted APIs.

## Reason

The project requirement emphasizes privacy.

Running locally means:

- Source code remains on the user's machine.
- No API costs.
- Offline operation.
- Easy experimentation with models.

## Trade-offs

Advantages

- Privacy
- No recurring cost
- Offline support

Disadvantages

- Slower inference on some hardware
- Users must install Ollama
- Performance depends on local resources

---

# Decision 5: Dependency Injection

## Decision

Construct dependencies through an ApplicationContainer.

## Reason

Dependency Injection improves modularity.

Services depend on abstractions rather than creating concrete implementations.

Example:

ReviewService depends on BaseLLM instead of OllamaLLM directly.

## Trade-offs

Advantages

- Easier testing
- Better maintainability
- Easier replacement of implementations

Disadvantages

- Slightly more initial complexity

---

# Decision 6: MockLLM for Testing

## Decision

Use MockLLM instead of real Ollama during automated tests.

## Reason

Real LLM responses are:

- Non-deterministic
- Slow
- Hardware-dependent

MockLLM ensures tests are deterministic and suitable for continuous integration.

## Trade-offs

Advantages

- Reliable tests
- Fast execution
- No external dependency

Disadvantages

- Does not measure actual model quality

---

# Decision 7: Pydantic Response Validation

## Decision

Validate every LLM response using Pydantic.

## Reason

LLMs may generate malformed or incomplete JSON.

Validation ensures:

- Correct schema
- Required fields
- Type safety

## Trade-offs

Advantages

- Robust error handling
- Strong contracts

Disadvantages

- Cannot verify factual correctness

---

# Decision 8: Prompt Engineering

## Decision

Use structured prompts with explicit instructions.

## Reason

The prompt instructs the model to:

- Verify findings against the source.
- Avoid hallucinations.
- Merge duplicate findings.
- Respect analyzer severity.
- Return only JSON.

## Trade-offs

Advantages

- Better consistency
- Reduced false positives

Disadvantages

- Requires ongoing tuning

---

# Decision 9: Markdown and JSON Reports

## Decision

Support both Markdown and JSON output.

## Reason

Markdown is human-readable.

JSON is machine-readable.

Supporting both enables future integrations.

## Trade-offs

Advantages

- Flexible output
- Easier automation

Disadvantages

- Slightly more maintenance

---

# Decision 10: Modular Architecture

## Decision

Separate the system into independent modules.

## Reason

Each module has one responsibility.

Examples:

- Parser
- Analyzer
- Prompt Builder
- LLM
- Response Parser
- Report Generator

## Trade-offs

Advantages

- Easier testing
- Easier maintenance
- Better scalability

Disadvantages

- More files
- Slightly steeper learning curve

---

# Alternative Approaches Considered

## Cloud LLM APIs

Pros

- Better models
- Faster inference

Cons

- Privacy concerns
- API cost
- Internet dependency

---

## GitHub CodeQL

Pros

- Enterprise-grade analysis

Cons

- Complex setup
- Repository-oriented
- Less suitable for lightweight CLI use

---

## Single Monolithic Design

Pros

- Fewer files
- Simpler initially

Cons

- Difficult testing
- Poor scalability
- Tight coupling

---

# Lessons Learned

Developing this project highlighted several important software engineering concepts.

- Static analysis and AI complement each other.
- LLM output must always be validated.
- Prompt engineering significantly influences output quality.
- Dependency injection simplifies testing.
- Small, focused services improve maintainability.
- Automated testing is essential for reliable software.
- Architectural decisions are as important as implementation details.

---

# Conclusion

The final architecture prioritizes modularity, maintainability, privacy, and extensibility.

While the current implementation focuses on Python and local inference, the architecture is designed to accommodate additional languages, analyzers, report formats, and LLM providers with minimal changes to the existing codebase.