# """
# Background Tasks Module

# This module provides background task processing using Celery.
# It handles long-running operations like YouTube transcript extraction.
# """

# import os
# import logging
# import re
# from typing import Dict, Any, Optional, List

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Load environment variables
# from dotenv import load_dotenv
# load_dotenv()

# # Initialize Celery
# try:
#     from celery import Celery
    
#     # Create Celery app
#     celery_broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
#     celery_result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
#     celery_app = Celery('azure_ai_mega_toolkit',
#                    broker=celery_broker_url,
#                    backend=celery_result_backend)
    
#     # Configure Celery
#     celery_app.conf.update(
#         task_serializer='json',
#         accept_content=['json'],
#         result_serializer='json',
#         timezone='UTC',
#         enable_utc=True,
#     )
    
#     CELERY_AVAILABLE = True
#     logger.info(f"Celery initialized with broker: {celery_broker_url}")
# except ImportError:
#     logger.warning("Celery not available. Tasks will run synchronously.")
#     CELERY_AVAILABLE = False
    
#     # Create dummy Celery class for compatibility
#     class DummyCelery:
#         def task(self, *args, **kwargs):
#             def decorator(func):
#                 def wrapper(*args, **kwargs):
#                     return func(*args, **kwargs)
#                 wrapper.apply = lambda args=None, kwargs=None: DummyAsyncResult(func(*args or [], **(kwargs or {})))
#                 return wrapper
#             return decorator
    
#     class DummyAsyncResult:
#         def __init__(self, result):
#             self.result = result
        
#         def get(self):
#             return self.result
    
#     celery_app = DummyCelery()

# # YouTube Transcript API
# try:
#     from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
#     YOUTUBE_API_AVAILABLE = True
# except ImportError:
#     logger.warning("YouTube Transcript API not available. YouTube transcript features will be disabled.")
#     YOUTUBE_API_AVAILABLE = False
    
#     # Define dummy exceptions for compatibility
#     class TranscriptsDisabled(Exception): pass
#     class NoTranscriptFound(Exception): pass
#     class VideoUnavailable(Exception): pass

# # Azure Speech SDK
# try:
#     import azure.cognitiveservices.speech as speechsdk
#     SPEECH_SDK_AVAILABLE = True
# except ImportError:
#     logger.warning("Azure Speech SDK not available. Speech features will be disabled.")
#     SPEECH_SDK_AVAILABLE = False

# def extract_video_id(youtube_url: str) -> Optional[str]:
#     """Extract YouTube video ID from URL."""
#     if not youtube_url:
#         return None
    
#     # Common YouTube URL patterns
#     patterns = [
#         r'(?:v=|\/videos\/|embed\/|youtu.be\/|\/v\/|\/e\/|watch\?v=|&v=)([^#\&\?\n<>\'\"]*)',
#         r'(?:youtu.be\/)([^#\&\?\n<>\'\"]*)'
#     ]
    
#     for pattern in patterns:
#         match = re.search(pattern, youtube_url)
#         if match:
#             return match.group(1)
    
#     return None

# @celery_app.task(name='background_tasks.youtube_transcript')
# def youtube_transcript(video_url: str) -> Dict[str, Any]:
#     """
#     Celery task to fetch YouTube video transcript.
#     """
#     logger.info(f"Task youtube_transcript started for URL: {video_url}")
    
#     if not YOUTUBE_API_AVAILABLE:
#         logger.error("YouTube Transcript API not available.")
#         return {"error": "YouTube transcript service is not available.", "status": "error", "text": ""}
    
#     try:
#         video_id = extract_video_id(video_url)
#         if not video_id:
#             logger.warning(f"Could not extract video ID from URL: {video_url}")
#             return {"error": "Invalid YouTube URL format. Could not extract video ID.", "status": "error", "text": ""}
        
#         logger.info(f"Extracted video ID: {video_id} for URL: {video_url}")

#         transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
#         transcript_data = None
#         preferred_langs = ['en', 'en-US', 'en-GB']
        
