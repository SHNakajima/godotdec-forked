#!/usr/bin/env python3
"""
CTEX to Image Converter
Converts Godot 4.x CTEX files to PNG/WEBP images
"""

import os
import struct
from pathlib import Path

def convert_ctex_to_image(ctex_path, output_dir=None):
    """
    Convert a single CTEX file to image format
    
    Args:
        ctex_path (str): Path to the CTEX file
        output_dir (str): Output directory (optional, defaults to same directory)
    
    Returns:
        tuple: (success: bool, output_path: str, error_message: str)
    """
    try:
        with open(ctex_path, 'rb') as f:
            # CTEXファイルのサイズチェック
            f.seek(0, 2)  # ファイル末尾に移動
            file_size = f.tell()
            f.seek(0)  # ファイル先頭に戻る
            
            if file_size < 56:
                return False, "", f"File too small ({file_size} bytes), minimum 56 bytes required"
            
            # 最初の36バイトをスキップ
            f.seek(36)
            
            # フォーマット情報を読み取り (リトルエンディアン)
            format_bytes = f.read(4)
            if len(format_bytes) < 4:
                return False, "", "Failed to read format information"
                
            format_type = struct.unpack('<I', format_bytes)[0]
            
            # さらに16バイトスキップ (合計56バイト)
            f.seek(56)
            
            # 残りの画像データを読み取り
            image_data = f.read()
            
            if not image_data:
                return False, "", "No image data found after header"
            
            # フォーマットに応じて拡張子を決定
            format_map = {
                0: '.unknown',  # IMAGE
                1: '.png',      # PNG
                2: '.webp',     # WEBP
                3: '.basis'     # BASIS_UNIVERSAL
            }
            
            ext = format_map.get(format_type, f'.format{format_type}')
            
            # 出力パスを生成
            ctex_file = Path(ctex_path)
            if output_dir:
                output_path = Path(output_dir) / (ctex_file.stem + ext)
            else:
                output_path = ctex_file.parent / (ctex_file.stem + ext)
            
            # 出力ディレクトリを作成
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 画像データをファイルに保存
            with open(output_path, 'wb') as out:
                out.write(image_data)
            
            format_name = {
                0: 'IMAGE',
                1: 'PNG', 
                2: 'WEBP',
                3: 'BASIS_UNIVERSAL'
            }.get(format_type, f'UNKNOWN({format_type})')
            
            return True, str(output_path), f"Format: {format_name}, Size: {len(image_data)} bytes"
            
    except Exception as e:
        return False, "", f"Error processing file: {str(e)}"

def find_ctex_files(directory="."):
    """
    Find all CTEX files in directory and subdirectories
    
    Args:
        directory (str): Directory to search in
        
    Returns:
        list: List of CTEX file paths
    """
    ctex_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.ctex'):
                ctex_files.append(os.path.join(root, file))
    return ctex_files

def main():
    """Main function to convert all CTEX files in current directory"""
    print("CTEX to Image Converter")
    print("=" * 40)
    
    # 現在のディレクトリでCTEXファイルを検索
    current_dir = os.getcwd()
    print(f"Searching for CTEX files in: {current_dir}")
    
    ctex_files = find_ctex_files(current_dir)
    
    if not ctex_files:
        print("No CTEX files found in current directory and subdirectories.")
        return
    
    print(f"Found {len(ctex_files)} CTEX files:")
    for i, file in enumerate(ctex_files, 1):
        print(f"  {i}. {os.path.relpath(file)}")
    
    print("\nConverting files...")
    print("-" * 40)
    
    success_count = 0
    error_count = 0
    
    for ctex_file in ctex_files:
        rel_path = os.path.relpath(ctex_file)
        print(f"Processing: {rel_path}")
        
        success, output_path, message = convert_ctex_to_image(ctex_file)
        
        if success:
            success_count += 1
            print(f"  ✓ Converted to: {os.path.relpath(output_path)}")
            print(f"    {message}")
        else:
            error_count += 1
            print(f"  ✗ Failed: {message}")
        
        print()
    
    print("=" * 40)
    print(f"Conversion completed!")
    print(f"Success: {success_count} files")
    print(f"Errors:  {error_count} files")
    
    if error_count > 0:
        print("\nNote: Some files may not be standard CTEX format or may be corrupted.")

if __name__ == "__main__":
    main()