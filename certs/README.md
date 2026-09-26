# MediTraceX SSL Certificates Directory

This directory is used for public Certificate Authority (CA) certificates for secure remote cloud database connections (e.g. Aiven, AWS RDS, PlanetScale).

## Usage Options for Aiven MySQL CA Certificate

### Option 1: File in Repository (Easiest)
1. Download `ca.pem` from your Aiven Console (**Overview** → **CA Certificate**).
2. Save it to this folder as `aiven_ca.pem` (or `ca.pem`).
3. Commit and push. MediTraceX will automatically detect and load `certs/aiven_ca.pem`.

### Option 2: Render Secret Files (No commit needed)
1. In Render Dashboard → **`meditracex-backend`** → **Environment** → **Secret Files**.
2. Add a Secret File named `ca.pem` with path `/etc/secrets/ca.pem` and paste your Aiven CA certificate.
3. In Environment Variables, add `MYSQL_SSL_CA=/etc/secrets/ca.pem`.

### Option 3: Render Environment Variable (Direct text)
1. In Render Dashboard → **`meditracex-backend`** → **Environment**.
2. Add variable `MYSQL_SSL_CA_CONTENT` and paste the entire PEM text (including `-----BEGIN CERTIFICATE-----` and `-----END CERTIFICATE-----`).

> **Security Note**: Public CA certificates only contain public keys and root trust definitions; they do NOT contain private keys, passwords, or secrets.
