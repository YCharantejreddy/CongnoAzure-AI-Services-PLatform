# # """
# # Azure AI Service Integration Module

# # This module provides initialization and utility functions for Azure AI services.
# # It handles credential management, client initialization, and error handling.
# # """

# # import os
# # import logging
# # import io  # Required for BytesIO
# # from typing import Optional, Dict, List, Any, Tuple, Union

# # # Configure logging
# # logger = logging.getLogger(__name__)

# # # Azure Translator Service
# # try:
# #     from azure.ai.translation.text import TextTranslationClient
# #     from azure.core.credentials import AzureKeyCredential as AzureKeyCredentialTranslation  # Alias to avoid conflict
# #     TRANSLATOR_AVAILABLE = True
# #     logger.info("Azure Translator SDK imported successfully")
# # except ImportError as e:
# #     TRANSLATOR_AVAILABLE = False
# #     logger.warning(f"Azure Translator SDK not available: {str(e)}. Translation features will be disabled.")

# # # Azure Language Service
# # try:
# #     from azure.core.credentials import AzureKeyCredential  # Standard AzureKeyCredential
# #     from azure.ai.textanalytics import TextAnalyticsClient
# #     LANGUAGE_AVAILABLE = True
# # except ImportError as e:
# #     LANGUAGE_AVAILABLE = False
# #     logger.warning(f"Azure Language SDK not available: {str(e)}. Text analytics features will be disabled.")

# # # Azure Speech Service
# # try:
# #     import azure.cognitiveservices.speech as speechsdk
# #     SPEECH_AVAILABLE = True
# # except ImportError as e:
# #     SPEECH_AVAILABLE = False
# #     logger.warning(f"Azure Speech SDK not available: {str(e)}. Speech features will be disabled.")

# # # Azure Computer Vision Service
# # try:
# #     from azure.cognitiveservices.vision.computervision import ComputerVisionClient
# #     from msrest.authentication import CognitiveServicesCredentials  # Used by older Vision SDK
# #     VISION_AVAILABLE = True
# # except ImportError as e:
# #     VISION_AVAILABLE = False
# #     logger.warning(f"Azure Computer Vision SDK not available: {str(e)}. Vision features will be disabled.")

# # # Define character limits for summarization services
# # # These are approximate and can vary slightly based on Azure's current limits.
# # # Refer to official Azure documentation for the most up-to-date limits.
# # ABSTRACTIVE_SUMMARY_CHAR_LIMIT = 120000  # A bit less than 125k for safety
# # EXTRACTIVE_SUMMARY_CHAR_LIMIT = 5000    # A bit less than 5120 for safety

# # class AzureServiceManager:
# #     """
# #     Manages Azure AI service clients and provides utility functions for service operations.
# #     Handles initialization, credential management, and error handling.
# #     """
    
# #     def __init__(self):
# #         """Initialize Azure service clients based on available environment variables."""
# #         self.translator_client = self._init_translator_client()
# #         self.language_client = self._init_language_client()
# #         self.speech_config = self._init_speech_config()
# #         self.vision_client = self._init_vision_client()
        
# #         self._log_initialization_status()
    
# #     def _init_translator_client(self) -> Optional[TextTranslationClient]:
# #         """Initialize Azure Translator client if credentials are available."""
# #         if not TRANSLATOR_AVAILABLE:
# #             return None
            
# #         try:
# #             key = os.environ.get('TRANSLATOR_SUBSCRIPTION_KEY')
# #             endpoint = os.environ.get('TRANSLATOR_ENDPOINT')
# #             # Region is important for the Translator service key to be valid.
# #             # The TextTranslationClient itself doesn't take region as a direct init param for key-based auth,
# #             # but the key is tied to a region.
# #             # The endpoint usually implies the region or is global.
# #             # The 401 error strongly suggests the key is invalid for the endpoint/service.
            
# #             if not all([key, endpoint]):  # Region is implicitly part of the endpoint or key's validity
# #                 logger.warning("Azure Translator key or endpoint incomplete. Translation features will be disabled.")
# #                 return None
                
# #             logger.info(f"Initializing Azure Translator client with key: {key[:5]}..., endpoint: {endpoint}")
            
# #             # The azure-ai-translation-text SDK uses AzureKeyCredential.
# #             credential = AzureKeyCredentialTranslation(key) 
            
# #             # For azure-ai-translation-text==1.0.0b1, the client is initialized with endpoint and credential.
# #             # The 'region' parameter for the client constructor was removed or changed in later SDKs/contexts.
# #             # If a specific API version or SDK behavior requires region in client, this might need adjustment.
# #             # However, the 401 is a credential/authorization issue, not typically a missing client param if endpoint is correct.
# #             return TextTranslationClient(endpoint=endpoint, credential=credential)
            
# #         except Exception as e:
# #             logger.error(f"Failed to initialize Azure Translator client: {str(e)}")
# #             return None
    
# #     def _init_language_client(self) -> Optional[TextAnalyticsClient]:
# #         """Initialize Azure Language client if credentials are available."""
# #         if not LANGUAGE_AVAILABLE:
# #             return None
            
# #         try:
# #             key = os.environ.get('LANGUAGE_SUBSCRIPTION_KEY')
# #             endpoint = os.environ.get('LANGUAGE_ENDPOINT')
            
# #             if not all([key, endpoint]):
# #                 logger.warning("Azure Language credentials incomplete. Text analytics features will be disabled.")
# #                 return None
                
# #             credential = AzureKeyCredential(key)
# #             return TextAnalyticsClient(endpoint=endpoint, credential=credential)
            
# #         except Exception as e:
# #             logger.error(f"Failed to initialize Azure Language client: {str(e)}")
# #             return None
    
# #     def _init_speech_config(self) -> Optional[speechsdk.SpeechConfig]:
# #         """Initialize Azure Speech configuration if credentials are available."""
# #         if not SPEECH_AVAILABLE:
# #             return None
            
# #         try:
# #             key = os.environ.get('SPEECH_SUBSCRIPTION_KEY')
# #             region = os.environ.get('SPEECH_REGION')
            
# #             if not all([key, region]):
# #                 logger.warning("Azure Speech credentials incomplete. Speech features will be disabled.")
# #                 return None
                
# #             return speechsdk.SpeechConfig(subscription=key, region=region)
            
# #         except Exception as e:
# #             logger.error(f"Failed to initialize Azure Speech config: {str(e)}")
# #             return None
    
# #     def _init_vision_client(self) -> Optional[ComputerVisionClient]:
# #         """Initialize Azure Computer Vision client if credentials are available."""
# #         if not VISION_AVAILABLE:
# #             return None
            
# #         try:
# #             key = os.environ.get('VISION_SUBSCRIPTION_KEY')
# #             endpoint = os.environ.get('VISION_ENDPOINT')
            
# #             if not all([key, endpoint]):
# #                 logger.warning("Azure Vision credentials incomplete. Vision features will be disabled.")
# #                 return None
                
# #             credentials = CognitiveServicesCredentials(key)  # Older SDK auth method
# #             return ComputerVisionClient(endpoint=endpoint, credentials=credentials)
            
# #         except Exception as e:
# #             logger.error(f"Failed to initialize Azure Vision client: {str(e)}")
# #             return None
    