#         # Try manually created English transcripts first
#         for lang_code in preferred_langs:
#             try:
#                 transcript_data = transcript_list.find_manually_created_transcript([lang_code])
#                 logger.info(f"Found manual transcript in {lang_code} for {video_id}.")
#                 break
#             except NoTranscriptFound:
#                 continue
        
#         # If no manual English, try generated English
#         if not transcript_data:
#             for lang_code in preferred_langs:
#                 try:
#                     transcript_data = transcript_list.find_generated_transcript([lang_code])
#                     logger.info(f"Found generated transcript in {lang_code} for {video_id}.")
#                     break
#                 except NoTranscriptFound:
#                     continue
        
#         # If still no English, try any available transcript
#         if not transcript_data:
#             try:
#                 # Get the first available transcript from the list of available transcripts
#                 available_transcripts = list(transcript_list)  # Convert iterator to list to check if empty
#                 if available_transcripts:
#                     transcript_data = available_transcripts[0]
#                     logger.info(f"Found transcript in language: {transcript_data.language_code} for {video_id} (fallback).")
#                 else:  # This case means transcript_list was empty
#                     raise NoTranscriptFound("No transcripts available at all.")
#             except NoTranscriptFound:  # Catch if the list was empty or find_generated/manual failed for all
#                  logger.warning(f"No transcript available in any language for video ID: {video_id}")
#                  return {"error": "No transcript available for this video in any language.", "status": "error", "text": ""}

#         full_transcript_segments = transcript_data.fetch()
#         final_text = " ".join([item['text'] for item in full_transcript_segments])
        
#         if not final_text.strip():
#             logger.warning(f"Fetched transcript for video ID: {video_id} (lang: {transcript_data.language_code}) is empty.")
#             return {"text": "", "status": "success_empty_transcript", "language": transcript_data.language_code}

#         logger.info(f"Successfully fetched transcript for video ID: {video_id}, language: {transcript_data.language_code}, length: {len(final_text)}")
#         return {"text": final_text, "status": "success", "language": transcript_data.language_code}

#     except TranscriptsDisabled:
#         logger.warning(f"Transcripts are disabled for video: {video_url}")
#         return {"error": "Transcripts are disabled for this video.", "status": "error", "text": ""}
#     except VideoUnavailable:
#         logger.warning(f"Video is unavailable: {video_url}")
#         return {"error": "The video is unavailable.", "status": "error", "text": ""}
#     except NoTranscriptFound:  # Catch-all for NoTranscriptFound if specific searches fail
#         logger.warning(f"No transcript could be found for video: {video_url} after trying all options.")
#         return {"error": "No transcript data found for this video after trying all options.", "status": "error", "text": ""}
#     except Exception as e:
#         logger.error(f"Error extracting YouTube transcript for {video_url}: {str(e)}", exc_info=True)
#         return {"error": f"An unexpected error occurred while fetching transcript: {str(e)}", "status": "error", "text": ""}

# @celery_app.task(name='background_tasks.transcribe_audio')
# def transcribe_audio(audio_file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
#     """
#     Celery task for transcribing an audio file using Azure Speech SDK.
#     """
#     logger.info(f"Task transcribe_audio started for file: {audio_file_path}, language: {language}")
    
#     if not SPEECH_SDK_AVAILABLE:
#         logger.error("transcribe_audio task called, but Azure Speech SDK is not available.")
#         return {"error": "Speech SDK not available in the task worker environment.", "status": "error"}

#     try:
#         # Retrieve speech key and region from environment variables,
#         # as this task runs in a separate Celery worker process.
#         speech_key = os.environ.get('SPEECH_SUBSCRIPTION_KEY')
#         speech_region = os.environ.get('SPEECH_REGION')

#         if not speech_key or not speech_region:
#             logger.error("Speech key or region not configured in Celery worker environment.")
#             return {"error": "Speech service credentials not configured for transcription task.", "status": "error"}

