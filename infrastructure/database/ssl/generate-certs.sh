#!/bin/bash

# SSL Certificate Generation Script for Vanta Ledger
# Generated: August 4, 2025

set -e

echo "🔐 Generating SSL certificates for Vanta Ledger..."

# Create SSL directory structure
mkdir -p ssl/{postgresql,mongodb,pgadmin}

# Generate CA private key and certificate
echo "📜 Generating Certificate Authority..."
openssl genrsa -out ssl/ca-key.pem 4096
openssl req -new -x509 -days 365 -key ssl/ca-key.pem -sha256 -out ssl/ca.pem \
    -subj "/C=KE/ST=Nairobi/L=Nairobi/O=Vanta Ledger/OU=IT/CN=Vanta Ledger CA"

# PostgreSQL SSL certificates
echo "🐘 Generating PostgreSQL SSL certificates..."
openssl genrsa -out ssl/postgresql/postgresql-key.pem 2048
openssl req -new -key ssl/postgresql/postgresql-key.pem -out ssl/postgresql/postgresql.csr \
    -subj "/C=KE/ST=Nairobi/L=Nairobi/O=Vanta Ledger/OU=IT/CN=postgresql.vantaledger.local"
openssl x509 -req -in ssl/postgresql/postgresql.csr -CA ssl/ca.pem -CAkey ssl/ca-key.pem \
    -CAcreateserial -out ssl/postgresql/postgresql-cert.pem -days 365 -sha256
cat ssl/postgresql/postgresql-key.pem ssl/postgresql/postgresql-cert.pem > ssl/postgresql/postgresql.pem
chmod 600 ssl/postgresql/postgresql.pem

# MongoDB SSL certificates
echo "🍃 Generating MongoDB SSL certificates..."
openssl genrsa -out ssl/mongodb/mongodb-key.pem 2048
openssl req -new -key ssl/mongodb/mongodb-key.pem -out ssl/mongodb/mongodb.csr \
    -subj "/C=KE/ST=Nairobi/L=Nairobi/O=Vanta Ledger/OU=IT/CN=mongodb.vantaledger.local"
openssl x509 -req -in ssl/mongodb/mongodb.csr -CA ssl/ca.pem -CAkey ssl/ca-key.pem \
    -CAcreateserial -out ssl/mongodb/mongodb-cert.pem -days 365 -sha256
cat ssl/mongodb/mongodb-key.pem ssl/mongodb/mongodb-cert.pem > ssl/mongodb/mongodb.pem
chmod 600 ssl/mongodb/mongodb.pem

# pgAdmin SSL certificates
echo "🖥️ Generating pgAdmin SSL certificates..."
openssl genrsa -out ssl/pgadmin/pgadmin-key.pem 2048
openssl req -new -key ssl/pgadmin/pgadmin-key.pem -out ssl/pgadmin/pgadmin.csr \
    -subj "/C=KE/ST=Nairobi/L=Nairobi/O=Vanta Ledger/OU=IT/CN=pgadmin.vantaledger.local"
openssl x509 -req -in ssl/pgadmin/pgadmin.csr -CA ssl/ca.pem -CAkey ssl/ca-key.pem \
    -CAcreateserial -out ssl/pgadmin/pgadmin-cert.pem -days 365 -sha256
cat ssl/pgadmin/pgadmin-key.pem ssl/pgadmin/pgadmin-cert.pem > ssl/pgadmin/pgadmin.pem
chmod 600 ssl/pgadmin/pgadmin.pem

# Set proper permissions
chmod 600 ssl/ca-key.pem
chmod 644 ssl/ca.pem

echo "✅ SSL certificates generated successfully!"
echo "📁 Certificates location: ssl/"
echo "🔐 Remember to keep private keys secure!" 