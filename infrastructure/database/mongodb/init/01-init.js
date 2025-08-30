
// MongoDB initialization script for Vanta Ledger
// This script runs when the MongoDB container starts

// Switch to the vanta_ledger database
use vanta_ledger;

// Create collections with proper validation
db.createCollection("companies", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["name", "registration_number"],
            properties: {
                name: { bsonType: "string" },
                registration_number: { bsonType: "string" },
                industry: { bsonType: "string" },
                status: { bsonType: "string" }
            }
        }
    }
});

db.createCollection("documents", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["filename", "file_path"],
            properties: {
                filename: { bsonType: "string" },
                file_path: { bsonType: "string" },
                document_type: { bsonType: "string" },
                company_id: { bsonType: "number" }
            }
        }
    }
});

db.createCollection("financial_extractions");
db.createCollection("document_analyses");

// Create indexes for performance
db.companies.createIndex({ "name": 1 });
db.companies.createIndex({ "registration_number": 1 }, { unique: true });
db.companies.createIndex({ "status": 1 });

db.documents.createIndex({ "company_id": 1 });
db.documents.createIndex({ "project_id": 1 });
db.documents.createIndex({ "document_type": 1 });
db.documents.createIndex({ "upload_date": -1 });
db.documents.createIndex({ "postgres_id": 1 }, { unique: true });

// Text search index for OCR content
db.documents.createIndex({ "ai_analysis.ocr_text": "text" });

print("MongoDB database initialized successfully for Vanta Ledger");
