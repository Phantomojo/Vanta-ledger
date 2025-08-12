# Company Data Workflow: Progress & Next Steps

**Last updated:** $(date)

## What Has Been Done

- Extracted company names from:
  - Folder structure in `raw_docs/`
  - All OCR text files in `paperless_ocr_texts/` using a comprehensive Python script
- Cleaned, normalized, and de-duplicated company names using `scripts/clean_company_names.py`
- Output a refined list of company names in `cleaned_company_names.txt`
- Database schema is up-to-date (PostgreSQL, Alembic migrations run)

## Next Steps (Pick Up Here)

1. **Review the cleaned company names in `cleaned_company_names.txt`**
   - Optionally, manually remove any remaining false positives or edge cases
2. **Query the backend API for existing companies**
   - Compare with the cleaned list to identify missing companies
3. **Seed the backend with any missing companies**
   - Use the `/companies` API endpoint to create new company records
4. **Document-to-company matching**
   - For each document, use folder, filename, and OCR content to assign the best-matching company
   - Update the document’s `company_id` in the backend if not already set
5. **(Optional) Build/update an alias/short-form table for improved matching**

## Scripts Used
- `scripts/extract_company_names_from_ocr.py`: Extracts company-like names from OCR text files
- `scripts/clean_company_names.py`: Cleans and normalizes the extracted names

## Files of Interest
- `cleaned_company_names.txt`: The current master list of company names
- `raw_docs/`: Folder-based company names
- `paperless_ocr_texts/`: OCR text files

---
**To continue:**
- Start at step 1 above, or review this document for the latest status before resuming work. 