# #     def _log_initialization_status(self):
# #         """Log the initialization status of all Azure services."""
# #         logger.info(f"Azure Translator Service: {'Available' if self.translator_client else 'Unavailable'}")
# #         logger.info(f"Azure Language Service: {'Available' if self.language_client else 'Unavailable'}")
# #         logger.info(f"Azure Speech Service: {'Available' if self.speech_config else 'Unavailable'}")
# #         logger.info(f"Azure Computer Vision Service: {'Available' if self.vision_client else 'Unavailable'}")
    
# #     def translate_text(self, text: str, target_languages: List[str], source_language: Optional[str] = None) -> Dict[str, str]:
# #         """Translate text. Handles 401 by returning error, user must fix credentials."""
# #         if not self.translator_client:
# #             return {"error": "Translation service is not available due to client initialization failure."}
        
# #         try:
# #             # The API expects a list of dictionaries, even for a single text item.
# #             input_text_elements = [{'text': text}]
            
# #             response = self.translator_client.translate(
# #                 content=input_text_elements,  # Pass as list of dicts
# #                 to=target_languages,  # SDK uses 'to' parameter
# #                 from_parameter=source_language  # SDK uses 'from_parameter'
# #             )
            
# #             translations = {}
# #             # Response is a list, one item per input_text_element
# #             if response and isinstance(response, list) and response[0].translations:
# #                 for translation_item in response[0].translations:
# #                     translations[translation_item.to] = translation_item.text
# #             else:  # Handle unexpected response structure or empty translations
# #                 logger.warning(f"Unexpected translation response structure or empty translations: {response}")
# #                 return {"error": "Translation failed or returned no results."}

# #             return translations
            
# #         except Exception as e:  # Catching AzureHttpError or similar for auth issues
# #             logger.error(f"Translation error: {str(e)}")
# #             # Check if it's an authentication error (often includes status code 401)
# #             if "401" in str(e) or "authentication" in str(e).lower() or "credential" in str(e).lower():
# #                  return {"error": f"(401) Translation authorization failed. Please check your Translator API key and endpoint in the .env file. Details: {str(e)}"}
# #             return {"error": f"Translation failed: {str(e)}"}
    
# #     def analyze_sentiment(self, text: str) -> Dict[str, Any]:
# #         if not self.language_client:
# #             return {"error": "Sentiment analysis service is not available."}
        
# #         try:
# #             # Text Analytics SDK expects a list of documents.
# #             # Each document can be a string or an object with 'id' and 'text'.
# #             documents = [text] 
# #             response = self.language_client.analyze_sentiment(documents=documents, show_opinion_mining=True)  # Added opinion mining
            
# #             result_doc = response[0]  # Assuming single document processing
# #             if result_doc.is_error:
# #                 logger.error(f"Sentiment analysis document error: {result_doc.error.message}")
# #                 return {"error": f"Sentiment analysis document error: {result_doc.error.message}"}
            
# #             result = {
# #                 "sentiment": result_doc.sentiment,
# #                 "confidence_scores": {
# #                     "positive": result_doc.confidence_scores.positive,
# #                     "neutral": result_doc.confidence_scores.neutral,
# #                     "negative": result_doc.confidence_scores.negative
# #                 },
# #                 "sentences": []
# #             }
# #             for sentence in result_doc.sentences:
# #                 sentence_data = {
# #                     "text": sentence.text,
# #                     "sentiment": sentence.sentiment,
# #                     "confidence_scores": {
# #                         "positive": sentence.confidence_scores.positive,
# #                         "neutral": sentence.confidence_scores.neutral,
# #                         "negative": sentence.confidence_scores.negative
# #                     },
# #                     "opinions": []
# #                 }
# #                 # Include opinion mining results if available
# #                 for opinion in sentence.mined_opinions:
# #                     opinion_data = {
# #                         "target_text": opinion.target.text,
# #                         "target_sentiment": opinion.target.sentiment,
# #                         "assessments": [{"text": assessment.text, "sentiment": assessment.sentiment} for assessment in opinion.assessments]
# #                     }
# #                     sentence_data["opinions"].append(opinion_data)
# #                 result["sentences"].append(sentence_data)
            
# #             return result
            
# #         except Exception as e:
# #             logger.error(f"Sentiment analysis error: {str(e)}")
# #             return {"error": f"Sentiment analysis failed: {str(e)}"}
    
# #     def extractive_summarize(self, text: str, sentence_count: int = 3) -> Dict[str, Any]:
# #         if not self.language_client:
# #             return {"error": "Summarization service is not available."}
        
# #         # Truncate text if it exceeds the service limit
# #         if len(text) > EXTRACTIVE_SUMMARY_CHAR_LIMIT:
# #             text = text[:EXTRACTIVE_SUMMARY_CHAR_LIMIT]
# #             logger.warning(f"Text for extractive summarization truncated to {EXTRACTIVE_SUMMARY_CHAR_LIMIT} characters.")

# #         try:
# #             documents = [{"id": "1", "language": "en", "text": text}]  # SDK expects list of dicts
            
# #             poller = self.language_client.begin_extract_summary(documents=documents, max_sentence_count=sentence_count)
# #             extract_summary_results = poller.result()
            
# #             result = {}
# #             for doc_result in extract_summary_results:
# #                 if doc_result.is_error:
# #                     logger.error(f"Extractive summarization document error: {doc_result.error.message}")
# #                     result["error"] = f"Extractive summary document error: {doc_result.error.message}"
# #                     break 
# #                 result["summary"] = " ".join([sentence.text for sentence in doc_result.sentences])
# #                 result["sentences"] = [sentence.text for sentence in doc_result.sentences]
# #                 break  # Assuming single document processing
            
# #             return result
            
# #         except Exception as e:
# #             logger.error(f"Extractive summarization error: {str(e)}")
# #             return {"error": f"Extractive summarization failed: {str(e)}"}
    
# #     def abstractive_summarize(self, text: str, sentence_count: Optional[int] = None) -> Dict[str, Any]:
# #         # sentence_count for abstractive summary is more of a suggestion, API might not strictly adhere.
# #         if not self.language_client:
# #             return {"error": "Summarization service is not available."}

# #         # Truncate text if it exceeds the service limit
# #         if len(text) > ABSTRACTIVE_SUMMARY_CHAR_LIMIT:
# #             text = text[:ABSTRACTIVE_SUMMARY_CHAR_LIMIT]
# #             logger.warning(f"Text for abstractive summarization truncated to {ABSTRACTIVE_SUMMARY_CHAR_LIMIT} characters.")

# #         try:
# #             documents = [{"id": "1", "language": "en", "text": text}]  # SDK expects list of dicts

# #             poller_options = {}
# #             if sentence_count is not None and sentence_count > 0:
# #                 poller_options["sentence_count"] = sentence_count
                
# #             poller = self.language_client.begin_abstract_summary(documents=documents, **poller_options)
# #             abstract_summary_results = poller.result()
            
# #             result = {}
# #             for doc_result in abstract_summary_results:
# #                 if doc_result.is_error:
# #                     logger.error(f"Abstractive summarization document error: {doc_result.error.message}")
# #                     result["error"] = f"Abstractive summary document error: {doc_result.error.message}"
# #                     break
# #                 result["summary"] = doc_result.summaries[0].text if doc_result.summaries else ""
# #                 break  # Assuming single document processing
            
