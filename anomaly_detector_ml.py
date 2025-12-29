#!/usr/bin/env python3
"""
AI/ML Anomaly Detection System for File Structure Analysis
Uses Isolation Forest to detect anomalous files and directories

Author: AI/ML Task Executor
Date: 2025-12-29
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class FileAnomalyDetector:
    """ML-based anomaly detector for file system structures"""

    def __init__(self, contamination=0.1):
        """
        Initialize the anomaly detector

        Args:
            contamination: Expected proportion of anomalies (0.0 to 0.5)
        """
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            max_features=1.0,
            bootstrap=False,
            n_jobs=-1,
            warm_start=False
        )
        self.scaler = StandardScaler()
        self.features = []
        self.metadata = []
        self.predictions = None
        self.scores = None

    def collect_file_metadata(self, base_path, extensions=('.jpg', '.jpeg', '.png')):
        """
        Collect metadata from files in directory structure

        Args:
            base_path: Root directory to analyze
            extensions: File extensions to include

        Returns:
            List of metadata dictionaries
        """
        print(f"[INFO] Scanning directory: {base_path}")
        metadata_list = []

        base_path = Path(base_path)
        if not base_path.exists():
            print(f"[ERROR] Path does not exist: {base_path}")
            return metadata_list

        # Walk through directory tree
        for root, dirs, files in os.walk(base_path):
            root_path = Path(root)

            for filename in files:
                if not any(filename.lower().endswith(ext) for ext in extensions):
                    continue

                filepath = root_path / filename

                try:
                    # Get file stats
                    stats = filepath.stat()

                    # Extract timestamp from filename if present
                    # Format: P{1,2,3}_StoreName_YYYYMMDD_HHMMSS.jpg
                    parts = filename.split('_')
                    timestamp_str = None
                    camera_position = None

                    if len(parts) >= 3 and parts[0].startswith('P'):
                        camera_position = parts[0]
                        # Last two parts before .jpg should be date and time
                        if len(parts) >= 2:
                            # Get last part without extension
                            last_parts = '_'.join(parts[-2:]).replace('.jpg', '').replace('.jpeg', '').split('_')
                            if len(last_parts) >= 2:
                                timestamp_str = '_'.join(last_parts[-2:])

                    metadata = {
                        'filepath': str(filepath),
                        'filename': filename,
                        'directory': str(root_path.relative_to(base_path)),
                        'size_bytes': stats.st_size,
                        'size_kb': stats.st_size / 1024,
                        'size_mb': stats.st_size / (1024 * 1024),
                        'modified_timestamp': stats.st_mtime,
                        'created_timestamp': stats.st_ctime,
                        'camera_position': camera_position,
                        'filename_timestamp': timestamp_str,
                        'depth': len(root_path.relative_to(base_path).parts),
                        'extension': filepath.suffix.lower()
                    }

                    metadata_list.append(metadata)

                except (OSError, PermissionError) as e:
                    print(f"[WARNING] Cannot access {filepath}: {e}")

        print(f"[INFO] Collected metadata for {len(metadata_list)} files")
        return metadata_list

    def extract_features(self, metadata_list):
        """
        Extract numerical features for ML model

        Args:
            metadata_list: List of file metadata dictionaries

        Returns:
            numpy array of features
        """
        print("[INFO] Extracting features for ML model...")

        features = []
        self.metadata = metadata_list

        # Calculate statistical features
        all_sizes = [m['size_bytes'] for m in metadata_list]
        mean_size = np.mean(all_sizes)
        std_size = np.std(all_sizes)

        all_depths = [m['depth'] for m in metadata_list]
        mean_depth = np.mean(all_depths)

        for meta in metadata_list:
            feature_vector = [
                meta['size_bytes'],                          # Feature 1: File size (bytes)
                meta['size_kb'],                             # Feature 2: File size (KB)
                meta['depth'],                               # Feature 3: Directory depth
                meta['modified_timestamp'],                  # Feature 4: Last modified time
                len(meta['filename']),                       # Feature 5: Filename length
                meta['filename'].count('_'),                 # Feature 6: Underscore count (naming pattern)
                len(meta['directory']),                      # Feature 7: Directory path length
                abs(meta['size_bytes'] - mean_size),         # Feature 8: Distance from mean size
                (meta['size_bytes'] - mean_size) / (std_size + 1e-10),  # Feature 9: Z-score of size
                abs(meta['depth'] - mean_depth),             # Feature 10: Distance from mean depth
            ]

            features.append(feature_vector)

        features_array = np.array(features)
        print(f"[INFO] Extracted {features_array.shape[1]} features from {features_array.shape[0]} files")

        return features_array

    def fit_predict(self, features):
        """
        Train Isolation Forest and predict anomalies

        Args:
            features: numpy array of feature vectors

        Returns:
            predictions (-1 for anomaly, 1 for normal)
        """
        print("[INFO] Training Isolation Forest model...")

        # Standardize features
        features_scaled = self.scaler.fit_transform(features)

        # Fit model and predict
        predictions = self.model.fit_predict(features_scaled)

        # Get anomaly scores (lower = more anomalous)
        scores = self.model.score_samples(features_scaled)

        self.predictions = predictions
        self.scores = scores
        self.features = features_scaled

        anomaly_count = np.sum(predictions == -1)
        normal_count = np.sum(predictions == 1)

        print(f"[INFO] Detection complete:")
        print(f"  - Normal files: {normal_count}")
        print(f"  - Anomalous files: {anomaly_count}")
        print(f"  - Contamination rate: {anomaly_count / len(predictions) * 100:.2f}%")

        return predictions

    def get_anomalies(self, top_n=None):
        """
        Get list of detected anomalies sorted by severity

        Args:
            top_n: Return only top N most anomalous files

        Returns:
            List of anomaly dictionaries with metadata and scores
        """
        if self.predictions is None:
            raise ValueError("Must run fit_predict() first")

        anomalies = []

        for i, (pred, score, meta) in enumerate(zip(self.predictions, self.scores, self.metadata)):
            if pred == -1:  # Anomaly detected
                anomaly_info = meta.copy()
                anomaly_info['anomaly_score'] = float(score)
                anomaly_info['severity'] = 'HIGH' if score < -0.5 else 'MEDIUM' if score < -0.2 else 'LOW'
                anomalies.append(anomaly_info)

        # Sort by anomaly score (most anomalous first)
        anomalies.sort(key=lambda x: x['anomaly_score'])

        if top_n:
            return anomalies[:top_n]
        return anomalies

    def generate_report(self, output_path='anomaly_report.json'):
        """
        Generate comprehensive anomaly detection report

        Args:
            output_path: Path to save JSON report

        Returns:
            Dictionary containing report data
        """
        print(f"[INFO] Generating anomaly detection report...")

        anomalies = self.get_anomalies()

        # Calculate statistics
        all_sizes = [m['size_bytes'] for m in self.metadata]
        anomaly_sizes = [a['size_bytes'] for a in anomalies]

        normal_files = [m for m, p in zip(self.metadata, self.predictions) if p == 1]
        normal_sizes = [m['size_bytes'] for m in normal_files]

        # Group anomalies by type
        anomaly_types = defaultdict(list)

        for anomaly in anomalies:
            # Classify anomaly reason
            reasons = []

            if anomaly['size_kb'] < 1:
                reasons.append('EMPTY_OR_TINY_FILE')
            elif anomaly['size_kb'] < 10:
                reasons.append('SUSPICIOUSLY_SMALL')
            elif anomaly['size_mb'] > 5:
                reasons.append('SUSPICIOUSLY_LARGE')

            if anomaly['depth'] == 0:
                reasons.append('WRONG_DIRECTORY_LEVEL')
            elif anomaly['depth'] > 5:
                reasons.append('TOO_DEEPLY_NESTED')

            if anomaly['filename'].count('_') < 2:
                reasons.append('INVALID_NAMING_PATTERN')
            elif anomaly['filename'].count('_') > 10:
                reasons.append('ABNORMAL_FILENAME')

            if not reasons:
                reasons.append('MULTIVARIATE_ANOMALY')

            anomaly['reasons'] = reasons

            for reason in reasons:
                anomaly_types[reason].append(anomaly)

        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_files_analyzed': len(self.metadata),
                'anomalies_detected': len(anomalies),
                'contamination_rate': len(anomalies) / len(self.metadata) * 100,
                'model': 'Isolation Forest',
                'model_parameters': {
                    'n_estimators': 100,
                    'contamination': self.contamination,
                    'random_state': 42
                }
            },
            'statistics': {
                'all_files': {
                    'count': len(self.metadata),
                    'total_size_mb': sum(all_sizes) / (1024 * 1024),
                    'mean_size_kb': np.mean(all_sizes) / 1024,
                    'median_size_kb': np.median(all_sizes) / 1024,
                    'std_size_kb': np.std(all_sizes) / 1024,
                    'min_size_kb': min(all_sizes) / 1024,
                    'max_size_kb': max(all_sizes) / 1024
                },
                'normal_files': {
                    'count': len(normal_files),
                    'mean_size_kb': np.mean(normal_sizes) / 1024 if normal_sizes else 0,
                    'median_size_kb': np.median(normal_sizes) / 1024 if normal_sizes else 0
                },
                'anomalous_files': {
                    'count': len(anomalies),
                    'mean_size_kb': np.mean(anomaly_sizes) / 1024 if anomaly_sizes else 0,
                    'median_size_kb': np.median(anomaly_sizes) / 1024 if anomaly_sizes else 0
                }
            },
            'anomaly_breakdown': {
                anomaly_type: {
                    'count': len(files),
                    'percentage': len(files) / len(anomalies) * 100 if anomalies else 0,
                    'examples': [
                        {
                            'filepath': f['filepath'],
                            'size_kb': f['size_kb'],
                            'severity': f['severity'],
                            'score': f['anomaly_score']
                        }
                        for f in files[:5]  # Top 5 examples
                    ]
                }
                for anomaly_type, files in anomaly_types.items()
            },
            'top_anomalies': [
                {
                    'filepath': a['filepath'],
                    'filename': a['filename'],
                    'directory': a['directory'],
                    'size_kb': a['size_kb'],
                    'depth': a['depth'],
                    'severity': a['severity'],
                    'anomaly_score': a['anomaly_score'],
                    'reasons': a['reasons']
                }
                for a in anomalies[:20]  # Top 20 most anomalous
            ],
            'recommendations': self._generate_recommendations(anomalies, anomaly_types)
        }

        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] Report saved to: {output_path}")

        return report

    def _generate_recommendations(self, anomalies, anomaly_types):
        """Generate actionable recommendations based on detected anomalies"""
        recommendations = []

        if 'EMPTY_OR_TINY_FILE' in anomaly_types:
            count = len(anomaly_types['EMPTY_OR_TINY_FILE'])
            recommendations.append({
                'priority': 'HIGH',
                'issue': f'{count} empty or corrupted files detected',
                'action': 'Review and delete corrupted files. Re-download from source if possible.',
                'affected_files': count
            })

        if 'SUSPICIOUSLY_SMALL' in anomaly_types:
            count = len(anomaly_types['SUSPICIOUSLY_SMALL'])
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': f'{count} files are suspiciously small (<10KB)',
                'action': 'Verify image quality. May indicate failed downloads or placeholder images.',
                'affected_files': count
            })

        if 'SUSPICIOUSLY_LARGE' in anomaly_types:
            count = len(anomaly_types['SUSPICIOUSLY_LARGE'])
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': f'{count} files are unusually large (>5MB)',
                'action': 'Review for incorrect file types or unnecessary high resolution.',
                'affected_files': count
            })

        if 'WRONG_DIRECTORY_LEVEL' in anomaly_types:
            count = len(anomaly_types['WRONG_DIRECTORY_LEVEL'])
            recommendations.append({
                'priority': 'HIGH',
                'issue': f'{count} files in incorrect directory structure',
                'action': 'Reorganize files to match expected directory hierarchy.',
                'affected_files': count
            })

        if 'INVALID_NAMING_PATTERN' in anomaly_types:
            count = len(anomaly_types['INVALID_NAMING_PATTERN'])
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': f'{count} files with non-standard naming',
                'action': 'Rename files to follow standard pattern: P{1,2,3}_StoreName_YYYYMMDD_HHMMSS.jpg',
                'affected_files': count
            })

        if not recommendations:
            recommendations.append({
                'priority': 'INFO',
                'issue': 'No critical issues detected',
                'action': 'Directory structure appears healthy. Continue regular monitoring.',
                'affected_files': 0
            })

        return recommendations

    def print_summary(self, report):
        """Print human-readable summary to console"""
        print("\n" + "="*80)
        print("ANOMALY DETECTION REPORT SUMMARY")
        print("="*80)
        print(f"\nGenerated: {report['metadata']['generated_at']}")
        print(f"Total Files Analyzed: {report['metadata']['total_files_analyzed']}")
        print(f"Anomalies Detected: {report['metadata']['anomalies_detected']}")
        print(f"Contamination Rate: {report['metadata']['contamination_rate']:.2f}%")

        print("\n" + "-"*80)
        print("FILE STATISTICS")
        print("-"*80)
        stats = report['statistics']['all_files']
        print(f"Total Size: {stats['total_size_mb']:.2f} MB")
        print(f"Mean File Size: {stats['mean_size_kb']:.2f} KB")
        print(f"Median File Size: {stats['median_size_kb']:.2f} KB")
        print(f"Size Range: {stats['min_size_kb']:.2f} - {stats['max_size_kb']:.2f} KB")

        print("\n" + "-"*80)
        print("ANOMALY BREAKDOWN")
        print("-"*80)
        for anomaly_type, data in report['anomaly_breakdown'].items():
            print(f"\n{anomaly_type}:")
            print(f"  Count: {data['count']} ({data['percentage']:.1f}%)")
            if data['examples']:
                print(f"  Example: {data['examples'][0]['filepath']}")

        print("\n" + "-"*80)
        print("TOP 10 MOST ANOMALOUS FILES")
        print("-"*80)
        for i, anomaly in enumerate(report['top_anomalies'][:10], 1):
            print(f"\n{i}. {anomaly['filename']}")
            print(f"   Path: {anomaly['directory']}")
            print(f"   Size: {anomaly['size_kb']:.2f} KB | Severity: {anomaly['severity']}")
            print(f"   Score: {anomaly['anomaly_score']:.4f}")
            print(f"   Reasons: {', '.join(anomaly['reasons'])}")

        print("\n" + "-"*80)
        print("RECOMMENDATIONS")
        print("-"*80)
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"\n{i}. [{rec['priority']}] {rec['issue']}")
            print(f"   Action: {rec['action']}")
            print(f"   Affected Files: {rec['affected_files']}")

        print("\n" + "="*80)
        print("END OF REPORT")
        print("="*80 + "\n")


def main():
    """Main execution function"""
    print("="*80)
    print("AI/ML ANOMALY DETECTION SYSTEM")
    print("Isolation Forest-based File Structure Analysis")
    print("="*80 + "\n")

    # Configuration
    BASE_PATHS = [
        '/home/marcelo/sistemas/captura_cameras/cameras',
        '/home/marcelo/sistemas/captura_cameras_debug/imagens_simples'
    ]

    CONTAMINATION = 0.1  # Expect 10% anomalies
    OUTPUT_REPORT = '/home/marcelo/sistemas/anomaly_detection_report.json'

    # Initialize detector
    detector = FileAnomalyDetector(contamination=CONTAMINATION)

    # Collect metadata from all paths
    all_metadata = []
    for base_path in BASE_PATHS:
        if Path(base_path).exists():
            metadata = detector.collect_file_metadata(base_path)
            all_metadata.extend(metadata)
        else:
            print(f"[WARNING] Path not found: {base_path}")

    if not all_metadata:
        print("[ERROR] No files found to analyze!")
        sys.exit(1)

    print(f"\n[INFO] Total files collected: {len(all_metadata)}")

    # Extract features
    features = detector.extract_features(all_metadata)

    # Detect anomalies
    predictions = detector.fit_predict(features)

    # Generate and save report
    report = detector.generate_report(OUTPUT_REPORT)

    # Print summary
    detector.print_summary(report)

    print(f"\n[SUCCESS] Full report saved to: {OUTPUT_REPORT}")
    print("[INFO] Analysis complete!\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
