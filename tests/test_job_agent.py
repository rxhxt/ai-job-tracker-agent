"""
Unit tests for the Job AI Agent.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from models.job_application import JobApplication, EmailData, EmailType, JobStatus
from services.email_parser import EmailParsingService
from utils.helpers import EmailParser, DateUtils, ValidationUtils

class TestJobApplication(unittest.TestCase):
    """Test JobApplication model."""
    
    def test_to_sheets_row(self):
        """Test conversion to sheets row format."""
        app = JobApplication(
            company="Test Company",
            position="Software Engineer",
            date_applied=datetime(2023, 1, 15),
            status=JobStatus.APPLIED,
            email_date=datetime(2023, 1, 15, 10, 30),
            notes="Test application",
            email_subject="Application Confirmation",
            email_id="test123"
        )
        
        row = app.to_sheets_row()
        expected = [
            "2023-01-15",
            "Test Company",
            "Software Engineer", 
            "Applied",
            "2023-01-15 10:30",
            "Test application",
            "Application Confirmation",
            "test123"
        ]
        
        self.assertEqual(row, expected)
    
    def test_from_sheets_row(self):
        """Test creation from sheets row."""
        row = [
            "2023-01-15",
            "Test Company",
            "Software Engineer",
            "Applied",
            "2023-01-15 10:30",
            "Test application",
            "Application Confirmation",
            "test123"
        ]
        
        app = JobApplication.from_sheets_row(row)
        
        self.assertEqual(app.company, "Test Company")
        self.assertEqual(app.position, "Software Engineer")
        self.assertEqual(app.status, JobStatus.APPLIED)
        self.assertEqual(app.notes, "Test application")

class TestEmailParser(unittest.TestCase):
    """Test EmailParser utility functions."""
    
    def test_clean_email_content(self):
        """Test email content cleaning."""
        dirty_content = "<p>Hello&nbsp;there!</p><br><br>This is a test."
        clean_content = EmailParser.clean_email_content(dirty_content)
        
        self.assertNotIn('<', clean_content)
        self.assertNotIn('&nbsp;', clean_content)
        self.assertIn('Hello there!', clean_content)
    
    def test_extract_company_from_email(self):
        """Test company extraction from email."""
        sender = "noreply@techcorp.com"
        subject = "Application Confirmation"
        content = "Thank you for applying"
        
        company = EmailParser.extract_company_from_email(sender, subject, content)
        self.assertEqual(company, "Techcorp")
    
    def test_extract_position_from_content(self):
        """Test position extraction from content."""
        subject = "Application for Software Engineer position"
        content = "Thank you for applying for the Software Engineer role"
        
        position = EmailParser.extract_position_from_content(subject, content)
        self.assertIn("Software Engineer", position)

class TestDateUtils(unittest.TestCase):
    """Test DateUtils utility functions."""
    
    def test_parse_email_date(self):
        """Test email date parsing."""
        date_str = "Mon, 15 Jan 2023 10:30:00 +0000"
        parsed_date = DateUtils.parse_email_date(date_str)
        
        self.assertIsNotNone(parsed_date)
        self.assertEqual(parsed_date.day, 15)
        self.assertEqual(parsed_date.month, 1)
        self.assertEqual(parsed_date.year, 2023)
    
    def test_get_date_range(self):
        """Test date range calculation."""
        start_date, end_date = DateUtils.get_date_range(7)
        
        self.assertIsInstance(start_date, datetime)
        self.assertIsInstance(end_date, datetime)
        self.assertLess(start_date, end_date)

class TestValidationUtils(unittest.TestCase):
    """Test ValidationUtils utility functions."""
    
    def test_is_valid_email(self):
        """Test email validation."""
        self.assertTrue(ValidationUtils.is_valid_email("test@example.com"))
        self.assertTrue(ValidationUtils.is_valid_email("user.name+tag@domain.co.uk"))
        self.assertFalse(ValidationUtils.is_valid_email("invalid-email"))
        self.assertFalse(ValidationUtils.is_valid_email("@domain.com"))
        self.assertFalse(ValidationUtils.is_valid_email("user@"))
    
    def test_validate_spreadsheet_id(self):
        """Test spreadsheet ID validation."""
        valid_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        invalid_id = "short"
        
        self.assertTrue(ValidationUtils.validate_spreadsheet_id(valid_id))
        self.assertFalse(ValidationUtils.validate_spreadsheet_id(invalid_id))
        self.assertFalse(ValidationUtils.validate_spreadsheet_id(""))

class TestEmailParsingService(unittest.TestCase):
    """Test EmailParsingService."""
    
    def setUp(self):
        """Set up test cases."""
        self.email_parser = EmailParsingService()
    
    @patch('services.email_parser.settings.OPENAI_API_KEY', '')
    def test_parse_with_patterns_rejection(self):
        """Test pattern-based parsing for rejection emails."""
        email_data = EmailData(
            email_id="test123",
            subject="Application Update",
            sender="hr@company.com",
            date=datetime.now(),
            body="We regret to inform you that we have decided to move forward with other candidates."
        )
        
        job_app = self.email_parser._parse_with_patterns(email_data)
        
        self.assertIsNotNone(job_app)
        self.assertEqual(email_data.email_type, EmailType.REJECTION)
    
    @patch('services.email_parser.settings.OPENAI_API_KEY', '')
    def test_parse_with_patterns_interview(self):
        """Test pattern-based parsing for interview emails."""
        email_data = EmailData(
            email_id="test123",
            subject="Interview Invitation - Software Engineer",
            sender="hr@techcorp.com",
            date=datetime.now(),
            body="We would like to schedule an interview with you for the Software Engineer position."
        )
        
        job_app = self.email_parser._parse_with_patterns(email_data)
        
        self.assertIsNotNone(job_app)
        self.assertEqual(email_data.email_type, EmailType.INTERVIEW_INVITATION)
        self.assertIn("Software Engineer", email_data.position)

if __name__ == '__main__':
    unittest.main()