# #             return result
            
# #         except Exception as e:
# #             logger.error(f"Abstractive summarization error: {str(e)}")
# #             return {"error": f"Abstractive summarization failed: {str(e)}"}
    
# #     def analyze_image(self, image_path: str) -> Dict[str, Any]:
# #         """Analyze image using Azure Computer Vision API."""
# #         if not self.vision_client:
# #             return {"error": "Vision service is not available."}
        
# #         try:
# #             # Open the image file
# #             with open(image_path, "rb") as image_file:
# #                 # Analyze the image
# #                 features = [
# #                     "Categories", "Tags", "Description", "Objects", "Adult",
# #                     "Brands", "Color", "Faces"
# #                 ]
                
# #                 response = self.vision_client.analyze_image_in_stream(
# #                     image=image_file,
# #                     visual_features=features
# #                 )
                
# #                 # Process the response into a serializable format
# #                 result = self.make_vision_result_serializable(response)
# #                 return result
                
# #         except Exception as e:
# #             logger.error(f"Image analysis error: {str(e)}")
# #             return {"error": f"Image analysis failed: {str(e)}"}
    
# #     def make_vision_result_serializable(self, vision_response) -> Dict[str, Any]:
# #         """Convert Vision API response to a JSON-serializable format."""
# #         result = {}
        
# #         # Categories
# #         if hasattr(vision_response, 'categories') and vision_response.categories:
# #             result['categories'] = [
# #                 {'name': c.name, 'score': c.score} for c in vision_response.categories
# #             ]
        
# #         # Tags
# #         if hasattr(vision_response, 'tags') and vision_response.tags:
# #             result['tags'] = [
# #                 {'name': t.name, 'confidence': t.confidence} for t in vision_response.tags
# #             ]
        
# #         # Description
# #         if hasattr(vision_response, 'description') and vision_response.description:
# #             result['description'] = {
# #                 'captions': [
# #                     {'text': c.text, 'confidence': c.confidence} 
# #                     for c in vision_response.description.captions
# #                 ],
# #                 'tags': vision_response.description.tags
# #             }
        
# #         # Objects
# #         if hasattr(vision_response, 'objects') and vision_response.objects:
# #             result['objects'] = [
# #                 {
# #                     'object': o.object_property,
# #                     'confidence': o.confidence,
# #                     'rectangle': {
# #                         'x': o.rectangle.x,
# #                         'y': o.rectangle.y,
# #                         'w': o.rectangle.w,
# #                         'h': o.rectangle.h
# #                     }
# #                 } for o in vision_response.objects
# #             ]
        
# #         # Adult content
# #         if hasattr(vision_response, 'adult') and vision_response.adult:
# #             result['adult'] = {
# #                 'is_adult_content': vision_response.adult.is_adult_content,
# #                 'is_racy_content': vision_response.adult.is_racy_content,
# #                 'adult_score': vision_response.adult.adult_score,
# #                 'racy_score': vision_response.adult.racy_score
# #             }
        
# #         # Brands
# #         if hasattr(vision_response, 'brands') and vision_response.brands:
# #             result['brands'] = [
# #                 {
# #                     'name': b.name,
# #                     'confidence': b.confidence,
# #                     'rectangle': {
# #                         'x': b.rectangle.x,
# #                         'y': b.rectangle.y,
# #                         'w': b.rectangle.w,
# #                         'h': b.rectangle.h
# #                     }
# #                 } for b in vision_response.brands
# #             ]
        
# #         # Color
# #         if hasattr(vision_response, 'color') and vision_response.color:
# #             result['color'] = {
# #                 'dominant_color_foreground': vision_response.color.dominant_color_foreground,
# #                 'dominant_color_background': vision_response.color.dominant_color_background,
# #                 'dominant_colors': vision_response.color.dominant_colors,
# #                 'accent_color': vision_response.color.accent_color,
# #                 'is_black_and_white': vision_response.color.is_black_and_white
# #             }
        
# #         # Faces
# #         if hasattr(vision_response, 'faces') and vision_response.faces:
# #             result['faces'] = [
# #                 {
# #                     'age': f.age,
# #                     'gender': f.gender,
# #                     'rectangle': {
# #                         'left': f.face_rectangle.left,
# #                         'top': f.face_rectangle.top,
# #                         'width': f.face_rectangle.width,
# #                         'height': f.face_rectangle.height
# #                     }
# #                 } for f in vision_response.faces
# #             ]
        
# #         return result
    
# #     def get_speech_token(self) -> Dict[str, Any]:
# #         """Get a token for the Speech SDK client-side authentication."""
# #         if not self.speech_config:
# #             return {"error": "Speech service is not available."}
        
# #         try:
# #             # Get the auth token from the speech config
# #             # Note: This is a simplified approach. In production, you might want to use a more secure method.
# #             auth_token = self.speech_config.get_property(speechsdk.PropertyId.SpeechServiceAuthorization_Token)
# #             region = self.speech_config.get_property(speechsdk.PropertyId.SpeechServiceConnection_Region)
            
# #             if not auth_token:
# #                 # If token is not available directly, use the subscription key
# #                 # The client will need to use the subscription key directly
# #                 subscription_key = os.environ.get('SPEECH_SUBSCRIPTION_KEY')
# #                 if subscription_key:
# #                     return {
# #                         "subscription_key": subscription_key,
# #                         "region": region
# #                     }
# #                 else:
# #                     return {"error": "Speech service credentials are not available."}
            
# #             return {
# #                 "token": auth_token,
# #                 "region": region
# #             }
            
# #         except Exception as e:
# #             logger.error(f"Error getting speech token: {str(e)}")
# #             return {"error": f"Failed to get speech token: {str(e)}"}

# # # Create a singleton instance
# # azure_services = AzureServiceManager()
# """
# Azure AI Service Integration Module

# This module provides initialization and utility functions for Azure AI services.
# It handles credential management, client initialization, and error handling.
# """

# import os
# import logging
# import io
# from typing import Optional, Dict, List, Any 

# # Configure logging
# logger = logging.getLogger(__name__)

# # Azure Translator Service
# try:
#     from azure.ai.translation.text import TextTranslationClient
#     from azure.core.credentials import AzureKeyCredential as AzureKeyCredentialTranslation
#     TRANSLATOR_AVAILABLE = True
#     logger.info("Azure Translator SDK imported successfully")
# except ImportError as e:
#     TRANSLATOR_AVAILABLE = False
#     logger.warning(f"Azure Translator SDK not available: {str(e)}. Translation features will be disabled.")

# # Azure Language Service
# try:
#     from azure.core.credentials import AzureKeyCredential
#     from azure.ai.textanalytics import TextAnalyticsClient
#     LANGUAGE_AVAILABLE = True
#     logger.info("Azure Language SDK imported successfully")
# except ImportError as e:
#     LANGUAGE_AVAILABLE = False
#     logger.warning(f"Azure Language SDK not available: {str(e)}. Text analytics features will be disabled.")

