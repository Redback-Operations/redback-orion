# Shared Folder

This folder contains common project components that can be reused by all team members.

## Purpose

Use this folder for items that should not be duplicated inside individual task folders.

Current shared structure:

- `services/` - common service modules for the 3 agreed microservices
- `config/` - shared settings, thresholds, and paths
- `schemas/` - shared request and response formats and data contracts

## Example

If the detection team defines one JSON output format and the analytics team needs to read it, that format should be documented in `schemas/` so both teams follow the same structure.

If all services need the same confidence threshold or input path setting, keep it in `config/`.

If the backend team needs a reusable service module for one of the 3 microservices, place that code in `services/`.
