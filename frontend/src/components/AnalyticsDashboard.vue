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
        <div v-if="analysisData.dwell_time_analysis && analysisData.dwell_time_analysis.summary" class="card">
          <div class="card-icon">⏳</div>
          <div class="card-content">
            <h3>{{ analysisData.dwell_time_analysis.summary.overall_average.toFixed(1) }}s</h3>
            <p>Permanencia Promedio</p>
          </div>
        </div>
        <div v-if="analysisData.dwell_time_analysis && analysisData.dwell_time_analysis.summary" class="card">
          <div class="card-icon">🔢</div>
          <div class="card-content">
            <h3>{{ analysisData.dwell_time_analysis.summary.total_measured_visits }}</h3>
            <p>Visitas Medidas</p>
          </div>
        </div>
        <div v-if="analysisData.demographic_analysis && analysisData.demographic_analysis.has_data" class="card demographic wide-card">
          <div class="card-icon">👤</div>
          <div class="card-content">
            <h3>{{ analysisData.demographic_analysis.summary.most_common_gender === 'M' ? '♂️' : '♀️' }}</h3>
            <p>Género Predominante</p>
          </div>
        </div>
        <div v-if="analysisData.demographic_analysis && analysisData.demographic_analysis.has_data" class="card demographic wide-card">
          <div class="card-icon">🎂</div>
          <div class="card-content">
            <h3>{{ formatAgeRange(analysisData.demographic_analysis.summary.most_common_age) }}</h3>
            <p>Edad Más Común</p>
          </div>
        </div>
      </div>

      <!-- Gráficos principales en primera fila -->
      <div class="charts-grid main-charts">
        <div class="chart-container large">
          <h3>📊 Distribución por Zonas</h3>
          <div class="chart-wrapper">
            <canvas ref="zoneChart"></canvas>
          </div>
        </div>

        <div class="chart-container large">
          <h3>⏰ Actividad Temporal</h3>
          <div class="chart-wrapper">
            <canvas ref="timelineChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Gráficos de tiempo de permanencia en segunda fila -->
      <div v-if="analysisData.dwell_time_analysis && analysisData.dwell_time_analysis.summary" class="charts-grid dwell-charts">
        <div class="chart-container medium">
          <h3>⏳ Distribución de Tiempo de Permanencia</h3>
          <div class="chart-wrapper">
            <canvas ref="dwellDistributionChart"></canvas>
          </div>
        </div>

        <div class="chart-container medium">
          <h3>🕐 Tiempo Promedio por Zona</h3>
          <div class="chart-wrapper">
            <canvas ref="dwellByZoneChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Gráficos demográficos (género y edad) -->
      <div v-if="analysisData.demographic_analysis && analysisData.demographic_analysis.has_data" class="charts-grid demographic-charts">
        <div class="chart-container medium">
          <h3>👥 Distribución por Género</h3>
          <div class="chart-wrapper">
            <canvas ref="genderChart"></canvas>
          </div>
        </div>

        <div class="chart-container medium">
          <h3>🎂 Distribución por Edad</h3>
          <div class="chart-wrapper">
            <canvas ref="ageChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Gráficos demográficos por zona -->
      <div v-if="analysisData.demographic_analysis && analysisData.demographic_analysis.has_data" class="charts-grid demographic-zone-charts">
        <div class="chart-container large">
          <h3>👥📍 Género por Zona</h3>
          <div class="chart-wrapper">
            <canvas ref="genderByZoneChart"></canvas>
          </div>
        </div>

        <div class="chart-container large">
          <h3>🎂📍 Edad por Zona</h3>
          <div class="chart-wrapper">
            <canvas ref="ageByZoneChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Información detallada en tercera fila -->
      <div class="info-grid">
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

        <div v-if="analysisData.dwell_time_analysis && analysisData.dwell_time_analysis.by_zone" class="chart-container wide">
          <h3>📊 Estadísticas de Permanencia por Zona</h3>
          <div class="dwell-stats">
            <div 
              v-for="(zoneData, zoneName) in analysisData.dwell_time_analysis.by_zone" 
              :key="zoneName"
              class="dwell-stat-item"
            >
              <h4>{{ formatZoneName(zoneName) }}</h4>
              <div class="dwell-details" v-if="typeof zoneData === 'object' && zoneData.average_dwell_time">
                <p><strong>Tiempo promedio:</strong> {{ zoneData.average_dwell_time.toFixed(1) }}s</p>
                <p><strong>Tiempo mediano:</strong> {{ zoneData.median_dwell_time.toFixed(1) }}s</p>
                <p><strong>Visitas totales:</strong> {{ zoneData.total_visits }}</p>
                <p><strong>Permanencia máxima:</strong> {{ zoneData.max_dwell_time.toFixed(1) }}s</p>
                <p><strong>Permanencia mínima:</strong> {{ zoneData.min_dwell_time.toFixed(1) }}s</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Información adicional -->
      <div class="additional-info">
        <div class="summary-row">
          <div class="info-section activity-section">
            <h3>🎯 Resumen de Actividad</h3>
            <div class="activity-summary">
              <div class="metric-item">
                <span class="metric-label">Pico de actividad:</span>
                <span class="metric-value">{{ analysisData.temporal_analysis.peak_activity.timestamp.toFixed(1) }}s 
                  ({{ analysisData.temporal_analysis.peak_activity.detections }} detecciones)</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Promedio por segundo:</span>
                <span class="metric-value">{{ analysisData.temporal_analysis.average_detections_per_second.toFixed(2) }} detecciones/s</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Tasa de detección:</span>
                <span class="metric-value">{{ analysisData.summary.detection_rate.toFixed(2) }} detecciones/frame</span>
              </div>
            </div>
          </div>

          <div v-if="analysisData.dwell_time_analysis && analysisData.dwell_time_analysis.summary" class="info-section dwell-section">
            <h3>⏳ Resumen de Tiempo de Permanencia</h3>
            <div class="dwell-summary">
              <div class="metric-item">
                <span class="metric-label">Tiempo promedio global:</span>
                <span class="metric-value">{{ analysisData.dwell_time_analysis.summary.overall_average.toFixed(1) }}s</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Tiempo mediano:</span>
                <span class="metric-value">{{ analysisData.dwell_time_analysis.summary.overall_median.toFixed(1) }}s</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Permanencia más larga:</span>
                <span class="metric-value">{{ analysisData.dwell_time_analysis.summary.longest_stay.toFixed(1) }}s</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Permanencia más corta:</span>
                <span class="metric-value">{{ analysisData.dwell_time_analysis.summary.shortest_stay.toFixed(1) }}s</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="analysisData.dwell_time_analysis && analysisData.dwell_time_analysis.summary" class="distribution-overview">
          <h3>📊 Distribución de Permanencias</h3>
          <div class="distribution-cards">
            <div class="dist-card short">
              <div class="dist-icon">⚡</div>
              <div class="dist-content">
                <h4>{{ analysisData.dwell_time_analysis.summary.distribution.under_10s }}</h4>
                <p>Menos de 10s</p>
              </div>
            </div>
            <div class="dist-card medium-time">
              <div class="dist-icon">⏱️</div>
              <div class="dist-content">
                <h4>{{ analysisData.dwell_time_analysis.summary.distribution['10_30s'] }}</h4>
                <p>10-30 segundos</p>
              </div>
            </div>
            <div class="dist-card long">
              <div class="dist-icon">⏰</div>
              <div class="dist-content">
                <h4>{{ analysisData.dwell_time_analysis.summary.distribution['30_60s'] }}</h4>
                <p>30-60 segundos</p>
              </div>
            </div>
            <div class="dist-card very-long">
              <div class="dist-icon">🕐</div>
              <div class="dist-content">
                <h4>{{ analysisData.dwell_time_analysis.summary.distribution.over_60s }}</h4>
                <p>Más de 60s</p>
              </div>
            </div>
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
      
      // Gráficos de tiempo de permanencia (si hay datos disponibles)
      if (this.analysisData.dwell_time_analysis && this.analysisData.dwell_time_analysis.summary) {
        this.createDwellDistributionChart()
        this.createDwellByZoneChart()
      }

      // Gráficos demográficos (si hay datos disponibles)
      if (this.analysisData.demographic_analysis && this.analysisData.demographic_analysis.has_data) {
        this.createGenderChart()
        this.createAgeChart()
        this.createGenderByZoneChart()
        this.createAgeByZoneChart()
      }
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

    createDwellDistributionChart() {
      const ctx = this.$refs.dwellDistributionChart
      console.log('Dwell distribution chart context:', ctx)
      
      if (!ctx) {
        console.error('Dwell distribution chart canvas not found')
        return
      }

      const distribution = this.analysisData.dwell_time_analysis.summary.distribution
      console.log('Dwell distribution data:', distribution)
      
      if (!distribution) {
        console.error('No dwell distribution data available')
        return
      }
      
      const labels = ['< 10s', '10-30s', '30-60s', '> 60s']
      const data = [
        distribution.under_10s || 0,
        distribution['10_30s'] || 0,
        distribution['30_60s'] || 0,
        distribution.over_60s || 0
      ]
      
      console.log('Distribution labels:', labels)
      console.log('Distribution data:', data)

      try {
        this.charts.dwellDistributionChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Número de visitas',
              data: data,
              backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 206, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(153, 102, 255, 0.8)'
              ],
              borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)'
              ],
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Número de visitas'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Duración de permanencia'
                }
              }
            }
          }
        })
        console.log('Dwell distribution chart created successfully')
      } catch (error) {
        console.error('Error creating dwell distribution chart:', error)
      }
    },

    createDwellByZoneChart() {
      const ctx = this.$refs.dwellByZoneChart
      console.log('Dwell by zone chart context:', ctx)
      
      if (!ctx) {
        console.error('Dwell by zone chart canvas not found')
        return
      }

      const zoneData = this.analysisData.dwell_time_analysis.by_zone
      console.log('Dwell by zone data:', zoneData)
      
      if (!zoneData || Object.keys(zoneData).length === 0) {
        console.error('No dwell by zone data available')
        return
      }
      
      const labels = []
      const avgTimes = []
      const visitCounts = []
      
      for (const [zoneName, data] of Object.entries(zoneData)) {
        if (typeof data === 'object' && data.average_dwell_time) {
          labels.push(this.formatZoneName(zoneName))
          avgTimes.push(data.average_dwell_time)
          visitCounts.push(data.total_visits)
        }
      }
      
      console.log('Dwell by zone labels:', labels)
      console.log('Dwell by zone avg times:', avgTimes)

      try {
        this.charts.dwellByZoneChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Tiempo promedio (segundos)',
              data: avgTimes,
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1,
              yAxisID: 'y'
            }, {
              label: 'Número de visitas',
              data: visitCounts,
              backgroundColor: 'rgba(255, 99, 132, 0.8)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1,
              yAxisID: 'y1',
              type: 'line'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                type: 'linear',
                display: true,
                position: 'left',
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Tiempo promedio (segundos)'
                }
              },
              y1: {
                type: 'linear',
                display: true,
                position: 'right',
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Número de visitas'
                },
                grid: {
                  drawOnChartArea: false,
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Zonas'
                }
              }
            }
          }
        })
        console.log('Dwell by zone chart created successfully')
      } catch (error) {
        console.error('Error creating dwell by zone chart:', error)
      }
    },

    createGenderChart() {
      const ctx = this.$refs.genderChart
      
      if (!ctx) {
        console.error('Gender chart canvas not found')
        return
      }

      const genderData = this.analysisData.demographic_analysis.gender_distribution
      console.log('Gender data:', genderData)
      
      if (!genderData || !genderData.counts) {
        console.error('No gender data available')
        return
      }

      const labels = []
      const data = []
      const colors = []
      
      for (const [gender, count] of Object.entries(genderData.counts)) {
        labels.push(gender === 'M' ? '♂ Masculino' : '♀ Femenino')
        data.push(count)
        colors.push(gender === 'M' ? 'rgba(54, 162, 235, 0.8)' : 'rgba(255, 99, 132, 0.8)')
      }

      try {
        this.charts.genderChart = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: labels,
            datasets: [{
              label: 'Personas',
              data: data,
              backgroundColor: colors,
              borderColor: colors.map(c => c.replace('0.8', '1')),
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: true,
                position: 'bottom'
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const label = context.label || ''
                    const value = context.parsed
                    const percentage = genderData.percentages[context.label.includes('♂') ? 'M' : 'F']
                    return `${label}: ${value} (${percentage}%)`
                  }
                }
              }
            }
          }
        })
        console.log('Gender chart created successfully')
      } catch (error) {
        console.error('Error creating gender chart:', error)
      }
    },

    createAgeChart() {
      const ctx = this.$refs.ageChart
      
      if (!ctx) {
        console.error('Age chart canvas not found')
        return
      }

      const ageData = this.analysisData.demographic_analysis.age_distribution
      console.log('Age data:', ageData)
      
      if (!ageData || !ageData.counts) {
        console.error('No age data available')
        return
      }

      // Ordenar rangos de edad de menor a mayor
      const ageOrder = ['0-18', '19-35', '36-60', '60+', 'Desconocido']
      const labels = []
      const data = []
      const colors = [
        'rgba(75, 192, 192, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(201, 203, 207, 0.8)'
      ]

      ageOrder.forEach((age, index) => {
        if (ageData.counts[age]) {
          labels.push(this.formatAgeRange(age))
          data.push(ageData.counts[age])
        }
      })

      try {
        this.charts.ageChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Personas',
              data: data,
              backgroundColor: colors.slice(0, labels.length),
              borderColor: colors.slice(0, labels.length).map(c => c.replace('0.8', '1')),
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const value = context.parsed.y
                    const age = context.label
                    // Buscar el percentage correspondiente
                    let percentage = 0
                    for (const [key, val] of Object.entries(ageData.counts)) {
                      if (age.includes(key) || age.includes(this.formatAgeRange(key))) {
                        percentage = ageData.percentages[key]
                        break
                      }
                    }
                    return `${age}: ${value} personas (${percentage}%)`
                  }.bind(this)
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Número de Personas'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Rango de Edad'
                }
              }
            }
          }
        })
        console.log('Age chart created successfully')
      } catch (error) {
        console.error('Error creating age chart:', error)
      }
    },

    createGenderByZoneChart() {
      const ctx = this.$refs.genderByZoneChart
      
      if (!ctx) {
        console.error('Gender by zone chart canvas not found')
        return
      }

      const genderByZone = this.analysisData.demographic_analysis.gender_by_zone
      console.log('Gender by zone data:', genderByZone)
      
      if (!genderByZone || Object.keys(genderByZone).length === 0) {
        console.error('No gender by zone data available')
        return
      }

      const zones = Object.keys(genderByZone).sort()
      const maleData = []
      const femaleData = []

      zones.forEach(zone => {
        const counts = genderByZone[zone].counts
        maleData.push(counts['M'] || 0)
        femaleData.push(counts['F'] || 0)
      })

      try {
        this.charts.genderByZoneChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: zones.map(z => this.formatZoneName(z)),
            datasets: [{
              label: '♂ Masculino',
              data: maleData,
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 2
            }, {
              label: '♀ Femenino',
              data: femaleData,
              backgroundColor: 'rgba(255, 99, 132, 0.8)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: true,
                position: 'top'
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Número de Personas'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Zonas'
                }
              }
            }
          }
        })
        console.log('Gender by zone chart created successfully')
      } catch (error) {
        console.error('Error creating gender by zone chart:', error)
      }
    },

    createAgeByZoneChart() {
      const ctx = this.$refs.ageByZoneChart
      
      if (!ctx) {
        console.error('Age by zone chart canvas not found')
        return
      }

      const ageByZone = this.analysisData.demographic_analysis.age_by_zone
      console.log('Age by zone data:', ageByZone)
      
      if (!ageByZone || Object.keys(ageByZone).length === 0) {
        console.error('No age by zone data available')
        return
      }

      const zones = Object.keys(ageByZone).sort()
      const ageRanges = ['0-18', '19-35', '36-60', '60+']
      const colors = [
        'rgba(75, 192, 192, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
      ]

      const datasets = ageRanges.map((range, index) => {
        const data = zones.map(zone => {
          const counts = ageByZone[zone].counts
          return counts[range] || 0
        })

        return {
          label: this.formatAgeRange(range),
          data: data,
          backgroundColor: colors[index],
          borderColor: colors[index].replace('0.8', '1'),
          borderWidth: 2
        }
      })

      try {
        this.charts.ageByZoneChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: zones.map(z => this.formatZoneName(z)),
            datasets: datasets
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: true,
                position: 'top'
              }
            },
            scales: {
              y: {
                stacked: true,
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Número de Personas'
                }
              },
              x: {
                stacked: true,
                title: {
                  display: true,
                  text: 'Zonas'
                }
              }
            }
          }
        })
        console.log('Age by zone chart created successfully')
      } catch (error) {
        console.error('Error creating age by zone chart:', error)
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
    },

    formatAgeRange(age) {
      const ageLabels = {
        '0-18': '0-18 años',
        '19-35': '19-35 años',
        '36-60': '36-60 años',
        '60+': '60+ años',
        'Desconocido': 'Desconocido'
      }
      return ageLabels[age] || age
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
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

@media (min-width: 1200px) {
  .summary-cards {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
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

.card.demographic {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card.demographic .card-content h3,
.card.demographic .card-content p {
  color: white;
}

.card.wide-card {
  grid-column: span 2;
}

@media (max-width: 768px) {
  .card.wide-card {
    grid-column: span 1;
  }
}

.charts-grid {
  display: grid;
  gap: 25px;
  margin-bottom: 30px;
}

.main-charts {
  grid-template-columns: 1fr 1fr;
}

.dwell-charts {
  grid-template-columns: 1fr 1fr;
}

.demographic-charts {
  grid-template-columns: 1fr 1fr;
}

.demographic-zone-charts {
  grid-template-columns: 1fr 1fr;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.chart-container.wide {
  grid-column: span 2;
}

@media (max-width: 1200px) {
  .main-charts,
  .dwell-charts,
  .demographic-charts,
  .demographic-zone-charts {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
  
  .chart-container.wide {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container.wide {
    grid-column: span 1;
  }
}

.chart-container {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.chart-container:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.15);
}

.chart-container.large {
  min-height: 400px;
}

.chart-container.medium {
  min-height: 350px;
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

.chart-container.large .chart-wrapper {
  height: 320px;
}

.chart-container.medium .chart-wrapper {
  height: 280px;
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

.summary-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .summary-row {
    grid-template-columns: 1fr;
  }
}

.info-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.info-section:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.15);
}

.activity-section {
  border-left: 4px solid #007bff;
}

.dwell-section {
  border-left: 4px solid #17a2b8;
}

.info-section h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 15px 0;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-label {
  font-weight: 500;
  color: #666;
}

.metric-value {
  font-weight: 600;
  color: #333;
  font-size: 1.1em;
}

.distribution-overview {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  border-left: 4px solid #28a745;
}

.distribution-overview h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.distribution-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.dist-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  transition: transform 0.2s, background 0.2s;
  border: 2px solid transparent;
}

.dist-card:hover {
  transform: translateY(-3px);
  background: #e9ecef;
}

.dist-card.short {
  border-color: #dc3545;
}

.dist-card.medium-time {
  border-color: #ffc107;
}

.dist-card.long {
  border-color: #fd7e14;
}

.dist-card.very-long {
  border-color: #6f42c1;
}

.dist-icon {
  font-size: 2em;
  margin-bottom: 10px;
}

.dist-content h4 {
  margin: 0;
  font-size: 1.8em;
  color: #333;
}

.dist-content p {
  margin: 5px 0 0 0;
  color: #666;
  font-size: 0.9em;
}

.dwell-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.dwell-stat-item {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #17a2b8;
}

.dwell-stat-item h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.dwell-details p {
  margin: 8px 0;
  color: #666;
}

@media (max-width: 1200px) {
  .main-charts,
  .dwell-charts {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
  
  .chart-container.wide {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-container.wide {
    grid-column: span 1;
  }
  
  .dwell-stats {
    grid-template-columns: 1fr;
  }
}

.dwell-stat-item {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #17a2b8;
}

.dwell-stat-item h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.dwell-details p {
  margin: 8px 0;
  color: #666;
}

.dwell-summary {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #ffc107;
}

.dwell-summary p {
  margin: 10px 0;
  color: #666;
  font-size: 1.1em;
}

.distribution-summary {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #dee2e6;
}

.distribution-summary h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.1em;
}

.distribution-summary p {
  margin: 5px 0;
  color: #666;
  font-size: 1em;
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