# # Azure Speech Service
# try:
#     import azure.cognitiveservices.speech as speechsdk
#     SPEECH_AVAILABLE = True
#     logger.info("Azure Speech SDK imported successfully")
# except ImportError as e:
#     SPEECH_AVAILABLE = False
#     logger.warning(f"Azure Speech SDK not available: {str(e)}. Speech features will be disabled.")

# # Azure Computer Vision Service
# try:
#     from azure.cognitiveservices.vision.computervision import ComputerVisionClient
#     from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes 
#     from msrest.authentication import CognitiveServicesCredentials
#     VISION_AVAILABLE = True
#     logger.info("Azure Computer Vision SDK imported successfully")
# except ImportError as e:
#     VISION_AVAILABLE = False
#     logger.warning(f"Azure Computer Vision SDK not available: {str(e)}. Vision features will be disabled.")

# ABSTRACTIVE_SUMMARY_CHAR_LIMIT = 120000 
# EXTRACTIVE_SUMMARY_CHAR_LIMIT = 5000    

# class AzureServiceManager:
#     def __init__(self):
#         self.translator_client = self._init_translator_client()
#         self.language_client = self._init_language_client()
#         self.speech_config = self._init_speech_config()
#         self.vision_client = self._init_vision_client()
#         self._log_initialization_status()
    
#     def _init_translator_client(self) -> Optional[TextTranslationClient]:
#         if not TRANSLATOR_AVAILABLE: return None
#         try:
#             key = os.environ.get('TRANSLATOR_SUBSCRIPTION_KEY')
#             endpoint = os.environ.get('TRANSLATOR_ENDPOINT')
#             if not all([key, endpoint]):
#                 logger.warning("Azure Translator key or endpoint incomplete. Translation features disabled.")
#                 return None
#             logger.info(f"Initializing Azure Translator client with key: {key[:5]}..., endpoint: {endpoint}")
#             credential = AzureKeyCredentialTranslation(key) 
#             return TextTranslationClient(endpoint=endpoint, credential=credential)
#         except Exception as e:
#             logger.error(f"Failed to initialize Azure Translator client: {str(e)}")
#             return None
    
#     def _init_language_client(self) -> Optional[TextAnalyticsClient]:
#         if not LANGUAGE_AVAILABLE: return None
#         try:
#             key = os.environ.get('LANGUAGE_SUBSCRIPTION_KEY')
#             endpoint = os.environ.get('LANGUAGE_ENDPOINT')
#             if not all([key, endpoint]):
#                 logger.warning("Azure Language credentials incomplete. Text analytics features disabled.")
#                 return None
#             credential = AzureKeyCredential(key)
#             return TextAnalyticsClient(endpoint=endpoint, credential=credential)
#         except Exception as e:
#             logger.error(f"Failed to initialize Azure Language client: {str(e)}")
#             return None
    
#     def _init_speech_config(self) -> Optional[speechsdk.SpeechConfig]:
#         if not SPEECH_AVAILABLE: return None
#         try:
#             key = os.environ.get('SPEECH_SUBSCRIPTION_KEY')
#             region = os.environ.get('SPEECH_REGION')
#             if not all([key, region]):
#                 logger.warning("Azure Speech credentials incomplete. Speech features disabled.")
#                 return None
#             return speechsdk.SpeechConfig(subscription=key, region=region)
#         except Exception as e:
#             logger.error(f"Failed to initialize Azure Speech config: {str(e)}")
#             return None
    
#     def _init_vision_client(self) -> Optional[ComputerVisionClient]:
#         if not VISION_AVAILABLE: return None
#         try:
#             key = os.environ.get('VISION_SUBSCRIPTION_KEY')
#             endpoint = os.environ.get('VISION_ENDPOINT')
#             if not all([key, endpoint]):
#                 logger.warning("Azure Vision credentials incomplete. Vision features disabled.")
#                 return None
#             credentials = CognitiveServicesCredentials(key)
#             return ComputerVisionClient(endpoint=endpoint, credentials=credentials)
#         except Exception as e:
#             logger.error(f"Failed to initialize Azure Vision client: {str(e)}")
#             return None
    
#     def _log_initialization_status(self):
#         logger.info(f"Azure Translator Service: {'Available' if self.translator_client else 'Unavailable'}")
#         logger.info(f"Azure Language Service: {'Available' if self.language_client else 'Unavailable'}")
#         logger.info(f"Azure Speech Service: {'Available' if self.speech_config else 'Unavailable'}")
#         logger.info(f"Azure Computer Vision Service: {'Available' if self.vision_client else 'Unavailable'}")

#     def translate_text(self, text: str, target_languages: List[str], source_language: Optional[str] = None) -> Dict[str, Any]:
#         if not self.translator_client:
#             return {"error": "Translation service is not available due to client initialization failure."}
#         try:
#             input_text_elements = [{'text': text}]
#             response = self.translator_client.translate(
#                 content=input_text_elements,
#                 to=target_languages,
#                 from_parameter=source_language 
#             )
#             translations = {}
#             if response and isinstance(response, list) and len(response) > 0 and response[0].translations:
#                 for translation_item in response[0].translations:
#                     translations[translation_item.to] = translation_item.text
#             else:
#                 logger.warning(f"Unexpected translation response structure or empty translations: {response}")
#                 return {"error": "Translation failed or returned no results."}
#             return translations
#         except Exception as e:
#             logger.error(f"Translation error: {str(e)}", exc_info=True)
#             if "401" in str(e) or "authentication" in str(e).lower() or "credential" in str(e).lower():
#                  return {"error": f"(401) Translation authorization failed. Details: {str(e)}"}
#             return {"error": f"Translation failed: {str(e)}"}
    
#     def analyze_sentiment(self, text: str) -> Dict[str, Any]:
#         if not self.language_client:
#             return {"error": "Sentiment analysis service is not available."}
#         try:
#             documents = [text] 
#             response = self.language_client.analyze_sentiment(documents=documents, show_opinion_mining=True)
#             result_doc = response[0]
#             if result_doc.is_error:
#                 return {"error": f"Sentiment analysis document error: {result_doc.error.message}"}
#             result = {
#                 "sentiment": result_doc.sentiment,
#                 "confidence_scores": {
#                     "positive": result_doc.confidence_scores.positive,
#                     "neutral": result_doc.confidence_scores.neutral,
#                     "negative": result_doc.confidence_scores.negative
#                 }, "sentences": []
#             }
#             for sentence in result_doc.sentences:
#                 s_data = {"text": sentence.text, "sentiment": sentence.sentiment, "confidence_scores": {
#                     "positive": sentence.confidence_scores.positive, "neutral": sentence.confidence_scores.neutral,
#                     "negative": sentence.confidence_scores.negative
#                 }, "opinions": []}
#                 for opinion in sentence.mined_opinions:
#                     s_data["opinions"].append({"target_text": opinion.target.text, "target_sentiment": opinion.target.sentiment,
#                                                "assessments": [{"text": ass.text, "sentiment": ass.sentiment} for ass in opinion.assessments]})
#                 result["sentences"].append(s_data)
#             return result
#         except Exception as e:
#             logger.error(f"Sentiment analysis error: {str(e)}", exc_info=True)
#             return {"error": f"Sentiment analysis failed: {str(e)}"}
    
