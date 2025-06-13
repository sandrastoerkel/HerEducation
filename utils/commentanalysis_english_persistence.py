import streamlit as st
import pandas as pd
import json
import pickle
import traceback
from datetime import datetime
from pathlib import Path
import re

class CommentAnalysisPersistence:
    """
    Class for handling persistent storage of analysis results
    """
    
    def __init__(self, results_dir):
        """
        Initialize with the directory for saved results
        
        Args:
            results_dir: Path object for the results directory
        """
        self.results_dir = results_dir
        
        # Create directory if it doesn't exist
        try:
            self.results_dir.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            st.error(f"Error creating directory: {e}")
            # Fallback to Desktop
            self.results_dir = Path.home() / "Desktop" / "StreamlitApp_Results"
            self.results_dir.mkdir(exist_ok=True, parents=True)
            st.warning(f"Using fallback directory: {self.results_dir}")
    
    def create_safe_filename(self, filename):
        """
        Creates a safe filename from any input filename
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename without problematic characters
        """
        # Extract only filename without path and extension
        base_filename = Path(filename).stem
        
        # Remove all problematic characters (EXACT same rule everywhere)
        safe_filename = re.sub(r'[^\w\-\.]', '_', base_filename)
        
        return safe_filename
    
    def save_analysis_results(self, filename, df, additional_data=None):
        """
        Saves analysis results with full consistency checking
        
        Args:
            filename: Original filename
            df: DataFrame with analysis results
            additional_data: Dictionary with additional data (e.g., models, topic info)
            
        Returns:
            Boolean indicating success
        """
        try:
            safe_filename = self.create_safe_filename(filename)
            
            st.info(f"💾 Saving analysis...")
            st.info(f"   Original name: {filename}")
            st.info(f"   Safe name: {safe_filename}")
            st.info(f"   Directory: {self.results_dir}")
            
            # Define all file paths
            df_pkl_path = self.results_dir / f"{safe_filename}_results.pkl"
            df_csv_path = self.results_dir / f"{safe_filename}_results.csv"
            additional_path = self.results_dir / f"{safe_filename}_additional.pkl"
            meta_path = self.results_dir / f"{safe_filename}_meta.json"
            
            # 1. Save DataFrame (try pickle, fallback to CSV)
            success_df_save = False
            try:
                df.to_pickle(df_pkl_path)
                st.success(f"✅ DataFrame saved as pickle")
                success_df_save = True
                saved_df_path = df_pkl_path
            except Exception as e:
                st.warning(f"⚠️ Pickle failed ({e}), trying CSV...")
                try:
                    df.to_csv(df_csv_path, index=False, encoding='utf-8')
                    st.success(f"✅ DataFrame saved as CSV")
                    success_df_save = True
                    saved_df_path = df_csv_path
                except Exception as csv_e:
                    st.error(f"❌ CSV save also failed: {csv_e}")
                    return False
            
            # 2. Save additional data
            has_additional = False
            if additional_data:
                try:
                    with open(additional_path, 'wb') as f:
                        pickle.dump(additional_data, f)
                    st.success(f"✅ Additional data saved")
                    has_additional = True
                except Exception as e:
                    st.warning(f"⚠️ Additional data not saved: {e}")
            
            # 3. Save metadata (IMPORTANT: includes all info for retrieval)
            metadata = {
                'original_filename': filename,  # Original filename
                'safe_filename': safe_filename,  # Processed safe name
                'analysis_date': datetime.now().isoformat(),
                'num_comments': len(df),
                'columns': list(df.columns),
                'has_additional_data': has_additional,
                'saved_files': {
                    'dataframe': str(saved_df_path),
                    'additional': str(additional_path) if has_additional else None,
                    'metadata': str(meta_path)
                }
            }
            
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            st.success(f"✅ Metadata saved: {meta_path}")
            
            # Verify saved files
            existing_files = []
            for path in [saved_df_path, meta_path]:
                if path.exists():
                    existing_files.append(f"   ✓ {path.name} ({path.stat().st_size} bytes)")
            
            if additional_path.exists():
                existing_files.append(f"   ✓ {additional_path.name} ({additional_path.stat().st_size} bytes)")
            
            st.success(f"🎉 Save successful! Files:")
            for file_info in existing_files:
                st.text(file_info)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error saving: {e}")
            st.error(traceback.format_exc())
            return False
    
    def load_analysis_results(self, filename):
        """
        Loads saved analysis results
        
        Args:
            filename: Original filename
            
        Returns:
            Tuple of (DataFrame, additional_data, metadata)
        """
        try:
            safe_filename = self.create_safe_filename(filename)
            
            st.info(f"📂 Loading analysis...")
            st.info(f"   Original name: {filename}")
            st.info(f"   Safe name: {safe_filename}")
            st.info(f"   Directory: {self.results_dir}")
            
            # Define all file paths (EXACT same logic as when saving)
            df_pkl_path = self.results_dir / f"{safe_filename}_results.pkl"
            df_csv_path = self.results_dir / f"{safe_filename}_results.csv"
            additional_path = self.results_dir / f"{safe_filename}_additional.pkl"
            meta_path = self.results_dir / f"{safe_filename}_meta.json"
            
            # Check if metadata exists
            if not meta_path.exists():
                st.error(f"❌ Metadata not found: {meta_path}")
                return None, None, None
            
            # Load metadata first
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            st.success(f"✅ Metadata loaded")
            
            # Load DataFrame (try pickle first, then CSV)
            df = None
            if df_pkl_path.exists():
                try:
                    df = pd.read_pickle(df_pkl_path)
                    st.success(f"✅ DataFrame loaded from pickle")
                except Exception as e:
                    st.warning(f"⚠️ Pickle loading failed: {e}")
            
            if df is None and df_csv_path.exists():
                try:
                    df = pd.read_csv(df_csv_path, encoding='utf-8')
                    st.success(f"✅ DataFrame loaded from CSV")
                except Exception as e:
                    st.error(f"❌ CSV loading failed: {e}")
                    return None, None, metadata
            
            if df is None:
                st.error(f"❌ No DataFrame file found")
                return None, None, metadata
            
            # Load additional data if available
            additional_data = None
            if additional_path.exists():
                try:
                    with open(additional_path, 'rb') as f:
                        additional_data = pickle.load(f)
                    st.success(f"✅ Additional data loaded")
                except Exception as e:
                    st.warning(f"⚠️ Additional data not loaded: {e}")
            
            st.success(f"🎉 Loading successful!")
            return df, additional_data, metadata
            
        except Exception as e:
            st.error(f"❌ Error loading: {e}")
            st.error(traceback.format_exc())
            return None, None, None
    
    def get_available_analyses(self):
        """
        Returns a list of available saved analyses
        
        Returns:
            List of dictionaries with analysis information
        """
        try:
            analyses = []
            meta_files = list(self.results_dir.glob("*_meta.json"))
            
            for meta_file in meta_files:
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Use original_filename from metadata
                    original_filename = metadata.get('original_filename', 'Unknown')
                    safe_filename = metadata.get('safe_filename', 'Unknown')
                    
                    analyses.append({
                        'filename': original_filename,
                        'safe_filename': safe_filename,
                        'date': metadata.get('analysis_date', datetime.now().isoformat()),
                        'num_comments': metadata.get('num_comments', 0),
                        'meta_file': str(meta_file)
                    })
                    
                except Exception as e:
                    continue
            
            return analyses
            
        except Exception as e:
            return []
    
    def test_save_load_consistency(self):
        """
        Tests the consistency between Save and Load operations
        """
        st.subheader("🧪 Test Save/Load Consistency")
        
        if st.button("Run Consistency Test"):
            # Create test data
            test_filename = "test_file_123!@#.csv"  # Problematic characters
            test_df = pd.DataFrame({
                'comment_text': ['Test 1', 'Test 2', 'Test 3'],
                'sentiment': ['positive', 'negative', 'neutral'],
                'topic': [0, 1, 2]
            })
            test_additional = {'model_info': 'test_model', 'topics': [0, 1, 2]}
            
            st.info(f"Test filename: {test_filename}")
            
            # 1. Save
            st.info("1. Saving test data...")
            save_success = self.save_analysis_results(test_filename, test_df, test_additional)
            
            if save_success:
                # 2. Check available analyses
                st.info("2. Searching for saved analyses...")
                available = self.get_available_analyses()
                
                found_test = False
                for analysis in available:
                    if analysis['filename'] == test_filename:
                        found_test = True
                        st.success(f"✅ Test analysis found in list: {analysis['filename']}")
                        break
                
                if not found_test:
                    st.error("❌ Test analysis NOT found in list!")
                    st.json(available)
                
                # 3. Load
                st.info("3. Loading test data...")
                loaded_df, loaded_additional, loaded_metadata = self.load_analysis_results(test_filename)
                
                if loaded_df is not None:
                    st.success("✅ Loading successful!")
                    st.info("Comparing data:")
                    
                    # Compare DataFrame
                    if test_df.equals(loaded_df):
                        st.success("✅ DataFrame identical")
                    else:
                        st.error("❌ DataFrame different")
                        st.write("Original:", test_df)
                        st.write("Loaded:", loaded_df)
                    
                    # Compare Additional Data
                    if test_additional == loaded_additional:
                        st.success("✅ Additional data identical")
                    else:
                        st.error("❌ Additional data different")
                        st.write("Original:", test_additional)
                        st.write("Loaded:", loaded_additional)
                else:
                    st.error("❌ Loading failed!")
            else:
                st.error("❌ Saving failed!")