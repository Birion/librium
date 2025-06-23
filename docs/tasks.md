# Librium Improvement Tasks

This document contains a prioritised list of tasks for improving the Librium codebase. Each task is marked with a checkbox that can be checked off when completed.

## Architecture Improvements

### Database and ORM
- [x] Implement database migrations using Alembic to manage schema changes
- [x] Add database indexing for frequently queried fields to improve performance
- [x] Implement connection pooling for better database performance
- [x] Migrate from Pony.ORM to SqlAlchemy
- [x] Add database transaction management for critical operations
- [x] Create a database backup and restore functionality

### Application Structure
- [x] Implement a service layer between views and database models
- [x] Implement proper error handling and logging throughout the application
- [x] Create a configuration management system for different environments (dev, test, prod)
- [x] Implement API versioning for better maintainability

[//]: # (- [ ] Implement centralised binary storage for cover images)

### Security
- [x] Implement API authentication tokens
- [ ] Implement input validation for all user inputs
- [ ] Add CSRF protection for forms
- [ ] Add rate limiting for API endpoints
- [ ] Implement authentication and authorisation
- [ ] Implement secure password storage if user accounts are added

## Code-Level Improvements

### Testing
- [ ] Increase test coverage for all components
- [ ] Add integration tests for critical user flows
- [ ] Ensure all tests are passing and testing correctly
- [ ] Implement property-based testing for complex logic
- [ ] Add performance tests for critical operations
- [ ] Implement continuous integration for automated testing

### Models
- [x] Add data validation in model properties
- [x] Implement soft delete functionality for books and other entities
- [x] Add created_at and updated_at timestamps to all models
- [ ] Add more helper methods for common queries
- [ ] Implement full-text search for books

### Views and Templates
- [ ] Implement proper pagination for book listings
- [ ] Add sorting options for book listings
- [ ] Improve error handling in view functions
- [ ] Implement AJAX for form submissions to improve the user experience
- [ ] Add client-side validation for forms

### API
- [ ] Document API endpoints using OpenAPI/Swagger
- [ ] Implement consistent error responses for API endpoints
- [ ] Add filtering and sorting options for API endpoints
- [ ] Implement bulk operations for API endpoints
- [ ] Add caching for frequently accessed API endpoints

### Frontend
- [ ] Optimise asset loading for better performance
- [ ] Implement responsive design for mobile devices
- [ ] Add accessibility features (ARIA attributes, keyboard navigation)
- [ ] Implement progressive enhancement for JavaScript features
- [ ] Add dark mode support

## Feature Improvements

### Book Management
- [ ] Implement batch operations for books (delete, update)
- [ ] Add reading progress tracking
- [ ] Implement book import from external sources (ISBN lookup)
- [ ] Add book lending tracking
- [ ] Implement book recommendations based on reading history

### Metadata Management
- [ ] Add support for custom metadata fields
- [ ] Implement hierarchical genres
- [ ] Add support for multiple editions of the same book
- [ ] Implement author merging for duplicate authors
- [ ] Add support for book tags

### Collection Organisation
- [ ] Implement custom shelves/collections
- [ ] Add support for reading lists
- [ ] Implement advanced search with multiple criteria
- [ ] Add statistics and visualisations for the collection
- [x] Implement export to various formats (CSV, JSON, etc.)

## Documentation Improvements

### User Documentation
- [ ] Create comprehensive user guide
- [ ] Add inline help and tooltips
- [ ] Create FAQ section
- [ ] Implement contextual help

### Developer Documentation
- [ ] Create API documentation
- [ ] Document database schema
- [ ] Add a code style guide
- [ ] Create contribution guidelines
- [ ] Document deployment process

## DevOps Improvements

### Deployment
- [ ] Create a Docker container for easy deployment
- [ ] Implement CI/CD pipeline
- [ ] Add monitoring and alerting
- [ ] Implement automated backups
- [ ] Create deployment documentation

### Performance
- [ ] Implement caching for frequently accessed data
- [ ] Optimize database queries
- [ ] Implement lazy loading for images
- [ ] Add compression for static assets
- [ ] Implement server-side rendering for critical content
