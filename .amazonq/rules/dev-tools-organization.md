## 👑 Primary Directive: Separation of Code and Tools

Your fundamental rule for file organization is the strict separation of **production source code** from **development artifacts**.

* ❌ **Development Tools Directory (`dev_tools/`)**: This is the designated workspace for any file that supports the development process but is **not** part of the final, shippable product. This includes tests, scripts, notes, documentation, and reports.

---

### 🤔 The Golden Rule: The Production Test

Before creating any file, ask this one question: **"Is this file required for the application to run in production?"**

* If **YES** ➡️ It is **source code**. Place it in the appropriate source directory (e.g., `students\`).
* If **NO** ➡️ It is a **development artifact**. Place it in the correct `dev_tools/` subfolder as defined below.

---

### 📂 `dev_tools/` Directory Structure

All development artifacts **must** be placed within the appropriate subfolder inside `dev_tools/`. The structure is based on the file's purpose.

* **🧪 Testing** → `dev_tools/testing/`
    * For unit tests, integration tests, and testing utilities.
    * *Example: A test for `src/main.py` goes in `dev_tools/testing/my_app/test_main.py`.*

* **🐛 Debugging** → `dev_tools/debugging/`
    * For temporary scripts used to troubleshoot or replicate bugs.

* **📚 Documentation** → `dev_tools/docs/`
    * For developer-facing documentation, API notes, or architectural diagrams.

* **⚙️ Utility Scripts** → `dev_tools/scripts/`
    * For helper scripts like database setup, deployment, or data processing.

* **📊 Reports & Logs** → `dev_tools/reports/`
    * For generated files like performance benchmarks, security scans, or code quality reports.

* **🔐 Security** → `dev_tools/security/`
    * For security-related configurations, scripts, or audit files not meant for production.

* **🛠️ Configs** → `dev_tools/config/`
    * For local development environment configurations or tool settings.

* **📝 Planning & Notes** → `dev_tools/planning/`
    * A consolidated folder for to-do lists, development diaries, work summaries, and rough notes.

* **🌐 MCP Server** → `dev_tools/mcp/<name-of-mcp-server>/`
    * For files specifically related to the MCP server's development and management.

By strictly adhering to this separation principle, the main project directory remains clean and represents only the final production code.