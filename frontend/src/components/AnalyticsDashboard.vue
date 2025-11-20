<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>📊 Analytics Dashboard por Zonas</h1>
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

    <div v-else-if="selectedTaskId" class="dashboard-content">
      <!-- Sistema de Pestañas -->
      <div class="tabs-container">
        <div class="tabs">
          <button 
            v-for="zone in [0, 1, 2, 3]" 
            :key="zone"
            :class="['tab-button', { active: activeZone === zone }]"
            @click="selectZone(zone)"
          >
            📍 Zona {{ zone }}
          </button>
        </div>
      </div>

      <!-- Contenido de la Zona Activa -->
      <div v-if="zoneData[activeZone]" class="zone-content">
        <!-- Tarjetas de resumen para la zona -->
        <div class="summary-cards">
          <div class="card">
            <div class="card-icon">🚶</div>
            <div class="card-content">
              <h3>{{ zoneData[activeZone].real_visits.total_real_visits }}</h3>
              <p>Visitas Reales</p>
            </div>
          </div>
          <div class="card">
            <div class="card-icon">👥</div>
            <div class="card-content">
              <h3>{{ zoneData[activeZone].real_visits.unique_persons }}</h3>
              <p>Personas Únicas</p>
            </div>
          </div>
          <div v-if="zoneData[activeZone].dwell_time.average_dwell_time" class="card">
            <div class="card-icon">⏳</div>
            <div class="card-content">
              <h3>{{ zoneData[activeZone].dwell_time.average_dwell_time.toFixed(1) }}s</h3>
              <p>Tiempo Promedio</p>
            </div>
          </div>
          <div v-if="zoneData[activeZone].gender_distribution.has_data" class="card demographic">
            <div class="card-icon">👤</div>
            <div class="card-content">
              <h3>{{ zoneData[activeZone].gender_distribution.most_common === 'M' ? '♂️' : '♀️' }}</h3>
              <p>Género Predominante</p>
            </div>
          </div>
          <div v-if="zoneData[activeZone].age_distribution.has_data" class="card demographic">
            <div class="card-icon">🎂</div>
            <div class="card-content">
              <h3>{{ formatAgeRange(zoneData[activeZone].age_distribution.most_common) }}</h3>
              <p>Edad Más Común</p>
            </div>
          </div>
        </div>

        <!-- Gráficos para la zona activa -->
        <div class="charts-grid zone-charts">
          <!-- Gráfico de Visitas Reales -->
          <div class="chart-container medium">
            <h3>🚶 Distribución de Visitas Reales - Zona {{ activeZone }}</h3>
            <div class="chart-wrapper">
              <canvas :ref="el => { if (el) visitsChartRef = el }"></canvas>
            </div>
          </div>

          <!-- Gráfico de Tiempo de Permanencia -->
          <div v-if="zoneData[activeZone].dwell_time.distribution" class="chart-container medium">
            <h3>⏳ Distribución de Tiempo de Permanencia - Zona {{ activeZone }}</h3>
            <div class="chart-wrapper">
              <canvas :ref="el => { if (el) dwellChartRef = el }"></canvas>
            </div>
          </div>

          <!-- Gráfico de Género -->
          <div v-if="zoneData[activeZone].gender_distribution.has_data" class="chart-container medium">
            <h3>👥 Distribución por Género - Zona {{ activeZone }}</h3>
            <div class="chart-wrapper">
              <canvas :ref="el => { if (el) genderChartRef = el }"></canvas>
            </div>
          </div>

          <!-- Gráfico de Edad -->
          <div v-if="zoneData[activeZone].age_distribution.has_data" class="chart-container medium">
            <h3>🎂 Distribución por Edad - Zona {{ activeZone }}</h3>
            <div class="chart-wrapper">
              <canvas :ref="el => { if (el) ageChartRef = el }"></canvas>
            </div>
          </div>
        </div>

        <!-- Información detallada de la zona -->
        <div class="zone-details-section">
          <div class="info-section">
            <h3>📊 Estadísticas de Visitas - Zona {{ activeZone }}</h3>
            <div class="stats-grid">
              <div class="metric-item">
                <span class="metric-label">Visitas totales:</span>
                <span class="metric-value">{{ zoneData[activeZone].real_visits.total_real_visits }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Personas únicas:</span>
                <span class="metric-value">{{ zoneData[activeZone].real_visits.unique_persons }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Promedio visitas/persona:</span>
                <span class="metric-value">{{ zoneData[activeZone].real_visits.average_visits_per_person.toFixed(2) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Máx visitas de una persona:</span>
                <span class="metric-value">{{ zoneData[activeZone].real_visits.max_visits_by_one_person }}</span>
              </div>
            </div>
          </div>

          <div v-if="zoneData[activeZone].dwell_time.average_dwell_time" class="info-section">
            <h3>⏳ Estadísticas de Permanencia - Zona {{ activeZone }}</h3>
            <div class="stats-grid">
              <div class="metric-item">
                <span class="metric-label">Tiempo promedio:</span>
                <span class="metric-value">{{ zoneData[activeZone].dwell_time.average_dwell_time.toFixed(1) }}s</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Tiempo mediano:</span>
                <span class="metric-value">{{ zoneData[activeZone].dwell_time.median_dwell_time.toFixed(1) }}s</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Tiempo máximo:</span>
                <span class="metric-value">{{ zoneData[activeZone].dwell_time.max_dwell_time.toFixed(1) }}s</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Tiempo mínimo:</span>
                <span class="metric-value">{{ zoneData[activeZone].dwell_time.min_dwell_time.toFixed(1) }}s</span>
              </div>
            </div>
          </div>

          <div v-if="zoneData[activeZone].gender_distribution.has_data" class="info-section">
            <h3>👥 Estadísticas de Género - Zona {{ activeZone }}</h3>
            <div class="stats-grid">
              <div class="metric-item">
                <span class="metric-label">Total clasificado:</span>
                <span class="metric-value">{{ zoneData[activeZone].gender_distribution.total_classified }} personas</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Más común:</span>
                <span class="metric-value">{{ zoneData[activeZone].gender_distribution.most_common === 'M' ? 'Masculino' : 'Femenino' }}</span>
              </div>
            </div>
          </div>

          <div v-if="zoneData[activeZone].age_distribution.has_data" class="info-section">
            <h3>🎂 Estadísticas de Edad - Zona {{ activeZone }}</h3>
            <div class="stats-grid">
              <div class="metric-item">
                <span class="metric-label">Total clasificado:</span>
                <span class="metric-value">{{ zoneData[activeZone].age_distribution.total_classified }} personas</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Rango más común:</span>
                <span class="metric-value">{{ formatAgeRange(zoneData[activeZone].age_distribution.most_common) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="zoneData[activeZone] && !zoneData[activeZone].has_data" class="no-data-zone">
        <p>📊 No hay datos disponibles para la Zona {{ activeZone }}</p>
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
      activeZone: 0,
      zoneData: {
        0: null,
        1: null,
        2: null,
        3: null
      },
      loading: false,
      error: null,
      charts: {},
      // Referencias a los canvas
      visitsChartRef: null,
      dwellChartRef: null,
      genderChartRef: null,
      ageChartRef: null,
      // Control de timeouts para evitar solapamientos
      chartCreationTimeout: null,
      isCreatingCharts: false
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
        this.zoneData = { 0: null, 1: null, 2: null, 3: null }
        this.destroyCharts()
        return
      }

      this.loading = true
      this.error = null
      
      // Destruir todos los gráficos existentes antes de cargar nuevos datos
      this.destroyCharts()

      try {
        console.log('Loading data for task:', this.selectedTaskId)
        
        // Cargar datos para cada zona (0, 1, 2, 3)
        const zonePromises = [0, 1, 2, 3].map(zoneId => 
          axios.get(`http://127.0.0.1:8000/analytics/zone/${this.selectedTaskId}/${zoneId}`)
            .then(response => ({ zoneId, data: response.data }))
            .catch(error => {
              console.error(`Error loading zone ${zoneId}:`, error)
              return { zoneId, data: { has_data: false, error: error.message } }
            })
        )
        
        const zoneResults = await Promise.all(zonePromises)
        
        // Almacenar datos de cada zona
        zoneResults.forEach(({ zoneId, data }) => {
          this.zoneData[zoneId] = data
        })
        
        console.log('Zone data loaded:', this.zoneData)
        
        // Esperar a que Vue actualice el DOM
        await this.$nextTick()
        console.log('DOM updated, creating charts...')
        
        // Cancelar cualquier creación de gráficos pendiente
        if (this.chartCreationTimeout) {
          clearTimeout(this.chartCreationTimeout)
        }
        
        // Esperar un poco más para que los canvas estén disponibles
        this.chartCreationTimeout = setTimeout(() => {
          this.renderZoneCharts()
        }, 150)
        
      } catch (error) {
        console.error('Error loading analysis:', error)
        this.error = 'Error loading analysis: ' + error.message
        this.zoneData = { 0: null, 1: null, 2: null, 3: null }
      } finally {
        this.loading = false
      }
    },
    
    selectZone(zone) {
      // Cancelar cualquier creación de gráficos pendiente
      if (this.chartCreationTimeout) {
        clearTimeout(this.chartCreationTimeout)
        this.chartCreationTimeout = null
      }
      
      // Si ya estamos creando gráficos, esperar
      if (this.isCreatingCharts) {
        this.chartCreationTimeout = setTimeout(() => this.selectZone(zone), 100)
        return
      }
      
      this.activeZone = zone
      
      // Limpiar los gráficos de los canvas actuales antes del cambio
      this.destroyCanvasCharts()
      
      // Crear gráficos para la nueva zona después de que Vue actualice el DOM
      this.$nextTick(() => {
        this.chartCreationTimeout = setTimeout(() => {
          this.renderZoneCharts()
        }, 200)
      })
    },

    renderZoneCharts() {
      // Prevenir múltiples creaciones simultáneas
      if (this.isCreatingCharts) {
        return
      }
      
      const zone = this.activeZone
      const data = this.zoneData[zone]
      
      if (!data || !data.has_data) {
        console.log(`No data available for zone ${zone}`)
        return
      }
      
      // Siempre renderizar los gráficos (el canvas es nuevo después del cambio de zona)
      this.createZoneCharts()
    },
    
    createZoneCharts() {
      // Prevenir múltiples creaciones simultáneas
      if (this.isCreatingCharts) {
        return
      }
      
      this.isCreatingCharts = true
      
      try {
        const zone = this.activeZone
        const data = this.zoneData[zone]
        
        if (!data || !data.has_data) {
          console.log(`No data available for zone ${zone}`)
          return
        }

        console.log(`Creating charts for zone ${zone} with data:`, data)
        
        // Gráfico de visitas reales
        this.createVisitsChart(zone, data)
        
        // Gráfico de tiempo de permanencia (si hay datos disponibles)
        if (data.dwell_time && data.dwell_time.distribution) {
          this.createDwellChart(zone, data)
        }

        // Gráficos demográficos (si hay datos disponibles)
        if (data.gender_distribution && data.gender_distribution.has_data) {
          this.createGenderChartForZone(zone, data)
        }
        
        if (data.age_distribution && data.age_distribution.has_data) {
          this.createAgeChartForZone(zone, data)
        }
      } finally {
        this.isCreatingCharts = false
      }
    },
    
    destroyZoneCharts(zone) {
      // Destruir solo los gráficos de la zona específica
      const chartKeys = [
        `visitsChart_${zone}`,
        `dwellChart_${zone}`,
        `genderChart_${zone}`,
        `ageChart_${zone}`
      ]
      
      chartKeys.forEach(key => {
        if (this.charts[key]) {
          try {
            this.charts[key].destroy()
          } catch (e) {
            console.warn(`Error destroying chart ${key}:`, e)
          }
          delete this.charts[key]
        }
      })
    },
    
    destroyAllCurrentCharts() {
      // Destruir todos los gráficos que puedan estar en los canvas actuales
      // Buscar por todas las zonas posibles
      for (let zone = 0; zone <= 3; zone++) {
        this.destroyZoneCharts(zone)
      }
    },
    
    destroyCanvasCharts() {
      // Destruir solo los gráficos actualmente en los canvas usando Chart.js API
      if (this.visitsChartRef) {
        const chart = Chart.getChart(this.visitsChartRef)
        if (chart) chart.destroy()
      }
      if (this.dwellChartRef) {
        const chart = Chart.getChart(this.dwellChartRef)
        if (chart) chart.destroy()
      }
      if (this.genderChartRef) {
        const chart = Chart.getChart(this.genderChartRef)
        if (chart) chart.destroy()
      }
      if (this.ageChartRef) {
        const chart = Chart.getChart(this.ageChartRef)
        if (chart) chart.destroy()
      }
    },

    createVisitsChart(zone, data) {
      const ctx = this.visitsChartRef
      
      if (!ctx) {
        console.error(`Visits chart canvas not found for zone ${zone}`)
        return
      }

      try {
        const chartKey = `visitsChart_${zone}`
        
        // Obtener instancia de Chart.js asociada al canvas si existe y destruirla
        const existingChart = Chart.getChart(ctx)
        if (existingChart) {
          existingChart.destroy()
        }
        
        this.charts[chartKey] = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['Visitas Reales', 'Personas Únicas'],
            datasets: [{
              label: 'Cantidad',
              data: [
                data.real_visits.total_real_visits,
                data.real_visits.unique_persons
              ],
              backgroundColor: [
                'rgba(54, 162, 235, 0.8)',
                'rgba(75, 192, 192, 0.8)'
              ],
              borderColor: [
                'rgba(54, 162, 235, 1)',
                'rgba(75, 192, 192, 1)'
              ],
              borderWidth: 2
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Cantidad'
                }
              }
            }
          }
        })
        console.log(`Visits chart created successfully for zone ${zone}`)
      } catch (error) {
        console.error(`Error creating visits chart for zone ${zone}:`, error)
      }
    },

    createDwellChart(zone, data) {
      const ctx = this.dwellChartRef
      
      if (!ctx) {
        console.error(`Dwell chart canvas not found for zone ${zone}`)
        return
      }
      
      const chartKey = `dwellChart_${zone}`
      
      // Obtener instancia de Chart.js asociada al canvas si existe y destruirla
      const existingChart = Chart.getChart(ctx)
      if (existingChart) {
        existingChart.destroy()
      }

      const distribution = data.dwell_time.distribution
      const labels = ['< 10s', '10-30s', '30-60s', '> 60s']
      const chartData = [
        distribution.under_10s || 0,
        distribution['10_30s'] || 0,
        distribution['30_60s'] || 0,
        distribution.over_60s || 0
      ]

      try {
        this.charts[chartKey] = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Número de visitas',
              data: chartData,
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
        console.log(`Dwell chart created successfully for zone ${zone}`)
      } catch (error) {
        console.error(`Error creating dwell chart for zone ${zone}:`, error)
      }
    },

    createGenderChartForZone(zone, data) {
      const ctx = this.genderChartRef
      
      if (!ctx) {
        console.error(`Gender chart canvas not found for zone ${zone}`)
        return
      }
      
      const chartKey = `genderChart_${zone}`
      
      // Obtener instancia de Chart.js asociada al canvas si existe y destruirla
      const existingChart = Chart.getChart(ctx)
      if (existingChart) {
        existingChart.destroy()
      }

      const genderData = data.gender_distribution
      
      if (!genderData || !genderData.counts) {
        console.error(`No gender data available for zone ${zone}`)
        return
      }

      const labels = []
      const chartData = []
      const colors = []
      
      for (const [gender, count] of Object.entries(genderData.counts)) {
        labels.push(gender === 'M' ? '♂ Masculino' : '♀ Femenino')
        chartData.push(count)
        colors.push(gender === 'M' ? 'rgba(54, 162, 235, 0.8)' : 'rgba(255, 99, 132, 0.8)')
      }

      try {
        this.charts[chartKey] = new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: labels,
            datasets: [{
              label: 'Personas',
              data: chartData,
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
        console.log(`Gender chart created successfully for zone ${zone}`)
      } catch (error) {
        console.error(`Error creating gender chart for zone ${zone}:`, error)
      }
    },

    createAgeChartForZone(zone, data) {
      const ctx = this.ageChartRef
      
      if (!ctx) {
        console.error(`Age chart canvas not found for zone ${zone}`)
        return
      }
      
      const chartKey = `ageChart_${zone}`
      
      // Obtener instancia de Chart.js asociada al canvas si existe y destruirla
      const existingChart = Chart.getChart(ctx)
      if (existingChart) {
        existingChart.destroy()
      }

      const ageData = data.age_distribution
      
      if (!ageData || !ageData.counts) {
        console.error(`No age data available for zone ${zone}`)
        return
      }

      // Definir mapeos de etiquetas para diferentes modelos
      const labelMappings = {
        // NTQAI Labels (Raw)
        'AgeLess15': '0-15 años',
        'Age16-30': '16-30 años',
        'Age31-45': '31-45 años',
        'Age46-60': '46-60 años',
        'AgeAbove60': '60+ años',
        
        // NTQAI Labels (Mapped in Backend)
        '0-15': '0-15 años',
        '16-30': '16-30 años',
        '31-45': '31-45 años',
        '46-60': '46-60 años',
        '60+': '60+ años',
        
        // PAR Labels
        'Niño': 'Niño (0-12)',
        'Adolescente': 'Adolescente (13-19)',
        'Adulto Joven': 'Joven (20-35)',
        'Adulto': 'Adulto (36-60)',
        'Mayor': 'Mayor (60+)',
        
        // Legacy Labels
        '0-18': '0-15 años',
        '19-30': '16-30 años',
        '19-35': '16-30 años',
        '36-60': '36-60 años'
      }

      // Orden preferido para cada set de etiquetas
      const sortOrders = {
        ntqai_raw: ['AgeLess15', 'Age16-30', 'Age31-45', 'Age46-60', 'AgeAbove60'],
        ntqai_mapped: ['0-15', '16-30', '31-45', '46-60', '60+'],
        par: ['Niño', 'Adolescente', 'Adulto Joven', 'Adulto', 'Mayor'],
        legacy: ['0-18', '19-30', '19-35', '36-60', '60+']
      }

      // Detectar qué tipo de etiquetas estamos usando
      const availableKeys = Object.keys(ageData.counts)
      let currentOrder = availableKeys // Default: orden como venga
      
      if (availableKeys.some(k => k.startsWith('Age'))) {
        currentOrder = sortOrders.ntqai_raw
      } else if (availableKeys.includes('0-15')) {
        currentOrder = sortOrders.ntqai_mapped
      } else if (availableKeys.includes('Niño')) {
        currentOrder = sortOrders.par
      } else if (availableKeys.includes('0-18') || availableKeys.includes('19-30')) {
        currentOrder = sortOrders.legacy
      }

      const labels = []
      const chartData = []
      
      // Construir datos ordenados
      currentOrder.forEach(key => {
        if (ageData.counts[key] !== undefined) {
          labels.push(labelMappings[key] || key)
          chartData.push(ageData.counts[key])
        }
      })
      
      // Agregar cualquier otra etiqueta que no esté en el orden predefinido
      availableKeys.forEach(key => {
        if (!currentOrder.includes(key)) {
          labels.push(labelMappings[key] || key)
          chartData.push(ageData.counts[key])
        }
      })

      const colors = [
        'rgba(75, 192, 192, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(255, 205, 86, 0.8)'
      ]

      try {
        this.charts[chartKey] = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Personas',
              data: chartData,
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
                    return `Cantidad: ${value}`
                  }
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
        console.log(`Age chart created successfully for zone ${zone}`)
      } catch (error) {
        console.error(`Error creating age chart for zone ${zone}:`, error)
      }
    },

    destroyCharts() {
      // Destruir todos los gráficos de todas las zonas
      Object.values(this.charts).forEach(chart => {
        if (chart) {
          try {
            chart.destroy()
          } catch (e) {
            console.warn('Error destroying chart:', e)
          }
        }
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
        '0-15': '0-15 años',
        '16-30': '16-30 años',
        '31-45': '31-45 años',
        '46-60': '46-60 años',
        '60+': '60+ años',
        // Legacy mappings
        '0-18': '0-15 años', // Remapeo para datos antiguos
        '19-30': '16-30 años', // Remapeo para datos antiguos
        '19-35': '16-30 años', // Remapeo para datos antiguos
        '36-60': '36-60 años',
        'Desconocido': 'Desconocido'
      }
      return ageLabels[age] || age
    }
  },

  beforeUnmount() {
    // Cancelar timeouts pendientes
    if (this.chartCreationTimeout) {
      clearTimeout(this.chartCreationTimeout)
    }
    // Destruir todos los gráficos
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

/* Estilos para el sistema de pestañas */
.tabs-container {
  margin-bottom: 30px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.tabs {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.tab-button {
  padding: 15px 30px;
  border: 2px solid #ddd;
  background: white;
  color: #666;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s;
}

.tab-button:hover {
  background: #f8f9fa;
  border-color: #007bff;
  color: #007bff;
}

.tab-button.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.zone-content {
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.zone-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .zone-charts {
    grid-template-columns: 1fr;
  }
}

.zone-details-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

@media (max-width: 768px) {
  .zone-details-section {
    grid-template-columns: 1fr;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.no-data-zone {
  text-align: center;
  padding: 60px;
  color: #666;
  font-size: 1.2em;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
</style>