#     def extractive_summarize(self, text: str, sentence_count: int = 3) -> Dict[str, Any]:
#         if not self.language_client: return {"error": "Summarization service unavailable."}
#         if len(text) > EXTRACTIVE_SUMMARY_CHAR_LIMIT:
#             text = text[:EXTRACTIVE_SUMMARY_CHAR_LIMIT]; logger.warning("Extractive summary text truncated.")
#         try:
#             poller = self.language_client.begin_extract_summary([{"id": "1", "language": "en", "text": text}], max_sentence_count=sentence_count)
#             res = poller.result(); result = {}
#             for doc_res in res:
#                 if doc_res.is_error: result["error"] = f"Extractive summary error: {doc_res.error.message}"; break
#                 result["summary"] = " ".join([s.text for s in doc_res.sentences])
#                 result["sentences"] = [s.text for s in doc_res.sentences]; break
#             return result
#         except Exception as e:
#             logger.error(f"Extractive summarization error: {str(e)}", exc_info=True)
#             return {"error": f"Extractive summarization failed: {str(e)}"}

#     def abstractive_summarize(self, text: str, sentence_count: Optional[int] = None) -> Dict[str, Any]:
#         if not self.language_client: return {"error": "Summarization service unavailable."}
#         if len(text) > ABSTRACTIVE_SUMMARY_CHAR_LIMIT:
#             text = text[:ABSTRACTIVE_SUMMARY_CHAR_LIMIT]; logger.warning("Abstractive summary text truncated.")
#         try:
#             opts = {"sentence_count": sentence_count} if sentence_count and sentence_count > 0 else {}
#             poller = self.language_client.begin_abstract_summary([{"id": "1", "language": "en", "text": text}], **opts)
#             res = poller.result(); result = {}
#             for doc_res in res:
#                 if doc_res.is_error: result["error"] = f"Abstractive summary error: {doc_res.error.message}"; break
#                 result["summary"] = doc_res.summaries[0].text if doc_res.summaries else ""; break
#             return result
#         except Exception as e:
#             logger.error(f"Abstractive summarization error: {str(e)}", exc_info=True)
#             return {"error": f"Abstractive summarization failed: {str(e)}"}
    
#     def analyze_image(self, image_path: str, visual_features: Optional[List[VisualFeatureTypes]] = None) -> Dict[str, Any]:
#         if not self.vision_client:
#             return {"error": "Vision service is not available."}
        
#         features_to_use = visual_features # visual_features is now expected to be List[VisualFeatureTypes]
#         if not features_to_use: # Fallback if app.py failed to provide mapped features
#             features_to_use = [
#                 VisualFeatureTypes.categories, VisualFeatureTypes.tags, VisualFeatureTypes.description,
#                 VisualFeatureTypes.objects, VisualFeatureTypes.adult
#             ]
#             logger.warning(f"No specific visual_features (enums) provided to analyze_image, using default set.")
        
#         logger.info(f"Analyzing image {image_path} with features: {[f.value for f in features_to_use if hasattr(f, 'value')]}")

#         try:
#             with open(image_path, "rb") as image_file:
#                 response = self.vision_client.analyze_image_in_stream(
#                     image=image_file,
#                     visual_features=features_to_use 
#                 )
#                 result = self.make_vision_result_serializable(response)
#                 return result
#         except Exception as e:
#             logger.error(f"Image analysis error for {image_path}: {str(e)}", exc_info=True)
#             return {"error": f"Image analysis failed: {str(e)}"}

#     def make_vision_result_serializable(self, vision_response) -> Dict[str, Any]:
#         result = {}
#         if vision_response is None: return result
#         try:
#             if hasattr(vision_response, 'categories') and vision_response.categories:
#                 result['categories'] = []
#                 for c in vision_response.categories:
#                     category_detail = None; detail_dict = {}
#                     if c.detail:
#                         if hasattr(c.detail, 'celebrities') and c.detail.celebrities:
#                             detail_dict['celebrities'] = [{'name': celeb.name, 'confidence': celeb.confidence, 
#                                                            'face_rectangle': celeb.face_rectangle.__dict__ if celeb.face_rectangle and hasattr(celeb.face_rectangle, '__dict__') else None} 
#                                                           for celeb in c.detail.celebrities]
#                         if hasattr(c.detail, 'landmarks') and c.detail.landmarks:
#                              detail_dict['landmarks'] = [{'name': landmark.name, 'confidence': landmark.confidence} for landmark in c.detail.landmarks]
#                     if detail_dict: category_detail = detail_dict
#                     result['categories'].append({'name': c.name, 'score': c.score, 'detail': category_detail})

#             if hasattr(vision_response, 'tags') and vision_response.tags:
#                 result['tags'] = [{'name': t.name, 'confidence': t.confidence} for t in vision_response.tags]
            
#             if hasattr(vision_response, 'description') and vision_response.description and vision_response.description.captions:
#                 result['description'] = {
#                     'captions': [{'text': c.text, 'confidence': c.confidence} for c in vision_response.description.captions if c.text],
#                     'tags': list(vision_response.description.tags) if vision_response.description.tags else []
#                 }
            
#             if hasattr(vision_response, 'objects') and vision_response.objects:
#                 result['objects'] = [{'object_property': o.object_property, 
#                                     'confidence': o.confidence, 
#                                     'rectangle': o.rectangle.__dict__ if o.rectangle and hasattr(o.rectangle, '__dict__') else None} 
#                                    for o in vision_response.objects]
            
#             if hasattr(vision_response, 'adult') and vision_response.adult:
#                 result['adult'] = {'is_adult_content': vision_response.adult.is_adult_content, 
#                                    'is_racy_content': vision_response.adult.is_racy_content,
#                                    'is_gory_content': getattr(vision_response.adult, 'is_gory_content', None), 
#                                    'adult_score': vision_response.adult.adult_score,
#                                    'racy_score': vision_response.adult.racy_score, 
#                                    'gory_score': getattr(vision_response.adult, 'gory_score', None)}
            
#             if hasattr(vision_response, 'brands') and vision_response.brands:
#                 result['brands'] = [{'name': b.name, 
#                                      'confidence': b.confidence,
#                                      'rectangle': b.rectangle.__dict__ if b.rectangle and hasattr(b.rectangle, '__dict__') else None} 
#                                     for b in vision_response.brands]
            
#             if hasattr(vision_response, 'color') and vision_response.color:
#                 result['color'] = {'dominant_color_foreground': vision_response.color.dominant_color_foreground,
#                                    'dominant_color_background': vision_response.color.dominant_color_background,
#                                    'dominant_colors': list(vision_response.color.dominant_colors) if vision_response.color.dominant_colors else [],
#                                    'accent_color': vision_response.color.accent_color, 
#                                    'is_bw_img': vision_response.color.is_bw_img}
            
#             if hasattr(vision_response, 'faces') and vision_response.faces:
#                 result['faces'] = [{'age': f.age, 
#                                     'gender': str(f.gender) if f.gender else None, 
#                                     'face_rectangle': f.face_rectangle.__dict__ if f.face_rectangle and hasattr(f.face_rectangle, '__dict__') else None} 
#                                    for f in vision_response.faces]
#         except Exception as e:
#             logger.error(f"Error during vision result serialization: {e}", exc_info=True)
#             result['serialization_error'] = str(e) 
            
