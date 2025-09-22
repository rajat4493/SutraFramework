# Changelog
All notable changes to this project will be documented here.
This project follows [Semantic Versioning](https://semver.org/).

## [0.1.1] - 2025-09-22
### Fixed
- Ollama model tag mismatch causing `HTTP 404` in analyzer/classifier/summarizer.
### Changed
- Error messages now include Ollama response body.

## [0.1.0-alpha] - 2025-09-21
### Added
- Local-first multi-agent runner (`sutra.py`) with retries & JSON coercion.
- Example: `catagent_pipeline.py` (analyzer → classifier → summarizer).
- CLI: `python3 sutra.py run <pipeline>.py --input '{"text":"..."}'`.
