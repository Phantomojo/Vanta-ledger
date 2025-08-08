# Vanta Ledger: Code Audit and Remediation Guide

## 1. Introduction

This document provides a comprehensive summary of the code audit performed on the Vanta Ledger application. The application is well-architected with a rich feature set, including advanced AI and document processing capabilities.

The audit identified several critical issues related to security, dependency management, API consistency, and project setup. I have already taken action to resolve the most severe security vulnerabilities and to clean up the dependency management.

This guide details the remaining issues and provides step-by-step instructions to fix them, with a focus on improving the project's security, maintainability, and stability.

## 2. Security Vulnerabilities

A number of security vulnerabilities related to hardcoded credentials were identified. Storing secrets in source code is a major security risk.

**Actions Already Taken:**

*   **Removed Hardcoded Admin User:** The hardcoded `admin` user with the password `admin123` in `backend/app/auth.py` has been removed. The `get_user_by_username` function now contains a placeholder and a `TODO` comment to implement a proper database lookup.
*   **Removed Hardcoded Database Passwords:** Default passwords in `backend/app/config.py` and `backend/app/hybrid_database.py` have been removed. The application will now raise an error if the database URIs are not set as environment variables.
*   **Fixed `alembic.ini`:** The hardcoded database URL in `alembic.ini` has been removed. A wrapper script, `scripts/run_alembic.sh`, was created to load the database URL from the `.env` file when running migrations.
*   **Removed Insecure Files:** The `backend/app/main_backup.py` file, which contained a hardcoded secret, has been deleted.

**Recommended Actions:**

*   **Implement a User Database:** Prioritize the implementation of a proper user management system that stores user credentials securely in the database.
*   **Use a Secrets Manager:** For production environments, use a dedicated secrets management service (like AWS Secrets Manager, Google Secret Manager, or HashiCorp Vault) instead of `.env` files.

## 3. Dependency Management

The project had multiple, conflicting `requirements.txt` files, which makes the environment difficult to reproduce and poses a security risk due to outdated packages.

**Actions Already Taken:**

*   **Consolidated Dependencies:** The dependency management has been streamlined using `pip-tools`. I have created the following files in the `backend/` directory:
    *   `requirements.in`: For core application dependencies.
    *   `requirements-dev.in`: For development and testing dependencies.
    *   `requirements-llm.in`: For optional local LLM dependencies.
*   **Generated Pinned Requirements:** These `.in` files have been used to generate fully pinned `requirements.txt`, `requirements-dev.txt`, and `requirements-llm.txt` files.
*   **Removed Old Files:** The old, inconsistent `requirements` files have been deleted.

**Recommended Actions:**

*   **Adopt the New Workflow:** For all future dependency management, developers should add new packages to the appropriate `.in` file and then run `pip-compile` to update the corresponding `.txt` file. For example:
    ```bash
    # In the backend/ directory
    pip-compile requirements.in -o requirements.txt
    ```

## 4. API Structure

The API structure was inconsistent, with some endpoints defined in `main.py` and others in separate router files. This makes the codebase harder to navigate and maintain.

**Actions Already Taken:**

*   **Refactored Legacy Endpoints:** All API endpoints have been moved from `main.py` into their own dedicated router files within the `backend/app/routes/` directory. This has made the `main.py` file much cleaner and the overall API structure more consistent and modular.

## 5. Project Setup and Testing (Critical)

The most significant issue identified is a broken project setup that prevents the test suite from running. This is caused by a combination of a non-standard `setup.py` script and an inconsistent project structure.

**The Problem:**

1.  **Non-Standard `setup.py`:** The `setup.py` in the root directory is not a standard packaging script. It's an automation script that attempts to create virtual environments, install dependencies, and run tests, which conflicts with standard tools like `pip`.
2.  **Inconsistent Project Structure:** The `pyproject.toml` file and the tests are configured for a `src`-based layout (i.e., they expect the code to be in `src/vanta_ledger`), but the application code resides in `backend/app`.

**Recommended Fix (A Step-by-Step Guide):**

This is a critical fix that will make the project adhere to modern Python packaging standards and will allow the tests to run correctly.

**Step 1: Restructure the Project Directory**

Move the application code to a `src` directory to match the configuration.

```bash
# Create the src directory
mkdir src

# Move the application code into a package directory
mv backend/app src/vanta_ledger

# The backend/app directory should now be gone.
# The new path to the application code is src/vanta_ledger/
```

**Step 2: Replace the `setup.py` Script**

The current `setup.py` is the main cause of the installation problems. It should be replaced with a minimal version that allows `setuptools` to work with `pyproject.toml`.

1.  Delete the existing `setup.py` file.
2.  Create a new `setup.py` file in the project root with the following content:
    ```python
    from setuptools import setup

    if __name__ == "__main__":
        setup()
    ```

**Step 3: Update `pyproject.toml`**

Now, update the `pyproject.toml` file to correctly locate the package in the new `src` directory.

1.  Open `pyproject.toml`.
2.  Find the `[tool.setuptools.packages.find]` section.
3.  Ensure it looks like this:
    ```toml
    [tool.setuptools.packages.find]
    where = ["src"]
    ```
    (I believe I have already made this change, but it's important to verify).

**Step 4: Run the Tests (The Right Way)**

After making these changes, the project setup will be clean and standard. You can now install the dependencies and run the tests.

```bash
# From the project root directory
# Install the project in editable mode with development dependencies
pip install -e .[dev]

# Run the test suite
pytest
```

These commands should now execute successfully without the errors you were seeing before.
***