#         speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
#         if language:
#             speech_config.speech_recognition_language = language
        
#         audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
#         speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
#         logger.info(f"Starting speech recognition for {audio_file_path}...")
#         result = speech_recognizer.recognize_once_async().get()
#         logger.info(f"Speech recognition result reason: {result.reason}")
            
#         if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#             logger.info(f"Successfully transcribed audio from {audio_file_path}, text length: {len(result.text)}")
#             return {"text": result.text, "status": "success"}
#         elif result.reason == speechsdk.ResultReason.NoMatch:
#             logger.info(f"No speech could be recognized in {audio_file_path}.")
#             return {"error": "No speech could be recognized.", "status": "no_match", "text": ""}
#         elif result.reason == speechsdk.ResultReason.Canceled:
#             cancellation_details = result.cancellation_details
#             logger.error(f"Speech recognition canceled for {audio_file_path}: {cancellation_details.reason}, Details: {cancellation_details.error_details}")
#             return {"error": f"Speech recognition canceled: {cancellation_details.reason}. Details: {cancellation_details.error_details}", "status": "canceled", "text": ""}
#         else:
#             logger.warning(f"Unknown speech recognition result for {audio_file_path}: {result.reason}")
#             return {"error": f"Unknown speech recognition result: {result.reason}", "status": "unknown", "text": ""}
                
#     except AttributeError as ae:
#         logger.error(f"Audio transcription AttributeError: {str(ae)}. This might indicate an issue with SpeechConfig initialization or SDK access.", exc_info=True)
#         return {"error": f"Audio transcription configuration error: {str(ae)}", "status": "error"}
#     except Exception as e:
#         logger.error(f"Audio transcription error for {audio_file_path}: {str(e)}", exc_info=True)
#         return {"error": f"Audio transcription failed: {str(e)}", "status": "error"}
# This MUST be one of the VERY FIRST lines, before any other imports that might involve I/O or threading
import eventlet
eventlet.monkey_patch()

"""
Background Tasks Module

This module provides background task processing using Celery.
It handles long-running operations like YouTube transcript extraction and audio transcription.
Eventlet monkey patching is applied for compatibility with Celery's eventlet pool.
"""

import os
import logging
import re
from typing import Dict, Any, Optional, List

# Configure logging (ensure it's configured after monkey_patch if it does I/O)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Configured in app.py
logger = logging.getLogger(__name__)

# Load environment variables (after monkey_patch)
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env') # More robust path to .env
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    logger.info(f".env file loaded by background_tasks from {dotenv_path}")
else:
    logger.info(".env file not found by background_tasks, relying on environment.")


# Initialize Celery
try:
    from celery import Celery
    
    celery_broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    celery_result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # The name 'azure_ai_mega_toolkit' should ideally match the main app's name or a project-wide name.
    # If your main Flask app instance in app.py is named 'app', Celery often uses 'app.celery'.
    # Using a unique name like 'background_tasks_worker' can also be clear.
    celery_app = Celery('background_tasks_worker', # Changed for clarity, ensure it's consistent if imported elsewhere
                       broker=celery_broker_url,
                       backend=celery_result_backend,
                       include=['background_tasks']) # Ensure tasks in this module are discovered

    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],  # application/json is also common
        result_serializer='json',
        timezone=os.environ.get('TZ', 'UTC'), # Use system TZ or default to UTC
        enable_utc=True, # Recommended for timezone handling
        # Optional: Improve task state persistence
        # task_track_started=True,
        # result_extended=True,
    )
    
    CELERY_AVAILABLE = True
    logger.info(f"Celery initialized for 'background_tasks_worker' with broker: {celery_broker_url}")

