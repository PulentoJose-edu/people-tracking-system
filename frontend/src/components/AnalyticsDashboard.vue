<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>📊 Analytics Dashboard</h1>
      <div class="controls">
        <select v-model="selectedTaskId" @change="loadTaskData" class="task-selector">
          <option value="">Seleccionar tarea...</option>
          <option v-for="task in availableTasks" :key="task.task_id" :value="task.task_id">
            {{ task.task_id }} ({{ formatDate(task.timestamp) }})
          </option>
        </select>
        <button @click="refreshData" class="refresh-btn" :disabled="loading">
          {{ loading ? '🔄' : '↻' }} Actualizar
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Cargando análisis...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>❌ {{ error }}</p>
    </div>

    <div v-else-if="analysisData" class="dashboard-content">
      <!-- Tarjetas de resumen -->
      <div class="summary-cards">
        <div class="card">
          <div class="card-icon">👥</div>
          <div class="card-content">
            <h3>{{ analysisData.summary.total_detections }}</h3>
            <p>Total Detecciones</p>
          </div>
        </div>
        <div class="card">
          <div class="card-icon">🚶</div>
          <div class="card-content">
            <h3>{{ analysisData.summary.unique_persons }}</h3>
            <p>Personas Únicas</p>
          </div>
        </div>
        <div class="card">
          <div class="card-icon">⏱️</div>
          <div class="card-content">
            <h3>{{ analysisData.summary.duration_seconds.toFixed(1) }}s</h3>
            <p>Duración</p>
          </div>
        </div>
        <div class="card">
          <div class="card-icon">📍</div>
          <div class="card-content">
            <h3>{{ analysisData.summary.zones_count }}</h3>
            <p>Zonas Activas</p>
          </div>
        </div>
      </div>

      <!-- Gráficos -->
      <div class="charts-grid">
        <div class="chart-container">
          <h3>📊 Distribución por Zonas</h3>
          <div class="chart-wrapper">
            <canvas ref="zoneChart"></canvas>
          </div>
        </div>

        <div class="chart-container">
          <h3>⏰ Actividad Temporal</h3>
          <div class="chart-wrapper">
            <canvas ref="timelineChart"></canvas>
          </div>
        </div>

        <div class="chart-container">
          <h3>🔄 Transiciones entre Zonas</h3>
          <div class="flow-visualization">
            <div v-if="analysisData.flow_analysis.zone_transitions" class="flow-items">
              <div 
                v-for="(count, transition) in analysisData.flow_analysis.zone_transitions" 
                :key="transition"
                class="flow-item"
              >
                <span class="transition-name">{{ formatTransition(transition) }}</span>
                <span class="transition-count">{{ count }} movimientos</span>
              </div>
            </div>
            <div v-else class="no-data">
              No se detectaron transiciones entre zonas
            </div>
          </div>
        </div>

        <div class="chart-container">
          <h3>📈 Estadísticas por Zona</h3>
          <div class="zone-stats">
            <div 
              v-for="(zoneData, zoneName) in analysisData.zone_analysis" 
              :key="zoneName"
              class="zone-stat-item"
            >
              <h4>{{ formatZoneName(zoneName) }}</h4>
              <div class="zone-details">
                <p><strong>Entradas:</strong> {{ zoneData.total_entries }}</p>
                <p><strong>Personas únicas:</strong> {{ zoneData.unique_persons }}</p>
                <p><strong>Duración activa:</strong> {{ zoneData.activity_duration.toFixed(1) }}s</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Información adicional -->
      <div class="additional-info">
        <div class="info-section">
          <h3>🎯 Resumen de Actividad</h3>
          <div class="activity-summary">
            <p><strong>Pico de actividad:</strong> 
              {{ analysisData.temporal_analysis.peak_activity.timestamp.toFixed(1) }}s 
              ({{ analysisData.temporal_analysis.peak_activity.detections }} detecciones)
            </p>
            <p><strong>Promedio por segundo:</strong> 
              {{ analysisData.temporal_analysis.average_detections_per_second.toFixed(2) }} detecciones/s
            </p>
            <p><strong>Tasa de detección:</strong> 
              {{ analysisData.summary.detection_rate.toFixed(2) }} detecciones/frame
            </p>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>📊 Selecciona una tarea para ver el análisis</p>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import axios from 'axios'

Chart.register(...registerables)

