
import unittest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..src.vanta_ledger.models.company import Company, Base

class TestCompanyModel(unittest.TestCase):

    def setUp(self):
        """Set up a temporary in-memory database for testing."""
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        """Tear down the database session."""
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_company(self):
        """Test creating a new company."""
        company_data = {
            "name": "Test Corp",
            "registration_number": "TC12345",
            "industry": "Technology",
            "company_type": "business_partner",
        }
        company = Company(**company_data)
        self.session.add(company)
        self.session.commit()

        retrieved_company = self.session.query(Company).filter_by(name="Test Corp").first()
        self.assertIsNotNone(retrieved_company)
        self.assertEqual(retrieved_company.name, "Test Corp")
        self.assertEqual(retrieved_company.registration_number, "TC12345")

    def test_address_methods(self):
        """Test the address getter and setter methods."""
        company = Company(name="Address Test", registration_number="AT54321")
        address_data = {"street": "123 Main St", "city": "Testville"}
        company.set_address(address_data)
        self.session.add(company)
        self.session.commit()

        retrieved_company = self.session.query(Company).filter_by(name="Address Test").first()
        self.assertEqual(retrieved_company.get_address(), address_data)

    def test_to_dict_method(self):
        """Test the to_dict method."""
        company = Company(
            name="Dict Test",
            registration_number="DT67890",
            industry="Finance"
        )
        address_data = {"street": "456 Market St", "city": "Financeville"}
        company.set_address(address_data)
        self.session.add(company)
        self.session.commit()

        company_dict = company.to_dict()

        self.assertEqual(company_dict['name'], "Dict Test")
        self.assertEqual(company_dict['address'], address_data)
        self.assertIn('created_at', company_dict)
        self.assertIn('updated_at', company_dict)

if __name__ == '__main__':
    unittest.main()