except ImportError:
    logger.warning("Celery library not found. Tasks will run synchronously as dummy tasks.")
    CELERY_AVAILABLE = False
    
    # Dummy Celery class for environments where Celery is not installed/needed (e.g., simple local dev)
    class DummyCelery:
        def task(self, *args_decorator, **kwargs_decorator):
            def decorator(func):
                def wrapper(*args_task, **kwargs_task):
                    logger.info(f"Running dummy task: {func.__name__} with args {args_task} and kwargs {kwargs_task}")
                    return func(*args_task, **kwargs_task)
                
                # Mock the .apply_async() and .delay() methods for compatibility
                def apply_async(args=None, kwargs=None, **options):
                    logger.info(f"Calling dummy task {func.__name__}.apply_async (runs synchronously)")
                    result = func(*(args or ()), **(kwargs or {}))
                    return DummyAsyncResult(result)
                
                wrapper.apply_async = apply_async
                wrapper.delay = lambda *args, **kwargs: apply_async(args=args, kwargs=kwargs)
                wrapper.apply = lambda args=None, kwargs=None: DummyAsyncResult(func(*(args or ()), **(kwargs or {})))


                return wrapper
            return decorator

    class DummyAsyncResult:
        def __init__(self, result_value):
            self.result = result_value
            self.status = 'SUCCESS' # Mock status
        
        def get(self, timeout=None): # Add timeout for compatibility
            return self.result
        
        def successful(self): return True
        def failed(self): return False
        def ready(self): return True


    celery_app = DummyCelery()

# YouTube Transcript API
try:
    from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
    YOUTUBE_API_AVAILABLE = True
    logger.info("youtube_transcript_api imported successfully.")
except ImportError:
    logger.warning("youtube_transcript_api not available. YouTube transcript features will be disabled.")
    YOUTUBE_API_AVAILABLE = False
    class TranscriptsDisabled(Exception): pass
    class NoTranscriptFound(Exception): pass
    class VideoUnavailable(Exception): pass

# Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
    SPEECH_SDK_AVAILABLE = True
    logger.info("Azure Speech SDK (speechsdk) imported successfully.")
except ImportError:
    logger.warning("Azure Speech SDK (speechsdk) not available. Speech features will be disabled.")
    SPEECH_SDK_AVAILABLE = False
    speechsdk = None # Define for type hinting

