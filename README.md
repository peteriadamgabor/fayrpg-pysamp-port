# FayRPG 2.0 - Python Port

[![Status](https://img.shields.io/badge/status-discontinued-red)](.)
[![open.mp](https://img.shields.io/badge/server-open.mp_v1.4-blue)](https://open.mp/)
[![PySAMP](https://img.shields.io/badge/framework-PySAMP-blue.svg)](https://github.com/pysamp)
[![License](https://img.shields.io/github/license/peteriadamgabor/fayrpg-pysamp-port)](https://github.com/peteriadamgabor/fayrpg-pysamp-port/blob/master/LICENSE.md)

This repository houses the source code for a modernized software port of a legacy Grand Theft Auto: San Andreas gamemode. It is a comprehensive translation of the 2011 'Version 2.0' of the Hungarian FayRPG server (est. 2008), converting the original Pawn implementation to Python via the `PySAMP` framework.

> [!WARNING]
> **Project Status: Discontinued**
>
> Development on this project has been formally discontinued, and the repository is now archived. The cessation of active development is attributable to temporal constraints and the project's considerable scope—a common outcome for ambitious, non-commercial endeavors. The source code is presented in its current, incomplete state and is made available strictly for archival, educational, or experimental purposes.

> [!CAUTION]
> **Important Usage Stipulation**
>
> The use of the name "FayRPG" in any derivative works or future developments based on this source code is expressly **prohibited**. This stipulation is in place to honor the legacy of the original server and to preclude any potential community confusion. Consequently, any derivative works must be released under a distinct and original project name.

---

## 📖 Project Overview

This project originated from the objective of developing a complete and modernized reinterpretation of a notable legacy roleplaying server. The primary objective extended beyond a mere feature-for-feature replication; it sought to preserve the essential gameplay ethos and community atmosphere of the original server. This was to be achieved by leveraging the substantial technical advantages afforded by the `open.mp` platform and the Python programming language. This technological stack was selected to facilitate the implementation of more sophisticated features, to enhance server performance, and to establish a more efficient and maintainable development workflow compared to the limitations of the original Pawn scripting environment.

### Specification

| Detail                | Specification        |
|-----------------------|----------------------|
| **Original Project**  | FayRPG 2.0 (2011)    |
| **Original Language** | Pawn                 |
| **Target Language**   | Python 3.10 (32-bit) |
| **Framework**         | PySAMP               |
| **Server Platform**   | `open.mp` (v1.4+)    |
| **Current Status**    | Discontinued         |

## 📊 Development State Analysis

The project is best characterized as a proof-of-concept or a foundational software architecture. Although the core server infrastructure and main application loop are implemented, it has not achieved feature parity with the original and cannot be considered to be in a deployable or playable condition. Substantial development effort is necessary to implement the numerous gameplay systems that constituted the definitive user experience of the original server.

#### Implemented Components:

* **🐳 Dockerized Core Server**: The environment is fully containerized, which streamlines the setup process for new developers.
* **🗄️ Database Integration**: A robust, dual-database backend utilizing PostgreSQL and SurrealDB has been connected and is functional for data persistence.
* **👤 Basic Player Account Management**: Core functionalities including account registration, authentication, and the persistence of essential character data have been implemented.
* **🏗️ Module Scaffolding**: The foundational structure for key architectural modules, as defined in `server.settings.toml`, has been established to guide future feature development.

#### Incomplete or Unimplemented Features:

* **💰 Job and Faction Systems**: The majority of the defining employment and faction-based mechanics have not yet been implemented.
* **🏡 Player-Owned Assets**: Systems governing player-owned properties, businesses, and vehicles are not fully functional.
* **🖥️ Advanced User Interface**: The current user interface is rudimentary and lacks the sophisticated, custom elements required for a polished user experience.
* **🌐 Multi-Language Support**: While the system is architected for localization, the translation files require extensive population and completion.
* **🎲 Core Gameplay Logic**: A significant portion of the fundamental gameplay logic, encompassing economic models, item interactions, and dynamic server events, is absent.

## 🛠️ Technology Stack

The project was architected utilizing a modern, maintainable technology stack, selected to provide a robust foundation for a large-scale gamemode implementation.

* **`open.mp`**: The core server platform, offering enhanced performance and stability relative to the original SA-MP server.
* **`PySAMP`**: A high-level framework that enables gamemode development in Python, promoting more structured, readable, and maintainable code.
* **`Python 3`**: The primary programming language for all gamemode logic, selected for its extensive standard library and modern programming paradigms.
* **`PostgreSQL`**: The primary relational database, employed for its proven reliability and robustness in managing critical, structured data such as player accounts.
* **`SurrealDB`**: A flexible, multi-model database utilized for less structured or ephemeral data, including player inventories and server logs.
* **`Docker`**: The containerization platform used for the entire stack, ensuring a consistent and reproducible environment for both development and production.
* **Plugins**: Incorporates essential third-party plugins, such as the Incognito Streamer Plugin.

## 🌍 Localization Architecture

The application was architected with integral multi-language support to allow for the complete translation of the gamemode into various languages. The localization system is managed via TOML configuration files, a decision intended to simplify the contribution process for non-technical community members. It should be noted, however, that the localization feature is in an incomplete state. The provided localization files for Hungarian (`hu`) are the most developed but are not exhaustive, and translation for other languages has not been initiated.

## 🚀 Environment Setup and Execution

>**Recommendation**: The use of the provided Docker environment is strongly recommended. This containerized environment encapsulates all requisite server dependencies, including database services and the specific Python runtime, thereby ensuring environment consistency and mitigating setup discrepancies across different development machines. To provision a local instance of the server, the following steps should be executed.

#### Prerequisites:

* [Docker Engine](https://docs.docker.com/engine/install/)
* [Docker Compose](https://docs.docker.com/compose/install/)

#### Installation and Configuration:

1.  **Clone the Repository:**
    ```sh
    git clone [https://github.com/YourUsername/YourRepo.git](https://github.com/YourUsername/YourRepo.git) my-rpg-project
    cd my-rpg-project
    ```
2.  **Create Environment File:**
    The server requires a `.env` file for secret management at the Docker level. Create this file in the project root with the following database credentials:
    ```.env
    # .env file
    PG_PASS=your_strong_postgres_password
    SR_USER=your_surrealdb_user
    SR_PASS=your_strong_surrealdb_password
    ```
3.  **Review Docker Compose Configuration:**
    The `docker-compose.yml` file orchestrates all necessary services. The default configuration is generally sufficient for local development.

4.  **Launch the Server Environment:**
    Execute the following command to build and start all services in detached mode:
    ```sh
    docker-compose up -d
    ```
    Upon successful execution, the server will be accessible at `localhost:7777`.

## 🛠️ Development Utilities

The project repository includes several command-line utilities designed to assist in the development process.

* **Database Migrations**: To generate a new migration script that reflects changes in the SQLAlchemy models, execute:
    ```sh
    python tools/migration/migration.py migrate "Descriptive commit message" --autogenerate
    ```
* **Map Data Conversion**: To convert legacy map files from `.pwn` format to a Python-compatible structure, use the following command:
    ```sh
    python tools/mapconverter/map_converter.py pwn-convert map
    ```

## ⚙️ Application Configuration

The application uses a set of `.toml` files for configuration. The primary file for sensitive information is `.secrets.toml`.

#### `.secrets.toml`

This file contains sensitive data such as API keys and database passwords required by the Python application. This file **must not** be committed to version control. It should be created manually in the project root.

```toml
# .secrets.toml

[secrets]
DB_PASSWORD = "ANONYMIZED_DB_PASSWORD"
SERVER_PASSWORD = "ANONYMIZED_SERVER_PASSWORD"
SURREALDB_PASSWORD = "ANONYMIZED_SURREALDB_PASSWORD"
SMTP_KEY = "ANONYMIZED_SMTP_KEY"
````

-----

## 🤝 Contribution Guidelines

External contributions to this project are permitted. Although active development by the original project maintainers is infrequent due to temporal limitations, submitted pull requests will be reviewed and potentially merged as time allows. Developers are encouraged to fork the repository for independent development. Contributions of particular value would include the implementation of missing features, the resolution of existing software defects, and the expansion of localization support.

## 📄 Licensing Information

This project is distributed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/). This license permits the sharing and adaptation of the source code, provided that appropriate attribution is given to the original work and any derivative works are distributed under the same license. For the full legal text and further details, please consult the `LICENSE.md` file.

## ❤️ Acknowledgements

  * The original developers of **FayRPG**, whose foundational work provided the inspiration for this project.
  * The development teams of **open.mp** and **SA-MP**, for their sustained efforts in creating and maintaining the platforms upon which the community is established.
  * The developers of the **PySAMP** framework, for providing the essential tools that enable modern Python-based development for Grand Theft Auto: San Andreas.
