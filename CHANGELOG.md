# Changelog

## [main] - Migration to OpenAI fallback
### Changed
- Switched fallback model from GPT4All to OpenAI ChatGPT.
- Removed `gpt4all`, local Mistral model, and llama.cpp dependencies.
- Updated `fallback_chain.py` to rely only on OpenAI ChatCompletion API.
- Improved error handling and fallback routing logic.

## [GPT4All] - Archived working GPT4All branch
### Added
- Full support for local inference with GPT4All Mistral 7B model.
- Telegram bot fallback routing using local GGUF model via llama.cpp.
- Admin panel for Telegram support with FAQ saving, reply logic and feedback.
