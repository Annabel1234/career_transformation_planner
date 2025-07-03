# Career Transformation Planner

A Django-based web application for career planning and transformation, featuring comprehensive user data management and file upload capabilities.

## Features

- **User Profile Management**: Complete career profiles with skills, education, experience, and goals
- **File Upload & Import**: Support for CSV, Excel, and JSON file imports
- **REST API**: Full API for programmatic access
- **Admin Interface**: Comprehensive Django admin for data management
- **Bulk Operations**: Import large datasets efficiently
- **Response Storage**: Automatic saving of API responses to local download folder
- **Data Export**: Export user data in JSON, CSV, and Excel formats

## Where You Can Upload User Information

### 1. **Web API Endpoints**

#### File Upload API
```
POST /api/imports/upload_file/
```
Upload files for data import with automatic processing.

#### Bulk Import API
```
POST /api/upload/bulk_import/
```
Direct bulk import with options for overwriting existing data.

### 2. **Django Admin Interface**
Access at `/admin/` for manual data entry and file uploads.

### 3. **Supported File Formats**

#### CSV Files
- **Skills**: `skill_name,category,proficiency_level,years_of_experience`
- **Education**: `institution,degree,field_of_study,start_date,end_date,gpa,description`
- **Experience**: `company,position,start_date,end_date,is_current,description,achievements`
- **Goals**: `title,description,target_date,priority,status`
- **Profile**: `phone,current_position,years_of_experience,current_salary,desired_salary,location,linkedin_url,github_url,portfolio_url`

#### Excel Files (.xlsx, .xls)
Same column structure as CSV files.

#### JSON Files
Array of objects with the same field structure.

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd career_transformation_planner
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

## Usage Examples

### Upload Skills via API

```bash
curl -X POST http://localhost:8000/api/imports/upload_file/ \
  -H "Authorization: Basic <base64-encoded-credentials>" \
  -F "file=@example_data/skills_example.csv" \
  -F "import_type=skills" \
  -F "file_type=csv"
```

### Upload Education via Python

```python
import requests

url = "http://localhost:8000/api/imports/upload_file/"
files = {'file': open('example_data/education_example.csv', 'rb')}
data = {
    'import_type': 'education',
    'file_type': 'csv'
}
response = requests.post(url, files=files, data=data, auth=('username', 'password'))
result = response.json()
print(f"Upload successful: {result['message']}")
print(f"Response saved to: {result['file_path']}")
```

### Bulk Import with Options

```python
import requests

url = "http://localhost:8000/api/upload/bulk_import/"
files = {'file': open('example_data/experience_example.csv', 'rb')}
data = {
    'import_type': 'experience',
    'overwrite_existing': True,
    'skip_errors': True
}
response = requests.post(url, files=files, data=data, auth=('username', 'password'))
result = response.json()
print(f"Bulk import completed: {result['processed']} records")
print(f"Response saved to: {result['file_path']}")
```

### Export User Data

```python
import requests

# Export all user data
url = "http://localhost:8000/api/upload/export_all/"
params = {'format': 'json'}  # or 'csv', 'excel'
response = requests.get(url, params=params, auth=('username', 'password'))
result = response.json()
print(f"Export completed: {result['message']}")
print(f"File saved to: {result['file_path']}")
print(f"Data summary: {result['data_summary']}")
```

## API Endpoints

### User Data Management
- `GET/POST /api/profiles/` - User profiles
- `GET/POST /api/skills/` - Available skills
- `GET/POST /api/user-skills/` - User's skills
- `GET/POST /api/education/` - Education history
- `GET/POST /api/experience/` - Work experience
- `GET/POST /api/goals/` - Career goals

### File Upload & Import
- `POST /api/imports/upload_file/` - Upload and process files
- `POST /api/upload/bulk_import/` - Bulk import with options
- `GET /api/imports/` - View import history

### Data Export & Response Storage
- `GET /api/profiles/export/` - Export user profile data
- `GET /api/user-skills/export/` - Export user skills
- `GET /api/education/export/` - Export education history
- `GET /api/experience/export/` - Export work experience
- `GET /api/goals/export/` - Export career goals
- `GET /api/imports/export/` - Export import history
- `GET /api/upload/export_all/` - Export all user data

## File Format Examples

### Skills CSV Example
```csv
skill_name,category,proficiency_level,years_of_experience
Python,language,4,3
JavaScript,language,3,2
React,framework,3,2
```

### Education CSV Example
```csv
institution,degree,field_of_study,start_date,end_date,gpa,description
University of Technology,BS,Computer Science,2018-09-01,2022-05-15,3.8,Studied software engineering
```

### Experience CSV Example
```csv
company,position,start_date,end_date,is_current,description,achievements
Tech Startup,Software Engineer,2022-06-01,2023-12-31,False,Developed web applications,Launched 3 features
```

## Admin Interface

Access the admin interface at `http://localhost:8000/admin/` to:

- View and edit all user data
- Monitor import history and results
- Manage skills and categories
- Bulk edit user information
- View import error logs

## Data Models

### UserProfile
Extended user information including career details, salary expectations, and social links.

### Skill & UserSkill
Skills catalog and user proficiency levels (1-5 scale).

### Education
Academic background with institutions, degrees, and dates.

### WorkExperience
Employment history with companies, positions, and achievements.

### CareerGoal
Career objectives with priorities and target dates.

### DataImport
Tracks all file imports with processing results and error logs.

## Response Storage

All API responses are automatically saved to a local `downloads/` folder:

### Automatic Storage
- **Success Responses**: All successful API calls save responses locally
- **Error Responses**: Error details are captured and stored
- **File Formats**: JSON, CSV, and Excel exports are saved
- **Timestamped Files**: Each file includes timestamp for tracking

### File Naming Convention
- `user_profile_username_YYYYMMDD_HHMMSS.json`
- `user_skills_username_YYYYMMDD_HHMMSS.csv`
- `import_response_username_id_YYYYMMDD_HHMMSS.json`
- `bulk_import_response_username_type_YYYYMMDD_HHMMSS.json`

### Use Cases
- **Local Backup**: Keep copies of all API interactions
- **Frontend Integration**: Use stored responses for frontend development
- **Data Analysis**: Analyze API usage patterns
- **Debugging**: Review error logs and response history

## Error Handling

The system provides comprehensive error handling:

- **Validation Errors**: Field-level validation with detailed messages
- **Processing Errors**: Row-by-row error tracking for bulk imports
- **File Format Errors**: Automatic detection of unsupported formats
- **Duplicate Handling**: Options to overwrite or skip existing records
- **Error Logging**: All errors are saved to local files for review

## Security Features

- **Authentication Required**: All endpoints require user authentication
- **File Type Validation**: Only allowed file types are processed
- **Data Isolation**: Users can only access their own data
- **CSRF Protection**: Built-in Django CSRF protection

## Development

### Adding New Import Types

1. Add new choices to the `DataImport.import_type` field
2. Implement processing methods in `DataImportViewSet`
3. Update serializers and admin interface
4. Add example files and documentation

### Customizing File Formats

Modify the import methods in `views.py` to handle different column names or data structures.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 