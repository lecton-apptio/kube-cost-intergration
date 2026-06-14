# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-14

### Added
- Initial production release
- `CloudabilityClient` for Kubernetes cost tracking via Cloudability API
- `NamespaceCost` dataclass for type-safe cost data
- OpenToken authentication support
- Comprehensive test suite (85%+ coverage)
- Full type hints with `py.typed` marker
- Zero external dependencies (uses only Python stdlib)
- Production-grade error handling
- Token redaction for security
- Environment variable loading utility

### Features
- Get namespace costs with date range filtering
- Detailed cost breakdown by service, lease type, and usage family
- Automatic date range defaults (last 30 days)
- Configurable cost dimensions
- Clean, typed API following best practices

### Documentation
- Comprehensive README with examples
- API reference documentation
- Authentication guide
- Development setup instructions

### Security
- Automatic token redaction in logs
- Secure credential handling
- Environment variable support

## [0.1.0] - 2026-06-14

### Added
- Initial bootstrap and project structure
- Basic Cloudability API integration
- OpenToken authentication discovery

---

**Made with ❤️ by Bob**