"""
YouTube-Integration für die Kommentaranalyse (05_kommentaranalyse_deutsch.py)
Verarbeitet YouTube-Video-Informationen für Kommentaranalysen
"""
import streamlit as st
import pandas as pd
import re
from pathlib import Path

class KommentaranalyseYouTube:
    """
    Verarbeitet YouTube-Informationen für die Kommentaranalyse
    """
    
    def __init__(self):
        """
        Initialisiert den YouTube-Manager
        """
        # Prüfe, ob yt-dlp verfügbar ist
        try:
            from yt_dlp import YoutubeDL
            self.yt_dlp_available = True
            self.YoutubeDL = YoutubeDL
        except ImportError:
            self.yt_dlp_available = False
            self.YoutubeDL = None
            st.warning("yt-dlp ist nicht installiert. YouTube-Informationen können nicht abgerufen werden.")
    
    def get_video_info(self, video_id):
        """
        Ruft Informationen über ein YouTube-Video basierend auf seiner ID ab
        
        Args:
            video_id: YouTube-Video-ID
            
        Returns:
            dict: Video-Informationen oder None bei Fehler
        """
        if not self.yt_dlp_available or not video_id:
            return None
            
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            # yt-dlp configuration
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with self.YoutubeDL(ydl_opts) as ydl:
                # Get video information without download
                info = ydl.extract_info(url, download=False)
                
                # Convert information to usable dictionary
                video_info = {
                    "title": info.get('title', 'Title not available'),
                    "views": info.get('view_count', 'Views not available'),
                    "publish_date": info.get('upload_date', 'Date not available'),
                    "length": info.get('duration', 'Length not available'),
                    "author": info.get('uploader', 'Author not available'),
                    "description": info.get('description', 'Description not available')
                }
                
                # Format upload date
                if isinstance(video_info['publish_date'], str) and len(video_info['publish_date']) == 8:
                    date_str = video_info['publish_date']
                    try:
                        video_info['publish_date'] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    except:
                        pass
                
                return video_info
        except Exception as e:
            st.warning(f"Konnte YouTube-Daten nicht abrufen: {e}")
            return None
    
    def format_duration(self, seconds):
        """
        Formatiert Sekunden in ein lesbares Zeitformat
        
        Args:
            seconds: Anzahl der Sekunden
            
        Returns:
            str: Formatierte Zeit (HH:MM:SS oder MM:SS)
        """
        if not isinstance(seconds, int):
            return str(seconds)
        
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
        
    def format_views(self, views):
        """
        Formatiert Aufrufe mit Kommas für bessere Lesbarkeit
        
        Args:
            views: Anzahl der Aufrufe
            
        Returns:
            str: Formatierte Aufrufe
        """
        if isinstance(views, int):
            return f"{views:,}"
        else:
            return str(views)
    
    def display_youtube_info(self, video_id):
        """
        Zeigt YouTube-Video-Informationen an
        
        Args:
            video_id: YouTube-Video-ID
        """
        if not video_id:
            return
            
        st.success(f"🎬 YouTube Video-ID: {video_id}")
        
        # Create expandable section for YouTube Info
        with st.expander("YouTube Video Informationen", expanded=True):
            # Display embedded YouTube player
            st.subheader("YouTube Video")
            st.markdown(f"""
            <iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" 
            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; 
            gyroscope; picture-in-picture" allowfullscreen></iframe>
            """, unsafe_allow_html=True)
            
            # Fetch and display video information
            with st.spinner("Rufe Informationen vom YouTube-Video ab..."):
                video_info = self.get_video_info(video_id)
            
            if video_info:
                # Create two columns layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Allgemeine Informationen")
                    st.markdown(f"**Titel:** {video_info['title']}")
                    st.markdown(f"**Autor:** {video_info['author']}")
                    
                    # Format views with commas for better readability
                    formatted_views = self.format_views(video_info['views'])
                    st.markdown(f"**Aufrufe:** {formatted_views}")
                    
                    st.markdown(f"**Veröffentlicht am:** {video_info['publish_date']}")
                    
                    # Convert seconds to readable format
                    formatted_duration = self.format_duration(video_info['length'])
                    st.markdown(f"**Dauer:** {formatted_duration}")
                
                with col2:
                    st.markdown("### Beschreibung")
                    if isinstance(video_info['description'], str) and len(video_info['description']) > 300:
                        st.markdown(f"{video_info['description'][:300]}...")
                        
                        # Use session state for toggle
                        toggle_key = f"show_full_description_{video_id}"
                        if toggle_key not in st.session_state:
                            st.session_state[toggle_key] = False
                        
                        if st.button("Vollständige Beschreibung anzeigen/verbergen", key=f"desc_button_{video_id}"):
                            st.session_state[toggle_key] = not st.session_state[toggle_key]
                        
                        if st.session_state[toggle_key]:
                            st.markdown("---")
                            st.markdown(video_info['description'])
                    else:
                        st.markdown(f"{video_info['description']}")
                
                # Option to download the information as CSV
                video_info_df = pd.DataFrame([video_info])
                csv = video_info_df.to_csv(index=False)
                st.download_button(
                    label="Video-Informationen als CSV herunterladen",
                    data=csv,
                    file_name=f"{video_id}_info.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Konnte keine Informationen von YouTube abrufen.")
    
    def extract_video_id(self, filename):
        """
        Extrahiert die YouTube-Video-ID aus dem Dateinamen
        
        Args:
            filename: Name der Datei
            
        Returns:
            str: YouTube-Video-ID oder None
        """
        # Pattern to match YouTube ID format in filenames like "20240618_87TYPn6gbwA_title.csv"
        pattern = r'_([a-zA-Z0-9_-]{11})_'
        match = re.search(pattern, filename)
        if match:
            return match.group(1)
        
        # Alternative pattern
        alt_pattern = r'_([a-zA-Z0-9_-]{11})'
        alt_match = re.search(alt_pattern, filename)
        if alt_match:
            return alt_match.group(1)
        
        return None