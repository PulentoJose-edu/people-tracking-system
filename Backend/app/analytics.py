import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

class AnalyticsProcessor:
    """
    Clase para procesar y analizar datos de seguimiento de personas
    """
    
    def __init__(self):
        self.current_session_data = {}
        
    def process_csv_data(self, csv_path: str) -> Dict:
        """
        Procesa un archivo CSV y retorna estadísticas analizadas
        """
        try:
            # Leer CSV
            df = pd.read_csv(csv_path)
            
            if df.empty:
                return {"error": "CSV file is empty"}
            
            # Análisis básico
            analysis = {
                "summary": self._generate_summary(df),
                "zone_analysis": self._analyze_zones(df),
                "temporal_analysis": self._analyze_temporal_patterns(df),
                "flow_analysis": self._analyze_flow_patterns(df)
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Error processing CSV: {str(e)}"}
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict:
        """
        Genera resumen estadístico general
        """
        return {
            "total_detections": len(df),
            "unique_persons": df['person_tracker_id'].nunique(),
            "zones_count": df['zone_id'].nunique(),
            "duration_seconds": df['timestamp_seconds'].max() - df['timestamp_seconds'].min(),
            "total_frames": df['frame'].max() if not df.empty else 0,
            "detection_rate": len(df) / (df['frame'].max() or 1),
            "zones_detected": sorted(df['zone_id'].unique().tolist())
        }
    
    def _analyze_zones(self, df: pd.DataFrame) -> Dict:
        """
        Analiza actividad por zona
        """
        zone_stats = {}
        
        for zone_id in df['zone_id'].unique():
            zone_data = df[df['zone_id'] == zone_id]
            
            zone_stats[f"zone_{zone_id}"] = {
                "total_entries": len(zone_data),
                "unique_persons": zone_data['person_tracker_id'].nunique(),
                "first_detection": zone_data['timestamp_seconds'].min(),
                "last_detection": zone_data['timestamp_seconds'].max(),
                "activity_duration": zone_data['timestamp_seconds'].max() - zone_data['timestamp_seconds'].min(),
                "peak_frame": zone_data.groupby('frame').size().idxmax() if not zone_data.empty else 0,
                "entries_timeline": zone_data.groupby('timestamp_seconds').size().to_dict()
            }
        
        return zone_stats
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analiza patrones temporales
        """
        # Agrupa por segundos
        temporal_data = df.groupby('timestamp_seconds').agg({
            'person_tracker_id': 'count',
            'zone_id': lambda x: len(x.unique())
        }).rename(columns={
            'person_tracker_id': 'detections_per_second',
            'zone_id': 'active_zones'
        })
        
        return {
            "timeline": temporal_data.to_dict('index'),
            "peak_activity": {
                "timestamp": temporal_data['detections_per_second'].idxmax(),
                "detections": temporal_data['detections_per_second'].max()
            },
            "average_detections_per_second": temporal_data['detections_per_second'].mean(),
            "activity_distribution": temporal_data['detections_per_second'].describe().to_dict()
        }
    
    def _analyze_flow_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analiza patrones de flujo entre zonas
        """
        flow_data = {}
        
        # Analizar movimiento de personas entre zonas
        for person_id in df['person_tracker_id'].unique():
            person_data = df[df['person_tracker_id'] == person_id].sort_values('timestamp_seconds')
            zones_visited = person_data['zone_id'].tolist()
            
            # Contar transiciones entre zonas
            for i in range(len(zones_visited) - 1):
                from_zone = f"zone_{zones_visited[i]}"
                to_zone = f"zone_{zones_visited[i + 1]}"
                
                if from_zone != to_zone:  # Solo contar transiciones reales
                    transition_key = f"{from_zone}_to_{to_zone}"
                    flow_data[transition_key] = flow_data.get(transition_key, 0) + 1
        
        return {
            "zone_transitions": flow_data,
            "most_common_transition": max(flow_data.items(), key=lambda x: x[1]) if flow_data else None,
            "total_transitions": sum(flow_data.values())
        }
    
    def generate_visualization_data(self, analysis: Dict) -> Dict:
        """
        Prepara datos optimizados para visualización
        """
        viz_data = {
            "charts": {
                "zone_distribution": {
                    "type": "pie",
                    "data": {
                        "labels": [],
                        "values": []
                    }
                },
                "temporal_activity": {
                    "type": "line",
                    "data": {
                        "x": [],
                        "y": []
                    }
                },
                "zone_comparison": {
                    "type": "bar",
                    "data": {
                        "labels": [],
                        "values": []
                    }
                }
            },
            "summary_cards": {
                "total_detections": analysis["summary"]["total_detections"],
                "unique_persons": analysis["summary"]["unique_persons"],
                "duration": f"{analysis['summary']['duration_seconds']:.1f}s",
                "zones_active": len(analysis["summary"]["zones_detected"])
            }
        }
        
        # Preparar datos para gráfico de distribución por zonas
        for zone, data in analysis["zone_analysis"].items():
            viz_data["charts"]["zone_distribution"]["data"]["labels"].append(zone)
            viz_data["charts"]["zone_distribution"]["data"]["values"].append(data["total_entries"])
            
            viz_data["charts"]["zone_comparison"]["data"]["labels"].append(zone)
            viz_data["charts"]["zone_comparison"]["data"]["values"].append(data["unique_persons"])
        
        # Preparar datos temporales
        timeline = analysis["temporal_analysis"]["timeline"]
        for timestamp, data in timeline.items():
            viz_data["charts"]["temporal_activity"]["data"]["x"].append(timestamp)
            viz_data["charts"]["temporal_activity"]["data"]["y"].append(data["detections_per_second"])
        
        return viz_data

# Instancia global del procesador
analytics_processor = AnalyticsProcessor()