#         return result
    
#     def get_speech_token(self) -> Dict[str, Any]:
#         if not self.speech_config:
#             return {"error": "Speech service configuration is not available."}
#         try:
#             subscription_key = os.environ.get('SPEECH_SUBSCRIPTION_KEY')
#             region = self.speech_config.region 
#             if not subscription_key or not region:
#                 return {"error": "Speech service credentials not properly configured on the server."}
#             return {"subscription_key": subscription_key, "region": region}
#         except Exception as e:
#             logger.error(f"Error getting speech credentials: {str(e)}", exc_info=True)
#             return {"error": f"Failed to get speech credentials: {str(e)}"}

# azure_services = AzureServiceManager()




"""
Azure AI Service Integration Module

This module provides initialization and utility functions for Azure AI services.
It handles credential management, client initialization, and error handling.
"""

import os
import logging
import io # Required for BytesIO
from typing import Optional, Dict, List, Any 

# Configure logging (app.py should ideally configure root logger)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Azure Translator Service
try:
    from azure.ai.translation.text import TextTranslationClient
    from azure.core.credentials import AzureKeyCredential as AzureKeyCredentialTranslation # Alias
    TRANSLATOR_AVAILABLE = True
    logger.info("Azure Translator SDK (azure-ai-translation-text) imported successfully.")
except ImportError as e:
    TRANSLATOR_AVAILABLE = False
    logger.warning(f"Azure Translator SDK not available: {str(e)}. Translation features will be disabled.")
    TextTranslationClient = None # For type hinting
    AzureKeyCredentialTranslation = None 

# Azure Language Service (Text Analytics)
try:
    from azure.core.credentials import AzureKeyCredential # Standard AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient
    LANGUAGE_AVAILABLE = True
    logger.info("Azure Language SDK (azure-ai-textanalytics) imported successfully.")
except ImportError as e:
    LANGUAGE_AVAILABLE = False
    logger.warning(f"Azure Language SDK not available: {str(e)}. Text analytics features will be disabled.")
    TextAnalyticsClient = None
    AzureKeyCredential = None

# Azure Speech Service
try:
    import azure.cognitiveservices.speech as speechsdk
    SPEECH_AVAILABLE = True
    logger.info("Azure Speech SDK (azure-cognitiveservices-speech) imported successfully.")
except ImportError as e:
    SPEECH_AVAILABLE = False
    logger.warning(f"Azure Speech SDK not available: {str(e)}. Speech features will be disabled.")
    speechsdk = None # For type hinting

# Azure Computer Vision Service
try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    # VisualFeatureTypes is used to specify which features to analyze
    from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes 
    from msrest.authentication import CognitiveServicesCredentials # Used by older Vision SDK
    VISION_AVAILABLE = True
    logger.info("Azure Computer Vision SDK (azure-cognitiveservices-vision-computervision) imported successfully.")
except ImportError as e:
    VISION_AVAILABLE = False
    logger.warning(f"Azure Computer Vision SDK not available: {str(e)}. Vision features will be disabled.")
    ComputerVisionClient = None
    VisualFeatureTypes = None 
    CognitiveServicesCredentials = None


# Define character limits for summarization services
ABSTRACTIVE_SUMMARY_CHAR_LIMIT = int(os.environ.get("ABSTRACTIVE_SUMMARY_CHAR_LIMIT", 120000))
EXTRACTIVE_SUMMARY_CHAR_LIMIT = int(os.environ.get("EXTRACTIVE_SUMMARY_CHAR_LIMIT", 5000))

