# [Serpentua](https://serpentua.com) Data Validation Platform (DVP)

A web-based data validation platform that monitors file integrity through SHA-256 checksum verification. DVP continuously scans your assets on configurable schedules, alerts you when files have been modified or deleted, and provides reporting and export capabilities.

## Features

- **Asset Management** — Organize files into asset groups and assets, with support for local and SMB paths
- **Checksum Validation** — SHA-256 integrity checks with full history tracking per file
- **Scheduled Scans** — Configurable daily scan schedules with support for daily, weekly, bi-weekly, and monthly validation intervals
- **Dashboard** — Overview of total assets, passed/failed validations, alerts, and acknowledgements
- **Reporting & Export** — Generate and export CSV reports for asset objects, alerts, failed validations, and deleted files
- **Email Notifications** — SMTP-based alerting with TLS support
- **File Exclusions** — Exclude specific files or paths from validation scans
- **Organization Settings** — Store your organization profile for reporting context


## Tech Stack

- **Backend:** Python 3.13, Flask
- **Database:** MySQL 8.0 (via SQLAlchemy + PyMySQL)
- **Frontend:** Bootstrap 5, jQuery
- **Containerization:** Docker & Docker Compose

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd serpentua-dvp-docker
   ```

2. Review and update the `.env` file with your desired configuration:
   ```
   DB_USER=dvp
   DB_PASSWORD=<your-password>
   DB_NAME=dvp_app
   DB_HOST=db
   MYSQL_ROOT_PASSWORD=<your-root-password>
   SERVER_HOST=0.0.0.0
   SERVER_PORT=8443
   ```

3. Start the application:
   ```bash
   docker-compose up -d
   ```

4. Access the dashboard at `http://localhost:8443`

## Project Structure

```
serpentua-dvp-docker/
├── dvp/
│   ├── __init__.py        # Flask app initialization
│   ├── database.py        # Database connection configuration
│   ├── dbstruct.py        # Table schema definitions
│   ├── models.py          # SQLAlchemy ORM models
│   ├── views.py           # Route handlers
│   ├── forms.py           # WTForms form definitions
│   ├── file.py            # File scanning, checksums, and scheduled workers
│   ├── reports.py         # Report data formatting
│   ├── static/            # CSS, JS, fonts, and images
│   └── templates/         # Jinja2 HTML templates
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── runserver.py
└── dvp.pyproj
```

## File Path Mapping

The Docker container mounts the entire host filesystem at `/host` (read-only). When adding asset paths in the application, use the container path instead of the native OS path:

| Host Path (Windows)       | Container Path              |
|---------------------------|-----------------------------|
| `C:\data\files`           | `/host/mnt/c/data/files`    |
| `D:\validation_data`      | `/host/mnt/d/validation_data` |
| `E:\backups`              | `/host/mnt/e/backups`       |

The general pattern is: replace the drive letter `X:\` with `/host/mnt/x/` (lowercase).

## Configuration

| Environment Variable   | Default         | Description                  |
|------------------------|-----------------|------------------------------|
| `DB_USER`              | `dvp`           | MySQL database user          |
| `DB_PASSWORD`          | —               | MySQL database password      |
| `DB_NAME`              | `dvp_app`       | MySQL database name          |
| `DB_HOST`              | `db`            | MySQL host (container name)  |
| `MYSQL_ROOT_PASSWORD`  | —               | MySQL root password          |
| `SERVER_HOST`          | `0.0.0.0`       | Flask server bind address    |
| `SERVER_PORT`          | `8443`          | Flask server port            |

## License

This software is released under the [Serpentua Source Available License](LICENSE). You are free to use and modify the software, but you may not sell it, offer it as a service, or use it to compete with [Serpentua's](https://serpentua.com) products. See the [LICENSE](LICENSE) file for full terms.



##############################
LICENSE AGREEMENT
##############################

Serpentua Source Available License v1.0

Copyright (c) 2026 Serpentua (https://serpentua.com). All rights reserved.

Permission is hereby granted, free of charge, to any person or organization
("Licensee") obtaining a copy of this software and associated documentation
files (the "Software"), to use, copy, modify, and distribute the Software,
subject to the following conditions:

1. NON-COMMERCIAL RESTRICTION
   The Licensee shall NOT, directly or indirectly:
   a. Sell, resell, sublicense, rent, or lease the Software or any
      derivative works thereof;
   b. Offer the Software, or any derivative work thereof, as a hosted or
      managed service, software-as-a-service (SaaS), platform-as-a-service
      (PaaS), or any other "as-a-service" offering to third parties;
   c. Use the Software, or any derivative work thereof, to create, operate,
      or contribute to any product or service that competes with any product
      or service offered by Serpentua.

2. PERMITTED USES
   The Licensee MAY:
   a. Use the Software for internal, personal, or organizational purposes;
   b. Modify the Software for the Licensee's own use;
   c. Distribute copies of the Software or derivative works, provided that
      all copies include this license and that such distribution does not
      violate the restrictions in Section 1.

3. ATTRIBUTION
   All copies or substantial portions of the Software must include this
   license and the above copyright notice.

4. NO WARRANTY
   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
   OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.
   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
   CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
   TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE
   SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

5. TERMINATION
   This license is automatically terminated if the Licensee violates any of
   the terms above. Upon termination, the Licensee must cease all use and
   destroy all copies of the Software.