def extract_video_id(youtube_url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats."""
    if not youtube_url: return None
    
    # Regex patterns to capture video ID from different YouTube URL formats
    # Order matters: more specific patterns first if ambiguity exists.
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/(?:watch\?v=|v\/|embed\/|shorts\/|live\/|playlist\?list=PL[^&]+&v=)([^#\&\?\s<>\'\"]+)', # Covers watch, v, embed, shorts, live, and v parameter in playlist
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^#\&\?\s<>\'\"]+)', # Covers youtu.be short links
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/attribution_link\?a=[^&]+&u=%2Fwatch%3Fv%3D([^%&]+)', # Attribution links
        r'(?:https?:\/\/)?(?:www\.)?googleusercontent\.com\/youtube_content\/v0\/([A-Za-z0-9_-]{11})' # Google user content links
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match and len(match.group(1)) == 11: # Standard YouTube ID length is 11
            return match.group(1)
    
    logger.warning(f"Could not extract a valid 11-character video ID from URL: {youtube_url}")
    return None # Fallback if no pattern matches or ID is not 11 chars

@celery_app.task(name='background_tasks.youtube_transcript', bind=True, max_retries=3, default_retry_delay=60)
def youtube_transcript(self, video_url: str) -> Dict[str, Any]:
    """
    Celery task to fetch YouTube video transcript.
    Retries on common transient errors from youtube_transcript_api.
    """
    logger.info(f"Task youtube_transcript (ID: {self.request.id}) started for URL: {video_url}")
    
    if not YOUTUBE_API_AVAILABLE:
        logger.error("YouTube Transcript API not available in Celery worker.")
        return {"error": "YouTube transcript service is not available in worker.", "status": "error_config", "text": "", "language": None}
    
    video_id = extract_video_id(video_url)
    if not video_id:
        logger.warning(f"Could not extract video ID from URL: {video_url} for task {self.request.id}")
        return {"error": "Invalid YouTube URL format. Could not extract video ID.", "status": "error_invalid_url", "text": "", "language": None}
    
    logger.info(f"Extracted video ID: {video_id} for URL: {video_url} (Task ID: {self.request.id})")

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        transcript_data = None
        # Prioritize manually created English transcripts, then generated English, then any other.
        preferred_langs_manual = ['en', 'en-US', 'en-GB']
        preferred_langs_generated = ['en', 'en-US', 'en-GB'] 

        for lang_code in preferred_langs_manual:
            try:
                transcript_data = transcript_list.find_manually_created_transcript([lang_code])
                logger.info(f"Found manual transcript in '{lang_code}' for video ID: {video_id}.")
                break
            except NoTranscriptFound: continue
        
        if not transcript_data:
            for lang_code in preferred_langs_generated:
                try:
                    transcript_data = transcript_list.find_generated_transcript([lang_code])
                    logger.info(f"Found generated transcript in '{lang_code}' for video ID: {video_id}.")
                    break
                except NoTranscriptFound: continue
        
        if not transcript_data: # Fallback to any available transcript
            available_transcripts = list(transcript_list) 
            if available_transcripts:
                # Heuristic: prefer shorter language codes (e.g., 'de' over 'de-DE') if multiple are available
                # Or just take the first one.
                available_transcripts.sort(key=lambda t: len(t.language_code))
                transcript_data = available_transcripts[0]
                logger.info(f"Found transcript in language: '{transcript_data.language_code}' for video ID: {video_id} (fallback).")
            else:
                raise NoTranscriptFound(f"No transcripts available at all for video ID: {video_id}")

        full_transcript_segments = transcript_data.fetch()
        final_text = " ".join([item['text'] for item in full_transcript_segments if 'text' in item])
        
        current_language = transcript_data.language_code

        if not final_text.strip():
            logger.warning(f"Fetched transcript for video ID: {video_id} (lang: {current_language}) is empty.")
            return {"text": "", "status": "success_empty_transcript", "language": current_language}

        logger.info(f"Successfully fetched transcript for video ID: {video_id}, lang: {current_language}, length: {len(final_text)}")
        return {"text": final_text, "status": "success", "language": current_language}

    except (TranscriptsDisabled, VideoUnavailable, NoTranscriptFound) as e:
        # These are specific, often non-retryable errors from the API for a given video.
        error_type_map = {
            TranscriptsDisabled: ("Transcripts are disabled for this video.", "error_transcripts_disabled"),
            VideoUnavailable: ("The video is unavailable or private.", "error_video_unavailable"),
            NoTranscriptFound: ("No transcript data found for this video after trying all options.", "error_no_transcript_found")
        }
        error_message, error_status = error_type_map.get(type(e), (str(e), "error_youtube_api"))
        logger.warning(f"{error_message} (Video URL: {video_url}, Task ID: {self.request.id}) - Error: {str(e)}")
        return {"error": error_message, "status": error_status, "text": "", "language": None}
    except Exception as e:
        # Catch other potential errors (network issues, API changes, etc.)
        logger.error(f"Error extracting YouTube transcript for {video_url} (Task ID: {self.request.id}): {str(e)}", exc_info=True)
        try:
            # Retry for generic exceptions which might be transient (e.g., network issues)
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for YouTube transcript task {self.request.id} for URL {video_url}.")
            return {"error": f"An unexpected error occurred after retries: {str(e)}", "status": "error_max_retries", "text": "", "language": None}


@celery_app.task(name='background_tasks.transcribe_audio', bind=True, max_retries=3, default_retry_delay=30)
def transcribe_audio(self, audio_file_path: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Celery task for transcribing an audio file using Azure Speech SDK.
    Retries on common transient errors.
    """
    logger.info(f"Task transcribe_audio (ID: {self.request.id}) started for file: {audio_file_path}, language: {language}")
    
    if not SPEECH_SDK_AVAILABLE or not speechsdk: # Check speechsdk itself
        logger.error("transcribe_audio task called, but Azure Speech SDK is not available in Celery worker.")
        return {"error": "Speech SDK not available in the task worker environment.", "status": "error_config", "text": ""}

    try:
        speech_key = os.environ.get('SPEECH_SUBSCRIPTION_KEY')
        speech_region = os.environ.get('SPEECH_REGION')

        if not speech_key or not speech_region:
            logger.error("Speech key or region not configured in Celery worker environment.")
            return {"error": "Speech service credentials not configured for transcription task.", "status": "error_config", "text": ""}

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        if language:
            speech_config.speech_recognition_language = language
        
        # Optional: Enable detailed logging from Speech SDK for debugging
        # speech_config.set_property(speechsdk.PropertyId.Speech_LogFilename, f"/tmp/speech_sdk_log_{self.request.id}.txt")


        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        # Using SpeechRecognizer for single utterance or shorter audio.
        # For longer audio, consider ConversationTranscriber or Batch Transcription.
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        logger.info(f"Starting speech recognition for {audio_file_path} (Task ID: {self.request.id})...")
        
        # recognize_once_async() is suitable for shorter audio.
        # For very long audio, you might need to handle continuous recognition
        # or use Azure Batch Transcription service.
        result = speech_recognizer.recognize_once_async().get() # Blocking call to get result
        
        logger.info(f"Speech recognition result reason for task {self.request.id}: {result.reason}")
            
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logger.info(f"Successfully transcribed audio from {audio_file_path} (Task ID: {self.request.id}), text length: {len(result.text)}")
            return {"text": result.text, "status": "success"}
        elif result.reason == speechsdk.ResultReason.NoMatch:
            logger.info(f"No speech could be recognized in {audio_file_path} (Task ID: {self.request.id}).")
            return {"error": "No speech could be recognized.", "status": "no_match", "text": ""}
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"Speech recognition canceled for {audio_file_path} (Task ID: {self.request.id}): {cancellation_details.reason}, Details: {cancellation_details.error_details}")
            # Some cancellation reasons might be retryable, e.g., connection issues.
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                 # ErrorCode 0x8 (ConnectionFailure) or 0x5 (ServiceTimeout) could be retryable
                if cancellation_details.error_code in [speechsdk.CancellationErrorCode.ConnectionFailure, speechsdk.CancellationErrorCode.ServiceTimeout]:
                    logger.info(f"Retrying task {self.request.id} due to cancellation: {cancellation_details.reason}")
                    raise self.retry(exc=Exception(f"Speech recognition canceled: {cancellation_details.reason}"))
            return {"error": f"Speech recognition canceled: {cancellation_details.reason}. Details: {cancellation_details.error_details}", "status": "canceled", "text": ""}
        else: # Should not happen with recognize_once_async if it completes.
            logger.warning(f"Unknown speech recognition result for {audio_file_path} (Task ID: {self.request.id}): {result.reason}")
            return {"error": f"Unknown speech recognition result: {result.reason}", "status": "unknown", "text": ""}
                
    except AttributeError as ae: # e.g. if speechsdk was None
        logger.error(f"Audio transcription AttributeError (Task ID: {self.request.id}): {str(ae)}. SDK access issue?", exc_info=True)
        return {"error": f"Audio transcription configuration error: {str(ae)}", "status": "error_attribute", "text": ""}
    except Exception as e:
        logger.error(f"Audio transcription error for {audio_file_path} (Task ID: {self.request.id}): {str(e)}", exc_info=True)
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for audio transcription task {self.request.id} for file {audio_file_path}.")
            return {"error": f"Audio transcription failed after retries: {str(e)}", "status": "error_max_retries", "text": ""}

# To run a Celery worker for these tasks (example):
# celery -A background_tasks.celery_app worker -l info -P eventlet
# Ensure Redis (or your chosen broker) is running.
# Ensure this file is in Python's path or the CWD when starting the worker.
