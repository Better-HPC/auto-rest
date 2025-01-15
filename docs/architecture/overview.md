# Application Architecture

Auto-REST uses a functional programming paradigm and relies heavily on the factory design pattern.
In this approach, factory functions are used to dynamically generate application components.
This enables a flexible architecture capable of adapting to the underlying database structure.

In general, functions are designed to be called sequentially, rather than being nested together.
This approach improves code clarity and makes logic easier to follow.
Nested functions are used occasionally, but only when they offer a notable improvement to the overall code quality.

The diagram below demonstrates the sequence of function calls initiated by the command-line application.
Functions are grouped together into modules based on their common responsibilities.

![Architecture Diagram](../static/architecture.svg)
