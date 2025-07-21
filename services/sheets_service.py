"""
Google Sheets API service for managing job application data.
"""

import logging
from typing import List, Optional, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from models.job_application import JobApplication, JobStatus
from utils.auth import GoogleAuthenticator
from config.settings import settings

logger = logging.getLogger(__name__)

class SheetsService:
    """Service for interacting with Google Sheets API."""
    
    def __init__(self):
        self.service = None
        self.credentials = None
        self.spreadsheet_id = settings.SPREADSHEET_ID
        self.worksheet_name = settings.WORKSHEET_NAME
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize Google Sheets API service."""
        try:
            self.credentials = GoogleAuthenticator.get_sheets_credentials(
                credentials_file=settings.SHEETS_CREDENTIALS_FILE,
                scopes=settings.SHEETS_SCOPES
            )
            
            if self.credentials:
                self.service = build('sheets', 'v4', credentials=self.credentials)
                logger.info("Google Sheets service initialized successfully")
                self._ensure_headers_exist()
            else:
                logger.error("Failed to get Google Sheets credentials")
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {e}")
    
    def _ensure_headers_exist(self) -> None:
        """Ensure the worksheet has proper headers."""
        try:
            # Check if headers exist
            range_name = f"{self.worksheet_name}!A1:H1"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # If no headers or incorrect headers, add them
            expected_headers = [
                "Date Applied", "Company", "Position", "Status", 
                "Email Date", "Notes", "Email Subject", "Email ID"
            ]
            
            if not values or values[0] != expected_headers:
                logger.info("Adding/updating headers in Google Sheet")
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body={'values': [expected_headers]}
                ).execute()
                
        except HttpError as e:
            logger.error(f"Error ensuring headers exist: {e}")
        except Exception as e:
            logger.error(f"Unexpected error with headers: {e}")
    
    def add_job_application(self, job_app: JobApplication) -> bool:
        """
        Add a new job application to the sheet.
        
        Args:
            job_app: JobApplication object to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Sheets service not initialized")
            return False
        
        try:
            # Check if application already exists
            existing_app = self.find_job_application(job_app.company, job_app.position)
            if existing_app:
                logger.info(f"Job application already exists for {job_app.company} - {job_app.position}")
                return self.update_job_application(job_app)
            
            # Find next empty row
            range_name = f"{self.worksheet_name}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            next_row = len(values) + 1
            
            # Add the job application
            range_name = f"{self.worksheet_name}!A{next_row}:H{next_row}"
            body = {'values': [job_app.to_sheets_row()]}
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"Added job application: {job_app.company} - {job_app.position}")
            return True
            
        except HttpError as e:
            logger.error(f"Error adding job application: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error adding job application: {e}")
            return False
    
    def update_job_application(self, job_app: JobApplication) -> bool:
        """
        Update an existing job application in the sheet.
        
        Args:
            job_app: JobApplication object with updated data
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Google Sheets service not initialized")
            return False
        
        try:
            # Find the row with this application
            row_index = self._find_application_row(job_app.company, job_app.position)
            if row_index is None:
                logger.warning(f"Job application not found: {job_app.company} - {job_app.position}")
                return self.add_job_application(job_app)
            
            # Update the row
            range_name = f"{self.worksheet_name}!A{row_index}:H{row_index}"
            body = {'values': [job_app.to_sheets_row()]}
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"Updated job application: {job_app.company} - {job_app.position}")
            return True
            
        except HttpError as e:
            logger.error(f"Error updating job application: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating job application: {e}")
            return False
    
    def find_job_application(self, company: str, position: str) -> Optional[JobApplication]:
        """
        Find a job application by company and position.
        
        Args:
            company: Company name
            position: Position title
            
        Returns:
            JobApplication object or None
        """
        if not self.service:
            return None
        
        try:
            # Get all data
            range_name = f"{self.worksheet_name}!A2:H"  # Skip header row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Search for matching application
            for row in values:
                if len(row) >= 3:  # Ensure we have at least company and position
                    row_company = row[1].strip().lower() if len(row) > 1 else ""
                    row_position = row[2].strip().lower() if len(row) > 2 else ""
                    
                    if (company.lower() in row_company or row_company in company.lower()) and \
                       (position.lower() in row_position or row_position in position.lower()):
                        return JobApplication.from_sheets_row(row)
            
            return None
            
        except HttpError as e:
            logger.error(f"Error finding job application: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error finding job application: {e}")
            return None
    
    def _find_application_row(self, company: str, position: str) -> Optional[int]:
        """
        Find the row number of a specific job application.
        
        Args:
            company: Company name
            position: Position title
            
        Returns:
            Row number (1-indexed) or None
        """
        try:
            # Get all data
            range_name = f"{self.worksheet_name}!A2:H"  # Skip header row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Search for matching application
            for i, row in enumerate(values):
                if len(row) >= 3:  # Ensure we have at least company and position
                    row_company = row[1].strip().lower() if len(row) > 1 else ""
                    row_position = row[2].strip().lower() if len(row) > 2 else ""
                    
                    if (company.lower() in row_company or row_company in company.lower()) and \
                       (position.lower() in row_position or row_position in position.lower()):
                        return i + 2  # +2 because we skipped header and arrays are 0-indexed
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding application row: {e}")
            return None
    
    def get_all_applications(self) -> List[JobApplication]:
        """
        Get all job applications from the sheet.
        
        Returns:
            List of JobApplication objects
        """
        if not self.service:
            return []
        
        try:
            # Get all data
            range_name = f"{self.worksheet_name}!A2:H"  # Skip header row
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            applications = []
            
            for row in values:
                if len(row) >= 3:  # Minimum required fields
                    try:
                        app = JobApplication.from_sheets_row(row)
                        applications.append(app)
                    except Exception as e:
                        logger.warning(f"Error parsing row: {row}, error: {e}")
            
            logger.info(f"Retrieved {len(applications)} job applications")
            return applications
            
        except HttpError as e:
            logger.error(f"Error getting all applications: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting all applications: {e}")
            return []
    
    def update_status(self, company: str, position: str, status: JobStatus, notes: str = "") -> bool:
        """
        Update the status of a specific job application.
        
        Args:
            company: Company name
            position: Position title
            status: New job status
            notes: Additional notes
            
        Returns:
            True if successful, False otherwise
        """
        job_app = self.find_job_application(company, position)
        if not job_app:
            logger.warning(f"Job application not found for status update: {company} - {position}")
            return False
        
        job_app.status = status
        if notes:
            job_app.notes = notes
        
        return self.update_job_application(job_app)
