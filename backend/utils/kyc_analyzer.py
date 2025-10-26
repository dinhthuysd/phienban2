"""KYC Document Analysis Engine
Tự động phân tích chất lượng ảnh, định dạng document và validation
"""
import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Tuple, List
from datetime import datetime, timezone
import base64
from skimage.metrics import structural_similarity as ssim
import logging

logger = logging.getLogger(__name__)

class KYCDocumentAnalyzer:
    """Advanced document analysis for KYC verification"""
    
    # Quality thresholds
    MIN_IMAGE_WIDTH = 800
    MIN_IMAGE_HEIGHT = 600
    MIN_BRIGHTNESS = 30
    MAX_BRIGHTNESS = 225
    MIN_SHARPNESS = 100
    MIN_FILE_SIZE = 50000  # 50KB
    MAX_FILE_SIZE = 10485760  # 10MB
    
    @staticmethod
    def analyze_image_quality(image_path: str) -> Dict:
        """Phân tích chất lượng ảnh toàn diện"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return {
                    'valid': False,
                    'error': 'Cannot read image file',
                    'quality_score': 0
                }
            
            # Get image properties
            height, width = img.shape[:2]
            
            # 1. Resolution Check
            resolution_check = width >= KYCDocumentAnalyzer.MIN_IMAGE_WIDTH and height >= KYCDocumentAnalyzer.MIN_IMAGE_HEIGHT
            resolution_score = min(100, (width / KYCDocumentAnalyzer.MIN_IMAGE_WIDTH) * 50 + (height / KYCDocumentAnalyzer.MIN_IMAGE_HEIGHT) * 50)
            
            # 2. Brightness Check
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            brightness_check = KYCDocumentAnalyzer.MIN_BRIGHTNESS <= brightness <= KYCDocumentAnalyzer.MAX_BRIGHTNESS
            brightness_score = 100 if brightness_check else max(0, 100 - abs(brightness - 127) / 127 * 100)
            
            # 3. Blur Detection (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_check = laplacian_var >= KYCDocumentAnalyzer.MIN_SHARPNESS
            sharpness_score = min(100, (laplacian_var / 300) * 100)
            
            # 4. Contrast Check
            contrast = gray.std()
            contrast_check = contrast >= 30
            contrast_score = min(100, (contrast / 50) * 100)
            
            # 5. Edge Detection (document boundaries)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.count_nonzero(edges) / (height * width)
            edge_score = min(100, edge_density * 500)
            
            # 6. Color Distribution
            color_hist = [cv2.calcHist([img], [i], None, [256], [0, 256]) for i in range(3)]
            color_variance = np.mean([np.var(hist) for hist in color_hist])
            color_score = min(100, color_variance / 1000)
            
            # Calculate overall quality score
            quality_score = (
                resolution_score * 0.25 +
                brightness_score * 0.20 +
                sharpness_score * 0.25 +
                contrast_score * 0.15 +
                edge_score * 0.10 +
                color_score * 0.05
            )
            
            # Determine quality level
            if quality_score >= 80:
                quality_level = 'excellent'
            elif quality_score >= 60:
                quality_level = 'good'
            elif quality_score >= 40:
                quality_level = 'acceptable'
            else:
                quality_level = 'poor'
            
            # Issues detection
            issues = []
            if not resolution_check:
                issues.append(f'Low resolution: {width}x{height} (minimum {KYCDocumentAnalyzer.MIN_IMAGE_WIDTH}x{KYCDocumentAnalyzer.MIN_IMAGE_HEIGHT})')
            if not brightness_check:
                issues.append(f'Brightness issue: {brightness:.1f} (optimal 50-200)')
            if not blur_check:
                issues.append(f'Image appears blurry (sharpness: {laplacian_var:.1f})')
            if not contrast_check:
                issues.append(f'Low contrast detected ({contrast:.1f})')
            
            return {
                'valid': quality_score >= 40,
                'quality_score': round(quality_score, 2),
                'quality_level': quality_level,
                'resolution': {'width': width, 'height': height, 'passed': resolution_check},
                'brightness': {'value': round(brightness, 2), 'passed': brightness_check},
                'sharpness': {'value': round(laplacian_var, 2), 'passed': blur_check},
                'contrast': {'value': round(contrast, 2), 'passed': contrast_check},
                'edge_density': round(edge_density, 4),
                'issues': issues,
                'recommendations': KYCDocumentAnalyzer._get_recommendations(issues)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image quality: {str(e)}")
            return {
                'valid': False,
                'error': str(e),
                'quality_score': 0
            }
    
    @staticmethod
    def detect_document_type(image_path: str) -> Dict:
        """Phát hiện loại document từ ảnh"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'type': 'unknown', 'confidence': 0}
            
            height, width = img.shape[:2]
            aspect_ratio = width / height
            
            # Detect based on aspect ratio and size
            if 1.5 <= aspect_ratio <= 1.7:
                doc_type = 'id_card'
                confidence = 85
            elif 1.3 <= aspect_ratio <= 1.5:
                doc_type = 'passport'
                confidence = 80
            elif 0.6 <= aspect_ratio <= 0.8:
                doc_type = 'portrait_photo'
                confidence = 75
            elif aspect_ratio > 2.0:
                doc_type = 'driver_license'
                confidence = 70
            else:
                doc_type = 'unknown'
                confidence = 30
            
            # Edge detection for document boundaries
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            has_rectangular_shape = False
            for contour in contours:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                if len(approx) == 4:  # Rectangle detected
                    has_rectangular_shape = True
                    confidence = min(95, confidence + 10)
                    break
            
            return {
                'type': doc_type,
                'confidence': confidence,
                'aspect_ratio': round(aspect_ratio, 2),
                'has_document_shape': has_rectangular_shape,
                'dimensions': {'width': width, 'height': height}
            }
            
        except Exception as e:
            logger.error(f"Error detecting document type: {str(e)}")
            return {'type': 'unknown', 'confidence': 0, 'error': str(e)}
    
    @staticmethod
    def detect_face(image_path: str) -> Dict:
        """Phát hiện khuôn mặt trong ảnh"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {'face_detected': False, 'face_count': 0}
            
            # Load OpenCV's pre-trained face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            face_info = []
            for (x, y, w, h) in faces:
                face_area = w * h
                img_area = img.shape[0] * img.shape[1]
                face_ratio = (face_area / img_area) * 100
                
                face_info.append({
                    'position': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                    'face_ratio': round(face_ratio, 2)
                })
            
            return {
                'face_detected': len(faces) > 0,
                'face_count': len(faces),
                'faces': face_info,
                'valid_for_id': len(faces) == 1  # ID should have exactly 1 face
            }
            
        except Exception as e:
            logger.error(f"Error detecting face: {str(e)}")
            return {'face_detected': False, 'face_count': 0, 'error': str(e)}
    
    @staticmethod
    def validate_document(image_path: str, id_type: str) -> Dict:
        """Validate toàn diện document"""
        try:
            # 1. Quality Analysis
            quality = KYCDocumentAnalyzer.analyze_image_quality(image_path)
            
            # 2. Document Type Detection
            doc_type = KYCDocumentAnalyzer.detect_document_type(image_path)
            
            # 3. Face Detection (for photo IDs)
            face_info = KYCDocumentAnalyzer.detect_face(image_path)
            
            # 4. Overall validation
            validation_score = 0
            validation_checks = []
            
            # Quality check
            if quality.get('valid', False):
                validation_score += 40
                validation_checks.append({'check': 'Image Quality', 'passed': True, 'score': quality['quality_score']})
            else:
                validation_checks.append({'check': 'Image Quality', 'passed': False, 'issues': quality.get('issues', [])})
            
            # Document type check
            if doc_type['confidence'] >= 70:
                validation_score += 30
                validation_checks.append({'check': 'Document Type', 'passed': True, 'detected': doc_type['type']})
            else:
                validation_checks.append({'check': 'Document Type', 'passed': False, 'confidence': doc_type['confidence']})
            
            # Face detection check (for IDs with photos)
            if id_type in ['passport', 'national_id', 'driver_license']:
                if face_info['valid_for_id']:
                    validation_score += 30
                    validation_checks.append({'check': 'Face Detection', 'passed': True, 'faces': face_info['face_count']})
                else:
                    validation_checks.append({'check': 'Face Detection', 'passed': False, 'faces': face_info['face_count']})
            else:
                validation_score += 30  # Not required for other types
            
            # Final decision
            auto_approved = validation_score >= 80 and quality.get('quality_score', 0) >= 60
            requires_manual_review = 50 <= validation_score < 80
            auto_rejected = validation_score < 50
            
            return {
                'validation_score': validation_score,
                'auto_approved': auto_approved,
                'requires_manual_review': requires_manual_review,
                'auto_rejected': auto_rejected,
                'quality_analysis': quality,
                'document_type': doc_type,
                'face_detection': face_info,
                'validation_checks': validation_checks,
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating document: {str(e)}")
            return {
                'validation_score': 0,
                'auto_approved': False,
                'requires_manual_review': True,
                'auto_rejected': False,
                'error': str(e)
            }
    
    @staticmethod
    def _get_recommendations(issues: List[str]) -> List[str]:
        """Get recommendations based on issues"""
        recommendations = []
        
        for issue in issues:
            if 'resolution' in issue.lower():
                recommendations.append('Use a higher resolution camera or scanner')
            if 'brightness' in issue.lower():
                recommendations.append('Ensure good lighting conditions')
            if 'blur' in issue.lower():
                recommendations.append('Hold camera steady and ensure focus')
            if 'contrast' in issue.lower():
                recommendations.append('Place document on contrasting background')
        
        if not recommendations:
            recommendations.append('Document meets quality standards')
        
        return recommendations

    @staticmethod
    def generate_thumbnail(image_path: str, output_path: str, size: Tuple[int, int] = (300, 300)) -> bool:
        """Generate thumbnail cho preview"""
        try:
            img = Image.open(image_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path, 'JPEG', quality=85)
            return True
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            return False
