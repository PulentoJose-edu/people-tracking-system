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
                "flow_analysis": self._analyze_flow_patterns(df),
                "dwell_time_analysis": self._analyze_dwell_times(df),
                "demographic_analysis": self._analyze_demographics(df)  # Nuevo análisis demográfico
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
    
    def _analyze_dwell_times(self, df: pd.DataFrame) -> Dict:
        """
        Analiza tiempos de permanencia usando eventos entry/exit
        """
        dwell_data = {
            "by_zone": {},
            "by_person": {},
            "summary": {}
        }
        
        # Verificar si tenemos eventos de salida
        has_exits = 'exit' in df['event'].values if 'event' in df.columns else False
        
        if not has_exits:
            # Si no hay eventos de salida, usar método anterior
            return self._analyze_dwell_times_fallback(df)
        
        # Procesar cada persona individualmente
        for person_id in df['person_tracker_id'].unique():
            person_data = df[df['person_tracker_id'] == person_id].sort_values('timestamp_seconds')
            person_dwell_times = []
            
            # Agrupar por zona para esta persona
            for zone_id in person_data['zone_id'].unique():
                zone_events = person_data[person_data['zone_id'] == zone_id].sort_values('timestamp_seconds')
                
                # Buscar pares entry-exit
                entry_times = zone_events[zone_events['event'] == 'entry']['timestamp_seconds'].tolist()
                exit_times = zone_events[zone_events['event'] == 'exit']['timestamp_seconds'].tolist()
                
                # Calcular tiempos de permanencia para cada sesión en la zona
                zone_dwell_times = []
                for i, entry_time in enumerate(entry_times):
                    # Buscar la salida correspondiente
                    matching_exits = [exit_time for exit_time in exit_times if exit_time > entry_time]
                    if matching_exits:
                        exit_time = min(matching_exits)  # La salida más próxima
                        dwell_time = exit_time - entry_time
                        zone_dwell_times.append(dwell_time)
                        person_dwell_times.append(dwell_time)
                        
                        # Remover esta salida para evitar reutilización
                        exit_times.remove(exit_time)
                
                # Estadísticas por zona
                if zone_dwell_times:
                    zone_key = f"zone_{zone_id}"
                    if zone_key not in dwell_data["by_zone"]:
                        dwell_data["by_zone"][zone_key] = []
                    dwell_data["by_zone"][zone_key].extend(zone_dwell_times)
            
            # Estadísticas por persona
            if person_dwell_times:
                dwell_data["by_person"][f"person_{person_id}"] = {
                    "total_dwell_time": sum(person_dwell_times),
                    "average_dwell_time": np.mean(person_dwell_times),
                    "visits_count": len(person_dwell_times),
                    "max_dwell_time": max(person_dwell_times),
                    "min_dwell_time": min(person_dwell_times)
                }
        
        # Calcular estadísticas de resumen por zona
        for zone_key, times in dwell_data["by_zone"].items():
            if times:
                dwell_data["by_zone"][zone_key] = {
                    "raw_times": times,
                    "average_dwell_time": np.mean(times),
                    "median_dwell_time": np.median(times),
                    "total_visits": len(times),
                    "max_dwell_time": max(times),
                    "min_dwell_time": min(times),
                    "std_dwell_time": np.std(times)
                }
        
        # Estadísticas generales
        all_dwell_times = []
        for zone_data in dwell_data["by_zone"].values():
            if isinstance(zone_data, dict) and "raw_times" in zone_data:
                all_dwell_times.extend(zone_data["raw_times"])
        
        if all_dwell_times:
            dwell_data["summary"] = {
                "overall_average": np.mean(all_dwell_times),
                "overall_median": np.median(all_dwell_times),
                "total_measured_visits": len(all_dwell_times),
                "longest_stay": max(all_dwell_times),
                "shortest_stay": min(all_dwell_times),
                "distribution": {
                    "under_10s": len([t for t in all_dwell_times if t < 10]),
                    "10_30s": len([t for t in all_dwell_times if 10 <= t < 30]),
                    "30_60s": len([t for t in all_dwell_times if 30 <= t < 60]),
                    "over_60s": len([t for t in all_dwell_times if t >= 60])
                }
            }
        
        return dwell_data
    
    def _analyze_dwell_times_fallback(self, df: pd.DataFrame) -> Dict:
        """
        Método de respaldo para calcular tiempo de permanencia sin eventos exit
        """
        dwell_data = {
            "by_zone": {},
            "by_person": {},
            "summary": {},
            "note": "Calculated using first-last detection method (less accurate)"
        }
        
        # Usar el método anterior basado en primera-última detección
        for person_id in df['person_tracker_id'].unique():
            person_data = df[df['person_tracker_id'] == person_id]
            
            for zone_id in person_data['zone_id'].unique():
                zone_person_data = person_data[person_data['zone_id'] == zone_id]
                
                if len(zone_person_data) > 1:
                    dwell_time = zone_person_data['timestamp_seconds'].max() - zone_person_data['timestamp_seconds'].min()
                    
                    zone_key = f"zone_{zone_id}"
                    if zone_key not in dwell_data["by_zone"]:
                        dwell_data["by_zone"][zone_key] = []
                    dwell_data["by_zone"][zone_key].append(dwell_time)
        
        # Calcular estadísticas
        for zone_key, times in dwell_data["by_zone"].items():
            if times:
                dwell_data["by_zone"][zone_key] = {
                    "raw_times": times,
                    "average_dwell_time": np.mean(times),
                    "median_dwell_time": np.median(times),
                    "total_visits": len(times),
                    "max_dwell_time": max(times),
                    "min_dwell_time": min(times)
                }
        
        return dwell_data
    
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
                },
                "dwell_time_distribution": {
                    "type": "bar",
                    "data": {
                        "labels": ["< 10s", "10-30s", "30-60s", "> 60s"],
                        "values": []
                    }
                },
                "average_dwell_by_zone": {
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
        
        # Preparar datos de tiempo de permanencia
        if "dwell_time_analysis" in analysis and "summary" in analysis["dwell_time_analysis"]:
            dwell_summary = analysis["dwell_time_analysis"]["summary"]
            
            # Distribución de tiempos
            if "distribution" in dwell_summary:
                dist = dwell_summary["distribution"]
                viz_data["charts"]["dwell_time_distribution"]["data"]["values"] = [
                    dist.get("under_10s", 0),
                    dist.get("10_30s", 0),
                    dist.get("30_60s", 0),
                    dist.get("over_60s", 0)
                ]
            
            # Tiempo promedio por zona
            if "by_zone" in analysis["dwell_time_analysis"]:
                for zone_key, zone_data in analysis["dwell_time_analysis"]["by_zone"].items():
                    if isinstance(zone_data, dict) and "average_dwell_time" in zone_data:
                        viz_data["charts"]["average_dwell_by_zone"]["data"]["labels"].append(zone_key)
                        viz_data["charts"]["average_dwell_by_zone"]["data"]["values"].append(
                            round(zone_data["average_dwell_time"], 2)
                        )
            
            # Añadir métricas de tiempo de permanencia a las tarjetas de resumen
            if "overall_average" in dwell_summary:
                viz_data["summary_cards"]["avg_dwell_time"] = f"{dwell_summary['overall_average']:.1f}s"
                viz_data["summary_cards"]["total_visits"] = dwell_summary.get("total_measured_visits", 0)
        
        return viz_data
    
    def _analyze_demographics(self, df: pd.DataFrame) -> Dict:
        """
        Analiza atributos demográficos (género y edad) de las personas detectadas
        """
        demographic_data = {
            "gender_distribution": {},
            "age_distribution": {},
            "gender_by_zone": {},
            "age_by_zone": {},
            "summary": {},
            "has_data": False
        }
        
        # Verificar si existen columnas demográficas
        if 'gender' not in df.columns or 'age' not in df.columns:
            demographic_data["note"] = "No demographic data available in this analysis"
            return demographic_data
        
        # Filtrar solo personas con datos demográficos válidos (no Desconocido)
        df_valid = df[
            (df['gender'] != 'Desconocido') & 
            (df['age'] != 'Desconocido')
        ].copy()
        
        if df_valid.empty:
            demographic_data["note"] = "No valid demographic data found"
            return demographic_data
        
        demographic_data["has_data"] = True
        
        # 1. Distribución por género (usando solo una entrada por persona)
        df_unique_persons = df_valid.drop_duplicates(subset=['person_tracker_id'])
        
        gender_counts = df_unique_persons['gender'].value_counts().to_dict()
        total_persons = len(df_unique_persons)
        
        demographic_data["gender_distribution"] = {
            "counts": gender_counts,
            "percentages": {
                gender: round((count / total_persons) * 100, 2) 
                for gender, count in gender_counts.items()
            },
            "total_classified": total_persons
        }
        
        # 2. Distribución por edad
        age_counts = df_unique_persons['age'].value_counts().to_dict()
        
        demographic_data["age_distribution"] = {
            "counts": age_counts,
            "percentages": {
                age: round((count / total_persons) * 100, 2) 
                for age, count in age_counts.items()
            },
            "total_classified": total_persons
        }
        
        # 3. Distribución por zona
        for zone_id in df_valid['zone_id'].unique():
            zone_data = df_valid[df_valid['zone_id'] == zone_id]
            zone_unique = zone_data.drop_duplicates(subset=['person_tracker_id'])
            
            zone_key = f"zone_{zone_id}"
            
            # Género por zona
            zone_gender = zone_unique['gender'].value_counts().to_dict()
            zone_total = len(zone_unique)
            
            demographic_data["gender_by_zone"][zone_key] = {
                "counts": zone_gender,
                "percentages": {
                    gender: round((count / zone_total) * 100, 2) 
                    for gender, count in zone_gender.items()
                },
                "total": zone_total
            }
            
            # Edad por zona
            zone_age = zone_unique['age'].value_counts().to_dict()
            
            demographic_data["age_by_zone"][zone_key] = {
                "counts": zone_age,
                "percentages": {
                    age: round((count / zone_total) * 100, 2) 
                    for age, count in zone_age.items()
                },
                "total": zone_total
            }
        
        # 4. Resumen con estadísticas clave
        # Calcular confianza promedio
        avg_gender_conf = df_valid['gender_confidence'].mean() if 'gender_confidence' in df_valid.columns else 0
        avg_age_conf = df_valid['age_confidence'].mean() if 'age_confidence' in df_valid.columns else 0
        
        demographic_data["summary"] = {
            "total_persons_classified": total_persons,
            "total_detections_with_demographics": len(df_valid),
            "classification_rate": round((total_persons / df['person_tracker_id'].nunique()) * 100, 2),
            "average_gender_confidence": round(avg_gender_conf, 3),
            "average_age_confidence": round(avg_age_conf, 3),
            "most_common_gender": max(gender_counts, key=gender_counts.get) if gender_counts else "N/A",
            "most_common_age": max(age_counts, key=age_counts.get) if age_counts else "N/A"
        }
        
        return demographic_data

# Instancia global del procesador
analytics_processor = AnalyticsProcessor()
