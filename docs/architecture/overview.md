# Application Architecture

Auto-REST is built on three key frameworks.

1. **FastAPI:** Used to handle HTTP requests, including request middleware, routing, and handling.
2. **SQLAlchemy:** Manages database interactions, schema mapping, and query execution.
3. **Pydantic:** Leveraged by FastAPI to standardize interfaces and enforce data validation.

## Package Architecture

Auto-REST uses a functional programming paradigm with heavy emphasis on the factory design pattern.
Inder this approach, factory functions are used to dynamically generate application components on an as-needed basis.
This enables a flexible architecture capable of adapting to the target database and its schema.

Functions are grouped together into modules based on their common responsibilities.
The `__main__` module serves as the application entry point triggered by the command line.
Other modules provide encapsulation, ensuring modularity and separation of concerns.
Summaries are provided below for individual modules.

| Module                      | Description                                                                                                       |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------|
| [app](app.md)               | Manages the initialization and high level configuration of FastAPI applications.                                  |
| [cli](cli.md)               | Defines the application command-line interface and handles parsing user inputs.                                   |
| [handlers](handlers.md)     | Implements logic for handling individual requests, executing and returning user queries.                          |
| [interfaces](interfaces.md) | Generates Pydantic interfaces from SQLAlchemy components, enabling support for FastAPI's typing hinting features. |
| [models](models.md)         | Manages database interactions, including schema and table mappings.                                               |
| [queries](queries.md)       | Provides wrappers around common, repeatable database queries.                                                     |
| [routers](routers.md)       | Defines API routers, used to direct incoming request traffic to the correct handling logic.                       |

The diagram below outlines the dependency relationship between each module.
A flat architecture is preferred where feasible.
However, deeper dependency relationships are permitted when used to promote code maintainability and quality.

![Architecture Diagram](../_static/img/architecture.svg)

## Application Flow

The diagram below demonstrates the sequence of function calls initiated by the command-line application.
In general, functions are designed to be called sequentially, rather than being deeply nested.
This approach improves code clarity and makes logic easier to follow.
However, nested functions are allowed when they provide an improvement to code readability and maintainability.

![Call Flow Diagram](../_static/img/call_flow.svg)
