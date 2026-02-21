import mimetypes
from supabase_client import get_supabase_client

class UploadService:
    BUCKET_NAME = 'complaint-files'

    @staticmethod
    def upload_file(file, path):
        """Uploads a file to Supabase Storage and returns the public URL."""
        supabase = get_supabase_client()
        content_type = mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        file_bytes = file.read()
        
        # Upload
        # Note: If file exists, this might error. We might want to use upsert=True if replacing, 
        # or rely on unique paths.
        res = supabase.storage.from_(UploadService.BUCKET_NAME).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": content_type, "upsert": "true"} 
        )
        
        # Get Public URL
        public_url = supabase.storage.from_(UploadService.BUCKET_NAME).get_public_url(path)
        return public_url
