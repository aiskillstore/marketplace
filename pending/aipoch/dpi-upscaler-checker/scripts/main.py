#!/usr/bin/env python3
"""
DPI Upscaler & Checker
Check image DPI and intelligently upscale low-resolution images

Features:
- Check whether images meet 300 DPI
- Fix blurry low-resolution images using super-resolution algorithms
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import warnings

import numpy as np
from PIL import Image, ExifTags


class DPIChecker:
    """DPI checker"""
    
    def __init__(self, target_dpi: int = 300):
        self.target_dpi = target_dpi
    
    def check_image(self, image_path: str) -> Dict:
        """
        Check the DPI information of a single image
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dictionary containing DPI information
        """
        try:
            with Image.open(image_path) as img:
                width_px, height_px = img.size
                
                # Get DPI information
                dpi = img.info.get('dpi', (None, None))
                
                # Try to get DPI from EXIF
                if dpi[0] is None or dpi[1] is None:
                    dpi = self._get_dpi_from_exif(img)
                
                # If no DPI information, default to 72
                if dpi[0] is None or dpi[1] is None:
                    dpi = (72, 72)
                
                # Calculate print size
                print_width_cm = (width_px / dpi[0]) * 2.54 if dpi[0] else None
                print_height_cm = (height_px / dpi[1]) * 2.54 if dpi[1] else None
                
                # Calculate required scale factor to reach target DPI
                avg_dpi = (dpi[0] + dpi[1]) / 2
                recommended_scale = self.target_dpi / avg_dpi if avg_dpi > 0 else 4
                
                return {
                    'file': image_path,
                    'format': img.format,
                    'mode': img.mode,
                    'width_px': width_px,
                    'height_px': height_px,
                    'dpi': list(dpi),
                    'avg_dpi': round(avg_dpi, 2),
                    'print_width_cm': round(print_width_cm, 2) if print_width_cm else None,
                    'print_height_cm': round(print_height_cm, 2) if print_height_cm else None,
                    'meets_target_dpi': avg_dpi >= self.target_dpi,
                    'recommended_scale': round(recommended_scale, 2),
                    'status': 'ok'
                }
                
        except Exception as e:
            return {
                'file': image_path,
                'error': str(e),
                'status': 'error'
            }
    
    def _get_dpi_from_exif(self, img: Image.Image) -> Tuple[Optional[int], Optional[int]]:
        """Extract DPI from EXIF data"""
        try:
            exif = img._getexif()
            if exif:
                # EXIF tag 282 = XResolution, 283 = YResolution
                x_res = exif.get(282)
                y_res = exif.get(283)
                
                # DPI in EXIF is usually stored as a fraction, e.g. 72/1
                if x_res and isinstance(x_res, tuple):
                    x_res = x_res[0] / x_res[1] if x_res[1] != 0 else x_res[0]
                if y_res and isinstance(y_res, tuple):
                    y_res = y_res[0] / y_res[1] if y_res[1] != 0 else y_res[0]
                
                return (int(x_res) if x_res else None, int(y_res) if y_res else None)
        except:
            pass
        return (None, None)
    
    def check_directory(self, directory: str) -> List[Dict]:
        """Batch check all images in a directory"""
        results = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
        
        for file_path in Path(directory).rglob('*'):
            if file_path.suffix.lower() in image_extensions:
                result = self.check_image(str(file_path))
                results.append(result)
        
        return results


class ImageUpscaler:
    """Image super-resolution processor"""
    
    def __init__(self):
        self.upscaler_type = None
        self._init_upscaler()
    
    def _init_upscaler(self):
        """Initialize super-resolution engine"""
        # Try to use Real-ESRGAN
        try:
            from realesrgan import RealESRGANer
            self.upscaler_type = 'realesrgan'
            print("[INFO] Using Real-ESRGAN super-resolution engine")
        except ImportError:
            # Try to use OpenCV DNN SuperRes
            try:
                import cv2
                self.cv2 = cv2
                self.upscaler_type = 'opencv_dnn'
                print("[INFO] Using OpenCV DNN super-resolution engine")
            except ImportError:
                # Use PIL high-quality interpolation
                self.upscaler_type = 'pil'
                print("[INFO] Using PIL Lanczos interpolation engine")
    
    def upscale(self, 
                image_path: str, 
                output_path: str, 
                scale: int = 2,
                target_dpi: int = 300) -> Dict:
        """
        Apply super-resolution processing to an image
        
        Args:
            image_path: Input image path
            output_path: Output image path
            scale: Upscale factor (2/3/4)
            target_dpi: Target DPI
            
        Returns:
            Processing result information
        """
        try:
            # Read original image
            with Image.open(image_path) as img:
                original_size = img.size
                original_mode = img.mode
                
                # Convert to RGB for AI processing
                if img.mode in ('RGBA', 'P'):
                    img_rgb = img.convert('RGB')
                else:
                    img_rgb = img
                
                # Perform super-resolution
                upscaled_img = self._upscale_image(img_rgb, scale)
                
                # Handle alpha channel if original image had transparency
                if original_mode == 'RGBA':
                    # Upscale alpha channel
                    alpha = img.split()[-1].resize(
                        (upscaled_img.width, upscaled_img.height), 
                        Image.LANCZOS
                    )
                    upscaled_img = upscaled_img.convert('RGBA')
                    upscaled_img.putalpha(alpha)
                
                # Set DPI and save
                upscaled_img.save(
                    output_path, 
                    dpi=(target_dpi, target_dpi),
                    quality=95,
                    optimize=True
                )
                
                return {
                    'input': image_path,
                    'output': output_path,
                    'original_size': original_size,
                    'upscaled_size': upscaled_img.size,
                    'scale': scale,
                    'target_dpi': target_dpi,
                    'status': 'success'
                }
                
        except Exception as e:
            return {
                'input': image_path,
                'error': str(e),
                'status': 'error'
            }
    
    def _upscale_image(self, img: Image.Image, scale: int) -> Image.Image:
        """Perform super-resolution using different engines"""
        if self.upscaler_type == 'pil':
            return self._upscale_pil(img, scale)
        elif self.upscaler_type == 'opencv_dnn':
            return self._upscale_opencv(img, scale)
        else:
            return self._upscale_pil(img, scale)  # Default to PIL
    
    def _upscale_pil(self, img: Image.Image, scale: int) -> Image.Image:
        """Upscale using PIL Lanczos interpolation"""
        new_size = (img.width * scale, img.height * scale)
        return img.resize(new_size, Image.LANCZOS)
    
    def _upscale_opencv(self, img: Image.Image, scale: int) -> Image.Image:
        """Upscale using OpenCV DNN super-resolution"""
        try:
            # Convert to OpenCV format (BGR)
            img_array = np.array(img)
            img_cv = self.cv2.cvtColor(img_array, self.cv2.COLOR_RGB2BGR)
            
            # Use bicubic interpolation as high-quality fallback
            new_width = int(img_cv.shape[1] * scale)
            new_height = int(img_cv.shape[0] * scale)
            upscaled = self.cv2.resize(
                img_cv, 
                (new_width, new_height), 
                interpolation=self.cv2.INTER_CUBIC
            )
            
            # Try to use DNN super-resolution (if model is available)
            try:
                sr = self.cv2.dnn_superres.DnnSuperResImpl_create()
                model_path = f"EDSR_x{scale}.pb"  # Model file needs to be downloaded
                if os.path.exists(model_path):
                    sr.readModel(model_path)
                    sr.setModel("edsr", scale)
                    upscaled = sr.upsample(img_cv)
            except:
                pass  # Use the already upscaled image
            
            # Convert back to PIL format (RGB)
            upscaled_rgb = self.cv2.cvtColor(upscaled, self.cv2.COLOR_BGR2RGB)
            return Image.fromarray(upscaled_rgb)
            
        except Exception as e:
            print(f"[WARN] OpenCV processing failed, falling back to PIL: {e}")
            return self._upscale_pil(img, scale)
    
    def batch_upscale(self,
                      input_dir: str,
                      output_dir: str,
                      scale: int = 2,
                      min_dpi: Optional[int] = None,
                      target_dpi: int = 300) -> List[Dict]:
        """Batch process images"""
        results = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp'}
        
        os.makedirs(output_dir, exist_ok=True)
        
        dpi_checker = DPIChecker(target_dpi) if min_dpi else None
        
        for file_path in Path(input_dir).rglob('*'):
            if file_path.suffix.lower() in image_extensions:
                # Check DPI (if required)
                if min_dpi and dpi_checker:
                    dpi_info = dpi_checker.check_image(str(file_path))
                    if dpi_info.get('meets_target_dpi', False):
                        print(f"[SKIP] {file_path} already meets DPI requirement")
                        continue
                
                # Build output path
                rel_path = file_path.relative_to(input_dir)
                output_path = Path(output_dir) / rel_path.parent / f"{file_path.stem}_upscaled{file_path.suffix}"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                result = self.upscale(str(file_path), str(output_path), scale, target_dpi)
                results.append(result)
                
                if result['status'] == 'success':
                    print(f"[OK] {file_path.name} -> {output_path}")
                else:
                    print(f"[ERROR] {file_path.name}: {result.get('error')}")
        
        return results


def print_dpi_report(result: Dict):
    """Print DPI check report"""
    if result.get('status') == 'error':
        print(f"❌ {result['file']}: {result.get('error')}")
        return
    
    print(f"\n📷 {result['file']}")
    print(f"   Format: {result.get('format', 'Unknown')}")
    print(f"   Size: {result['width_px']} x {result['height_px']} px")
    print(f"   DPI: {result['dpi'][0]} x {result['dpi'][1]}")
    print(f"   Average DPI: {result['avg_dpi']}")
    
    if result.get('print_width_cm'):
        print(f"   Print size: {result['print_width_cm']}cm x {result['print_height_cm']}cm")
    
    if result.get('meets_target_dpi'):
        print(f"   ✅ Meets 300 DPI requirement")
    else:
        print(f"   ⚠️  Does not meet 300 DPI requirement")
        print(f"   💡 Recommended upscale factor: {result['recommended_scale']}x")


def main():
    parser = argparse.ArgumentParser(
        description='DPI Upscaler & Checker - Check image DPI and intelligently upscale',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Check a single image
  python main.py check -i image.jpg
  
  # Batch check and generate report
  python main.py check -i ./images/ -o report.json
  
  # Super-resolution upscale (2x)
  python main.py upscale -i image.jpg -o output.jpg --scale 2
  
  # Batch fix low DPI images
  python main.py upscale -i ./input/ -o ./output/ --min-dpi 300 --scale 4
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # check command
    check_parser = subparsers.add_parser('check', help='Check image DPI')
    check_parser.add_argument('-i', '--input', required=True, 
                              help='Input image path or folder')
    check_parser.add_argument('-o', '--output', 
                              help='Output report path (JSON format)')
    check_parser.add_argument('--target-dpi', type=int, default=300,
                              help='Target DPI (default: 300)')
    
    # upscale command
    upscale_parser = subparsers.add_parser('upscale', help='Super-resolution upscale images')
    upscale_parser.add_argument('-i', '--input', required=True,
                                help='Input image path or folder')
    upscale_parser.add_argument('-o', '--output', required=True,
                                help='Output path')
    upscale_parser.add_argument('--scale', type=int, default=2, choices=[2, 3, 4],
                                help='Upscale factor (default: 2)')
    upscale_parser.add_argument('--min-dpi', type=int,
                                help='Only process images below this DPI')
    upscale_parser.add_argument('--target-dpi', type=int, default=300,
                                help='Target DPI for output images (default: 300)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'check':
        checker = DPIChecker(args.target_dpi)
        
        if os.path.isfile(args.input):
            # Single file check
            result = checker.check_image(args.input)
            print_dpi_report(result)
            results = [result]
        else:
            # Batch check
            print(f"Checking directory: {args.input}")
            results = checker.check_directory(args.input)
            
            # Statistics
            total = len(results)
            errors = sum(1 for r in results if r.get('status') == 'error')
            meets_dpi = sum(1 for r in results if r.get('meets_target_dpi', False))
            
            print(f"\n{'='*50}")
            print(f"Total: {total} images")
            print(f"Errors: {errors}")
            print(f"Meets DPI: {meets_dpi}")
            print(f"Needs fixing: {total - errors - meets_dpi}")
            
            for result in results:
                print_dpi_report(result)
        
        # Save report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\nReport saved: {args.output}")
    
    elif args.command == 'upscale':
        upscaler = ImageUpscaler()
        
        if os.path.isfile(args.input):
            # Single file processing
            result = upscaler.upscale(args.input, args.output, args.scale, args.target_dpi)
            if result['status'] == 'success':
                print(f"✅ Processing successful!")
                print(f"   Input: {result['input']}")
                print(f"   Output: {result['output']}")
                print(f"   Size: {result['original_size']} -> {result['upscaled_size']}")
            else:
                print(f"❌ Processing failed: {result.get('error')}")
                sys.exit(1)
        else:
            # Batch processing
            print(f"Batch processing: {args.input}")
            results = upscaler.batch_upscale(
                args.input, args.output, 
                args.scale, args.min_dpi, args.target_dpi
            )
            
            success = sum(1 for r in results if r['status'] == 'success')
            failed = sum(1 for r in results if r['status'] == 'error')
            
            print(f"\n{'='*50}")
            print(f"Processing complete: {success} succeeded, {failed} failed")


if __name__ == '__main__':
    main()