class AzureServiceManager:
    """
    Manages Azure AI service clients and provides utility functions for service operations.
    Handles initialization, credential management, and error handling.
    """
    
    def __init__(self):
        """Initialize Azure service clients based on available environment variables."""
        self.translator_client: Optional[TextTranslationClient] = self._init_translator_client()
        self.language_client: Optional[TextAnalyticsClient] = self._init_language_client()
        self.speech_config: Optional[speechsdk.SpeechConfig] = self._init_speech_config() if speechsdk else None
        self.vision_client: Optional[ComputerVisionClient] = self._init_vision_client()
        
        self._log_initialization_status()
    
    def _init_translator_client(self) -> Optional[TextTranslationClient]:
        if not TRANSLATOR_AVAILABLE or not TextTranslationClient or not AzureKeyCredentialTranslation: return None
        try:
            key = os.environ.get('TRANSLATOR_SUBSCRIPTION_KEY')
            endpoint = os.environ.get('TRANSLATOR_ENDPOINT')
            if not all([key, endpoint]):
                logger.warning("Azure Translator key or endpoint incomplete in .env. Translation features will be disabled.")
                return None
            logger.info(f"Initializing Azure Translator client with endpoint: {endpoint} (Key: ***{key[-4:]})")
            credential = AzureKeyCredentialTranslation(key) 
            return TextTranslationClient(endpoint=endpoint, credential=credential)
        except Exception as e:
            logger.error(f"Failed to initialize Azure Translator client: {str(e)}", exc_info=True)
            return None
    
    def _init_language_client(self) -> Optional[TextAnalyticsClient]:
        if not LANGUAGE_AVAILABLE or not TextAnalyticsClient or not AzureKeyCredential: return None
        try:
            key = os.environ.get('LANGUAGE_SUBSCRIPTION_KEY')
            endpoint = os.environ.get('LANGUAGE_ENDPOINT')
            if not all([key, endpoint]):
                logger.warning("Azure Language credentials incomplete in .env. Text analytics features will be disabled.")
                return None
            logger.info(f"Initializing Azure Language client with endpoint: {endpoint} (Key: ***{key[-4:]})")
            credential = AzureKeyCredential(key)
            return TextAnalyticsClient(endpoint=endpoint, credential=credential)
        except Exception as e:
            logger.error(f"Failed to initialize Azure Language client: {str(e)}", exc_info=True)
            return None
    
    def _init_speech_config(self) -> Optional[speechsdk.SpeechConfig]:
        if not SPEECH_AVAILABLE or not speechsdk: return None
        try:
            key = os.environ.get('SPEECH_SUBSCRIPTION_KEY')
            region = os.environ.get('SPEECH_REGION')
            if not all([key, region]):
                logger.warning("Azure Speech credentials incomplete in .env. Speech features will be disabled.")
                return None
            logger.info(f"Initializing Azure Speech config with region: {region} (Key: ***{key[-4:]})")
            return speechsdk.SpeechConfig(subscription=key, region=region)
        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech config: {str(e)}", exc_info=True)
            return None
    
    def _init_vision_client(self) -> Optional[ComputerVisionClient]:
        if not VISION_AVAILABLE or not ComputerVisionClient or not CognitiveServicesCredentials: return None
        try:
            key = os.environ.get('VISION_SUBSCRIPTION_KEY')
            endpoint = os.environ.get('VISION_ENDPOINT')
            if not all([key, endpoint]):
                logger.warning("Azure Vision credentials incomplete in .env. Vision features will be disabled.")
                return None
            logger.info(f"Initializing Azure Vision client with endpoint: {endpoint} (Key: ***{key[-4:]})")
            credentials = CognitiveServicesCredentials(key)
            return ComputerVisionClient(endpoint=endpoint, credentials=credentials)
        except Exception as e:
            logger.error(f"Failed to initialize Azure Vision client: {str(e)}", exc_info=True)
            return None
    
    def _log_initialization_status(self):
        logger.info(f"Azure Translator Service Status: {'Available' if self.translator_client else 'Unavailable'}")
        logger.info(f"Azure Language Service Status: {'Available' if self.language_client else 'Unavailable'}")
        logger.info(f"Azure Speech Service Status: {'Available' if self.speech_config else 'Unavailable'}")
        logger.info(f"Azure Computer Vision Service Status: {'Available' if self.vision_client else 'Unavailable'}")
    
    def translate_text(self, text: str, target_languages: List[str], source_language: Optional[str] = None) -> Dict[str, Any]:
        if not self.translator_client:
            return {"error": "Translation service is not available (client not initialized)."}
        if not text or not target_languages:
            return {"error": "Text and target_languages are required for translation."}
        try:
            input_text_elements = [{'text': text}]
            response = self.translator_client.translate(
                content=input_text_elements,
                to=target_languages,
                from_parameter=source_language # SDK uses 'from_parameter'
            )
            translations: Dict[str, str] = {}
            # Response is a list, one item per input_text_element
            if response and isinstance(response, list) and len(response) > 0 and response[0].translations:
                for translation_item in response[0].translations:
                    translations[translation_item.to] = translation_item.text
            else:
                logger.warning(f"Unexpected translation response structure or empty translations: {response}")
                return {"error": "Translation failed or returned no results."}
            return translations # Returns dict like {'fr': 'Bonjour', 'es': 'Hola'}
        except Exception as e:
            logger.error(f"Translation API error: {str(e)}", exc_info=True)
            err_msg = f"Translation failed: {str(e)}"
            if "401" in str(e) or "authentication" in str(e).lower():
                 err_msg = f"(401) Translation authorization failed. Check Translator API key/endpoint. Details: {str(e)}"
            return {"error": err_msg}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        if not self.language_client:
            return {"error": "Sentiment analysis service is not available (client not initialized)."}
        if not text:
            return {"error": "Text is required for sentiment analysis."}
        try:
            documents = [text] 
            response_list = self.language_client.analyze_sentiment(documents=documents, show_opinion_mining=True)
            
            if not response_list or len(response_list) == 0:
                return {"error": "Sentiment analysis returned an empty response."}

            result_doc = response_list[0] 
            if result_doc.is_error:
                logger.error(f"Sentiment analysis document error: Code: {result_doc.error.code}, Message: {result_doc.error.message}")
                return {"error": f"Sentiment analysis document error: {result_doc.error.message}"}
            
            result = {
                "sentiment": result_doc.sentiment,
                "confidence_scores": {
                    "positive": result_doc.confidence_scores.positive,
                    "neutral": result_doc.confidence_scores.neutral,
                    "negative": result_doc.confidence_scores.negative
                },
                "sentences": []
            }
            for sentence in result_doc.sentences:
                sentence_data = {
                    "text": sentence.text, "sentiment": sentence.sentiment,
                    "confidence_scores": {
                        "positive": sentence.confidence_scores.positive,
                        "neutral": sentence.confidence_scores.neutral,
                        "negative": sentence.confidence_scores.negative
                    },
                    "opinions": []
                }
                if sentence.mined_opinions: # Check if opinions exist
                    for opinion in sentence.mined_opinions:
                        opinion_data = {
                            "target_text": opinion.target.text,
                            "target_sentiment": opinion.target.sentiment,
                            "assessments": [{"text": assessment.text, "sentiment": assessment.sentiment} 
                                            for assessment in opinion.assessments]
                        }
                        sentence_data["opinions"].append(opinion_data)
                result["sentences"].append(sentence_data)
            return result
        except Exception as e:
            logger.error(f"Sentiment analysis API error: {str(e)}", exc_info=True)
            return {"error": f"Sentiment analysis failed: {str(e)}"}
    
    def extractive_summarize(self, text: str, sentence_count: int = 3) -> Dict[str, Any]:
        if not self.language_client:
            return {"error": "Summarization service is not available (client not initialized)."}
        if not text: return {"error": "Text is required for extractive summarization."}

        if len(text) > EXTRACTIVE_SUMMARY_CHAR_LIMIT:
            text = text[:EXTRACTIVE_SUMMARY_CHAR_LIMIT]
            logger.warning(f"Text for extractive summarization truncated to {EXTRACTIVE_SUMMARY_CHAR_LIMIT} chars.")
        try:
            # SDK expects list of dicts, each with id, language, text
            documents = [{"id": "1", "language": "en", "text": text}] 
            poller = self.language_client.begin_extract_summary(documents, max_sentence_count=sentence_count)
            extract_summary_results = poller.result() # Wait for completion
            
            result: Dict[str, Any] = {} # Explicitly type
            for doc_result in extract_summary_results: # Iterate over results (usually one for single doc input)
                if doc_result.is_error:
                    logger.error(f"Extractive summarization document error: Code: {doc_result.error.code}, Message: {doc_result.error.message}")
                    result["error"] = f"Extractive summary document error: {doc_result.error.message}"
                    break 
                result["summary"] = " ".join([sentence.text for sentence in doc_result.sentences])
                result["sentences"] = [sentence.text for sentence in doc_result.sentences]
                break # Assuming single document processing
            return result
        except Exception as e:
            logger.error(f"Extractive summarization API error: {str(e)}", exc_info=True)
            return {"error": f"Extractive summarization failed: {str(e)}"}
    
    def abstractive_summarize(self, text: str, sentence_count: Optional[int] = None) -> Dict[str, Any]:
        if not self.language_client:
            return {"error": "Summarization service is not available (client not initialized)."}
        if not text: return {"error": "Text is required for abstractive summarization."}

        if len(text) > ABSTRACTIVE_SUMMARY_CHAR_LIMIT:
            text = text[:ABSTRACTIVE_SUMMARY_CHAR_LIMIT]
            logger.warning(f"Text for abstractive summarization truncated to {ABSTRACTIVE_SUMMARY_CHAR_LIMIT} chars.")
        try:
            documents = [{"id": "1", "language": "en", "text": text}]
            poller_options = {}
            if sentence_count is not None and sentence_count > 0:
                # Note: For abstractive, 'sentence_count' is a suggestion for the summary length.
                poller_options["sentence_count"] = sentence_count 
                
            poller = self.language_client.begin_abstract_summary(documents, **poller_options)
            abstract_summary_results = poller.result() # Wait for completion
            
            result: Dict[str, Any] = {}
            for doc_result in abstract_summary_results:
                if doc_result.is_error:
                    logger.error(f"Abstractive summarization document error: Code: {doc_result.error.code}, Message: {doc_result.error.message}")
                    result["error"] = f"Abstractive summary document error: {doc_result.error.message}"
                    break
                result["summary"] = doc_result.summaries[0].text if doc_result.summaries else ""
                break # Assuming single document processing
            return result
        except Exception as e:
            logger.error(f"Abstractive summarization API error: {str(e)}", exc_info=True)
            return {"error": f"Abstractive summarization failed: {str(e)}"}
    
    def analyze_image(self, image_path: str, visual_features_enums: Optional[List[VisualFeatureTypes]] = None) -> Dict[str, Any]:
        """Analyze image using Azure Computer Vision. Takes a list of VisualFeatureTypes enums."""
        if not self.vision_client:
            return {"error": "Vision service is not available (client not initialized)."}
        if not os.path.exists(image_path):
            return {"error": f"Image file not found at path: {image_path}"}
        if not VisualFeatureTypes: # Check if the enum class itself is available
             return {"error": "VisualFeatureTypes enum not available from SDK. Cannot analyze image."}

        # Default features if none are provided or if the provided list is empty
        features_to_request = visual_features_enums
        if not features_to_request:
            logger.warning("No specific visual features (enums) provided to analyze_image, using a default set.")
            features_to_request = [
                VisualFeatureTypes.description, VisualFeatureTypes.tags, VisualFeatureTypes.objects,
                VisualFeatureTypes.categories, VisualFeatureTypes.adult, VisualFeatureTypes.faces
            ]
        
        # Log the string values of the enums being requested
        feature_names_requested = [f.value if hasattr(f, 'value') else str(f) for f in features_to_request]
        logger.info(f"Analyzing image '{os.path.basename(image_path)}' with features: {feature_names_requested}")

        try:
            with open(image_path, "rb") as image_file_stream:
                # The SDK's analyze_image_in_stream expects the list of enum members directly
                analysis_response = self.vision_client.analyze_image_in_stream(
                    image=image_file_stream,
                    visual_features=features_to_request # Pass the list of enums
                )
                # Process the response into a serializable format
                serialized_result = self.make_vision_result_serializable(analysis_response)
                return serialized_result
        except Exception as e:
            logger.error(f"Image analysis API error for '{os.path.basename(image_path)}': {str(e)}", exc_info=True)
            return {"error": f"Image analysis failed: {str(e)}"}
    
    def make_vision_result_serializable(self, vision_response) -> Dict[str, Any]:
        """Convert Vision API response to a JSON-serializable dictionary."""
        result: Dict[str, Any] = {}
        if vision_response is None: return result # Handle null response early

        try: # Wrap serialization in try-except to catch issues with unexpected response structures
            if hasattr(vision_response, 'categories') and vision_response.categories:
                result['categories'] = []
                for c in vision_response.categories:
                    category_detail = None
                    # Check for 'detail' and its attributes, which might be None
                    if c.detail:
                        detail_dict = {}
                        if hasattr(c.detail, 'celebrities') and c.detail.celebrities:
                            detail_dict['celebrities'] = [{'name': celeb.name, 'confidence': celeb.confidence, 
                                                           'face_rectangle': celeb.face_rectangle.__dict__ if celeb.face_rectangle else None} 
                                                          for celeb in c.detail.celebrities]
                        if hasattr(c.detail, 'landmarks') and c.detail.landmarks:
                             detail_dict['landmarks'] = [{'name': landmark.name, 'confidence': landmark.confidence} for landmark in c.detail.landmarks]
                        if detail_dict: # Only add detail if it has content
                            category_detail = detail_dict
                    result['categories'].append({'name': c.name, 'score': c.score, 'detail': category_detail})

            if hasattr(vision_response, 'tags') and vision_response.tags:
                result['tags'] = [{'name': t.name, 'confidence': t.confidence} for t in vision_response.tags]
            
            if hasattr(vision_response, 'description') and vision_response.description:
                result['description'] = {
                    'captions': [{'text': c.text, 'confidence': c.confidence} 
                                 for c in vision_response.description.captions if c.text] if vision_response.description.captions else [],
                    'tags': list(vision_response.description.tags) if vision_response.description.tags else []
                }
            
            if hasattr(vision_response, 'objects') and vision_response.objects:
                result['objects'] = [{'object_property': o.object_property, # Changed from 'object' to avoid keyword clash
                                    'confidence': o.confidence, 
                                    'rectangle': o.rectangle.__dict__ if o.rectangle else None} 
                                   for o in vision_response.objects]
            
            if hasattr(vision_response, 'adult') and vision_response.adult:
                result['adult'] = {'is_adult_content': vision_response.adult.is_adult_content, 
                                   'is_racy_content': vision_response.adult.is_racy_content,
                                   'is_gory_content': getattr(vision_response.adult, 'is_gory_content', None), # Check if attr exists
                                   'adult_score': vision_response.adult.adult_score,
                                   'racy_score': vision_response.adult.racy_score, 
                                   'gory_score': getattr(vision_response.adult, 'gory_score', None)}
            
            if hasattr(vision_response, 'brands') and vision_response.brands:
                result['brands'] = [{'name': b.name, 
                                     'confidence': b.confidence,
                                     'rectangle': b.rectangle.__dict__ if b.rectangle else None} 
                                    for b in vision_response.brands]
            
            if hasattr(vision_response, 'color') and vision_response.color:
                result['color'] = {'dominant_color_foreground': vision_response.color.dominant_color_foreground,
                                   'dominant_color_background': vision_response.color.dominant_color_background,
                                   'dominant_colors': list(vision_response.color.dominant_colors) if vision_response.color.dominant_colors else [],
                                   'accent_color': vision_response.color.accent_color, 
                                   'is_bw_img': getattr(vision_response.color, 'is_bw_img', False)} # Use is_bw_img
            
            if hasattr(vision_response, 'faces') and vision_response.faces:
                result['faces'] = [{'age': f.age, 
                                    'gender': str(f.gender) if f.gender else None, # Gender can be an enum
                                    'face_rectangle': f.face_rectangle.__dict__ if f.face_rectangle else None} 
                                   for f in vision_response.faces]
        except Exception as e:
            logger.error(f"Error during vision result serialization: {e}", exc_info=True)
            result['serialization_error'] = f"Could not fully serialize vision response: {str(e)}" # Add error info to result
            
        return result
    
    def get_speech_token(self) -> Dict[str, Any]:
        """
        Provides credentials needed for client-side Speech SDK.
        Returns subscription key and region, as tokens are short-lived and better managed by client SDKs.
        """
        if not self.speech_config: # Check if speech_config was initialized
            return {"error": "Speech service configuration is not available."}
        
        try:
            # The client-side Speech SDK typically uses the subscription key and region directly.
            # Generating and passing a short-lived token from server to client adds complexity
            # and is often not the recommended pattern for direct client-to-Azure speech.
            subscription_key = os.environ.get('SPEECH_SUBSCRIPTION_KEY')
            # speech_config.region is available if speech_config was initialized
            region = self.speech_config.region if self.speech_config else os.environ.get('SPEECH_REGION')

            if not subscription_key or not region:
                logger.error("Speech service subscription key or region is missing in server configuration (.env).")
                return {"error": "Speech service credentials not properly configured on the server."}
            
            return {
                "subscription_key": subscription_key,
                "region": region
            }
        except Exception as e:
            logger.error(f"Error retrieving speech credentials: {str(e)}", exc_info=True)
            return {"error": f"Failed to retrieve speech credentials: {str(e)}"}

# Create a singleton instance to be imported by other modules (like app.py)
azure_services = AzureServiceManager()
