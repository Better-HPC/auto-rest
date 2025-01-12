# Application Architecture

Auto-REST is built around a functional programming paradigm. 
It utilizes the factory pattern to dynamically generate application components based on the reflected database schema.
This enables flexible and efficient creation of components that are tailored to the specific structure of the database.

A strong preference is given to using sequential function calls rather than nested ones
This design improves code clarity and makes logic easier to follow.
Nested function design is used sparingly and only when it offers notable improvement to the overall code quality.

The diagram below illustrates the sequence of function calls triggered by the API.
Functions are grouped together into modules based on their common responsibilities.

![Architecture Diagram](../static/architecture.svg)
