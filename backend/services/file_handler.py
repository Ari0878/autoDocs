import os
import zipfile
import tarfile
import subprocess
from pathlib import Path
from werkzeug.utils import secure_filename

UPLOAD_BASE = Path('./uploads')
ALLOWED_EXTENSIONS = {'zip', 'tar', 'gz', 'py', 'js', 'ts', 'java', 'php', 'go', 'rb'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clone_github_repo(github_url: str, project_id: str) -> str:
    """Clone a GitHub repository and return the project path."""
    UPLOAD_BASE.mkdir(parents=True, exist_ok=True)
    
    project_dir = UPLOAD_BASE / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove .git extension if present
    repo_name = github_url.rstrip('/').split('/')[-1].replace('.git', '')
    clone_path = project_dir / repo_name
    
    try:
        # Clone the repository
        subprocess.run(
            ['git', 'clone', github_url, str(clone_path)],
            check=True,
            capture_output=True,
            text=True
        )
        return str(clone_path)
    except subprocess.CalledProcessError as e:
        print(f"[Git Clone Error] {e.stderr}")
        raise Exception(f"Failed to clone repository: {e.stderr}")

def save_uploaded_project(file, project_id: str) -> str:
    """Save uploaded file and extract if archive. Returns project folder path."""
    UPLOAD_BASE.mkdir(parents=True, exist_ok=True)
    
    project_dir = UPLOAD_BASE / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    
    filename = secure_filename(file.filename)
    file_path = project_dir / filename
    file.save(str(file_path))
    
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    if ext == 'zip':
        with zipfile.ZipFile(file_path, 'r') as z:
            z.extractall(project_dir / 'src')
        # Remove the zip file after extraction
        file_path.unlink()
        return str(project_dir / 'src')
    elif ext in ('tar', 'gz'):
        with tarfile.open(file_path, 'r:*') as t:
            t.extractall(project_dir / 'src')
        # Remove the tar file after extraction
        file_path.unlink()
        return str(project_dir / 'src')
    else:
        return str(project_dir)