export default {
  name: 'AnalyticsDashboard',
  data() {
    return {
      selectedTaskId: '',
      availableTasks: [],
      analysisData: null,
      loading: false,
      error: null,
      charts: {}
    }
  },
  mounted() {
    this.loadAvailableTasks()
  },
  methods: {
    async loadAvailableTasks() {
      try {
        const response = await axios.get('http://127.0.0.1:8000/analytics/summary')
        this.availableTasks = response.data.tasks || []
      } catch (error) {
        this.error = 'Error loading available tasks: ' + error.message
        console.error('Error details:', error)
      }
    },
    
    async loadTaskData() {
      if (!this.selectedTaskId) {
        this.analysisData = null
        return
      }

      this.loading = true
      this.error = null

      try {
        console.log('Loading data for task:', this.selectedTaskId)
        const response = await axios.get(`http://127.0.0.1:8000/analytics/analyze/${this.selectedTaskId}`)
        this.analysisData = response.data
        console.log('Analysis data loaded:', this.analysisData)
        
        // Esperar a que Vue actualice el DOM
        await this.$nextTick()
        console.log('DOM updated, creating charts...')
        
        // Esperar un poco más para que los canvas estén disponibles
        setTimeout(() => {
          this.createCharts()
        }, 100)
        
      } catch (error) {
        console.error('Error loading analysis:', error)
        this.error = 'Error loading analysis: ' + error.message
        this.analysisData = null
      } finally {
        this.loading = false
      }
    },

    createCharts() {
      this.destroyCharts()
      
      if (!this.analysisData) {
        console.log('No analysis data available for charts')
        return
      }

      console.log('Creating charts with data:', this.analysisData)
      
      // Gráfico de distribución por zonas
      this.createZoneChart()
      
      // Gráfico de línea temporal
      this.createTimelineChart()
    },

    createZoneChart() {
      const ctx = this.$refs.zoneChart
      console.log('Zone chart context:', ctx)
      
      if (!ctx) {
        console.error('Zone chart canvas not found')
        return
      }

      const zoneData = this.analysisData.zone_analysis
      console.log('Zone data:', zoneData)
      
      if (!zoneData || Object.keys(zoneData).length === 0) {
        console.error('No zone data available')
        return
      }
      
      const labels = Object.keys(zoneData).map(zone => this.formatZoneName(zone))
      const data = Object.values(zoneData).map(zone => zone.total_entries)
      
      console.log('Chart labels:', labels)
      console.log('Chart data:', data)

      try {
        this.charts.zoneChart = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: labels,
            datasets: [{
              data: data,
              backgroundColor: [
                '#FF6384',
                '#36A2EB', 
                '#FFCE56',
                '#4BC0C0',
                '#9966FF',
                '#FF9966'
              ],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom'
              }
            }
          }
        })
        console.log('Zone chart created successfully')
      } catch (error) {
        console.error('Error creating zone chart:', error)
      }
    },

    createTimelineChart() {
      const ctx = this.$refs.timelineChart
      console.log('Timeline chart context:', ctx)
      
      if (!ctx) {
        console.error('Timeline chart canvas not found')
        return
      }

      const timelineData = this.analysisData.temporal_analysis.timeline
      console.log('Timeline data:', timelineData)
      
      if (!timelineData || Object.keys(timelineData).length === 0) {
        console.error('No timeline data available')
        return
      }
      
      const timestamps = Object.keys(timelineData).map(t => parseFloat(t))
      const detections = Object.values(timelineData).map(d => d.detections_per_second)
      
      console.log('Timeline timestamps:', timestamps.slice(0, 5))
      console.log('Timeline detections:', detections.slice(0, 5))

      try {
        this.charts.timelineChart = new Chart(ctx, {
          type: 'line',
          data: {
            labels: timestamps,
            datasets: [{
              label: 'Detecciones por segundo',
              data: detections,
              borderColor: '#36A2EB',
              backgroundColor: 'rgba(54, 162, 235, 0.1)',
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Tiempo (segundos)'
                }
              },
              y: {
                title: {
                  display: true,
                  text: 'Detecciones'
                },
                beginAtZero: true
              }
            }
          }
        })
        console.log('Timeline chart created successfully')
      } catch (error) {
        console.error('Error creating timeline chart:', error)
      }
    },

    destroyCharts() {
      Object.values(this.charts).forEach(chart => {
        if (chart) chart.destroy()
      })
      this.charts = {}
    },

    refreshData() {
      this.loadAvailableTasks()
      if (this.selectedTaskId) {
        this.loadTaskData()
      }
    },

    formatDate(timestamp) {
      return new Date(timestamp * 1000).toLocaleString()
    },

    formatZoneName(zoneName) {
      return zoneName.replace('zone_', 'Zona ')
    },

    formatTransition(transition) {
      return transition.replace(/_to_/g, ' → ').replace(/zone_/g, 'Zona ')
    }
  },

  beforeUnmount() {
    this.destroyCharts()
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #eee;
}

.dashboard-header h1 {
  margin: 0;
  color: #333;
  font-size: 2.5em;
}

.controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

.task-selector {
  padding: 10px 15px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  min-width: 200px;
}

.refresh-btn {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}

.refresh-btn:hover:not(:disabled) {
  background: #0056b3;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 60px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 40px;
  color: #dc3545;
  font-size: 18px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.card-icon {
  font-size: 2.5em;
}

.card-content h3 {
  margin: 0;
  font-size: 2em;
  color: #333;
}

.card-content p {
  margin: 5px 0 0 0;
  color: #666;
  font-size: 1.1em;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.chart-container h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 1.3em;
}

.chart-wrapper {
  height: 300px;
  position: relative;
}

.flow-visualization {
  min-height: 200px;
}

.flow-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.flow-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #007bff;
}

.transition-name {
  font-weight: 500;
  color: #333;
}

.transition-count {
  background: #007bff;
  color: white;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 0.9em;
  font-weight: 500;
}

.zone-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.zone-stat-item {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #28a745;
}

.zone-stat-item h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.zone-details p {
  margin: 8px 0;
  color: #666;
}

.additional-info {
  margin-top: 30px;
}

.info-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.info-section h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.activity-summary p {
  margin: 10px 0;
  color: #666;
  font-size: 1.1em;
}

.no-data {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 40px;
}

.empty-state {
  text-align: center;
  padding: 80px;
  color: #666;
  font-size: 1.2em;
}
</style>
