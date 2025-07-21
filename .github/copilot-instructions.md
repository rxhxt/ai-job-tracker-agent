<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Job AI Agent - Copilot Instructions

This is a Python-based AI agent for automated job application tracking with Gmail and Google Sheets integration.

## Project Structure
- Follow the existing modular architecture with separate services for Gmail, Sheets, email parsing, and notifications
- Use proper error handling and logging throughout the codebase
- Implement OAuth2 authentication for Google APIs
- Use environment variables for all sensitive configuration

## Code Style Guidelines
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters and return values
- Implement proper exception handling with specific exception types
- Add comprehensive docstrings for all classes and methods
- Use dataclasses for model definitions

## AI/ML Integration
- Integrate with Google Gemini API for advanced email parsing and classification
- Implement fallback patterns for email parsing when AI is unavailable
- Use regex patterns as backup for email classification
- Consider privacy and data handling when processing email content

## API Integration Best Practices
- Implement proper rate limiting for Google APIs
- Use batch operations where possible for Google Sheets updates
- Handle API quotas and implement exponential backoff
- Cache authentication tokens appropriately

## Security Considerations
- Never commit credential files or API keys
- Use service accounts for Google Sheets access
- Implement proper scope limiting for Gmail API access
- Sanitize email content before processing

## Testing
- Write unit tests for all service classes
- Mock external API calls in tests
- Test email parsing with various email formats
- Include integration tests for end-to-end workflows
