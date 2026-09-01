# Architecture

Answer each of these, in your own words, once the system has taken real shape.

- What are the moving pieces, and how do they talk to each other?

        Vue 3 CDN
            ↓
        Flask REST API
            ↓
        Service layer
            ↓
        Repository/SQLAlchemy
            ↓
        PostgreSQL
        
- Where does each piece run?
- What is the request path for one representative user action, end to end?
- What did you decide *not* to build, and why?
