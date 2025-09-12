<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';
import AnalyticsDashboard from './components/AnalyticsDashboard.vue';

const selectedFile = ref(null);
const task_id = ref('');
const taskStatus = ref({});
const isProcessing = ref(false);
const errorMessage = ref('');
const activeTab = ref('upload'); // 'upload' o 'dashboard'
let pollingInterval = null;

const API_URL = 'http://127.0.0.1:8000'; // URL de tu backend FastAPI

// Propiedad computada para mostrar el progreso
const progressPercentage = computed(() => {
  if (taskStatus.value.status === 'processing' && taskStatus.value.total_frames > 0) {
    return ((taskStatus.value.progress / taskStatus.value.total_frames) * 100).toFixed(2);
  }
  return 0;
});

function handleFileChange(event) {
  selectedFile.value = event.target.files[0];
  resetState();
}

function resetState() {
  task_id.value = '';
  taskStatus.value = {};
  isProcessing.value = false;
  errorMessage.value = '';
  if (pollingInterval) clearInterval(pollingInterval);
}

async function startProcessing() {
  if (!selectedFile.value) {
    errorMessage.value = 'Por favor, selecciona un archivo de video.';
    return;
  }

  const formData = new FormData();
  formData.append('file', selectedFile.value);
  isProcessing.value = true;
  errorMessage.value = '';

  try {
    const response = await axios.post(`${API_URL}/upload-and-process/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    task_id.value = response.data.task_id;
    taskStatus.value = { status: 'pending' };
    pollStatus();

  } catch (error) {
    console.error('Error al subir el video:', error);
    errorMessage.value = 'Error al iniciar el procesamiento. Revisa la consola del navegador.';
    isProcessing.value = false;
  }
}

function pollStatus() {
  pollingInterval = setInterval(async () => {
    try {
      const response = await axios.get(`${API_URL}/status/${task_id.value}`);
      taskStatus.value = response.data;
      
      if (taskStatus.value.status === 'completed' || taskStatus.value.status === 'failed') {
        clearInterval(pollingInterval);
        isProcessing.value = false;
      }
    } catch (error) {
      console.error('Error al obtener el estado:', error);
      errorMessage.value = 'No se pudo obtener el estado del procesamiento.';
      isProcessing.value = false;
      clearInterval(pollingInterval);
    }
  }, 2000); // Consulta el estado cada 2 segundos
}
</script>

<template>
  <main class="container">
    <header>
      <h1>🎯 People Tracking System</h1>
      <p>Sistema avanzado de seguimiento y análisis de personas con YOLO v8</p>
    </header>

    <!-- Navegación por pestañas -->
    <nav class="tab-navigation">
      <button 
        @click="activeTab = 'upload'" 
        :class="{ active: activeTab === 'upload' }"
        class="tab-button"
      >
        📤 Procesar Video
      </button>
      <button 
        @click="activeTab = 'dashboard'" 
        :class="{ active: activeTab === 'dashboard' }"
        class="tab-button"
      >
        📊 Dashboard Analytics
      </button>
    </nav>

    <!-- Contenido de la pestaña Upload -->
    <div v-if="activeTab === 'upload'" class="tab-content">
      <div class="upload-section">
        <h2>🎬 Subir y Procesar Video</h2>
        <input type="file" @change="handleFileChange" accept="video/*" :disabled="isProcessing" />
        <button @click="startProcessing" :disabled="isProcessing">
          {{ isProcessing ? 'Procesando...' : 'Iniciar Análisis' }}
        </button>
      </div>

      <div v-if="errorMessage" class="error-message">
        ❌ {{ errorMessage }}
      </div>

      <div v-if="task_id" class="status-section">
        <h2>📋 Estado del Procesamiento</h2>
        <p><strong>Task ID:</strong> {{ task_id }}</p>
        <p><strong>Estado:</strong> {{ taskStatus.status || 'iniciando...' }}</p>

        <div v-if="taskStatus.status === 'processing'">
          <progress :value="taskStatus.progress" :max="taskStatus.total_frames"></progress>
          <span>{{ progressPercentage }}%</span>
          <p>Procesando frame {{ taskStatus.progress }} de {{ taskStatus.total_frames }}</p>
        </div>

        <div v-if="taskStatus.status === 'completed'" class="results">
          <h3>✅ ¡Procesamiento Completo!</h3>
          <p>Descarga tus resultados:</p>
          <div class="download-buttons">
            <a :href="`${API_URL}/download/video/${task_id}`" download class="download-btn">
              🎬 Video Procesado (MP4)
            </a>
            <a :href="`${API_URL}/download/csv/${task_id}`" download class="download-btn">
              📊 Datos CSV
            </a>
          </div>
          <div class="analyze-suggestion">
            <p>💡 <strong>¡Analiza tus datos!</strong></p>
            <button @click="activeTab = 'dashboard'" class="analyze-btn">
              Ver Dashboard de Analytics
            </button>
          </div>
        </div>
        
        <div v-if="taskStatus.status === 'failed'" class="error-message">
          <h3>❌ Error en el procesamiento</h3>
          <p>{{ taskStatus.error }}</p>
        </div>
      </div>
    </div>

    <!-- Contenido de la pestaña Dashboard -->
    <div v-if="activeTab === 'dashboard'" class="tab-content">
      <AnalyticsDashboard />
    </div>
  </main>
</template>

<style>
:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  color: rgba(255, 255, 255, 0.95);
}

body {
  margin: 0;
  padding: 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

header h1 {
  font-size: 3rem;
  margin: 0 0 1rem 0;
  background: linear-gradient(45deg, #ffd700, #ff6b6b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

header p {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0;
}

.tab-navigation {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
  gap: 1rem;
}

.tab-button {
  padding: 1rem 2rem;
  border: none;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.tab-button:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  transform: translateY(-2px);
}

.tab-button.active {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.tab-content {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-height: 400px;
}

.upload-section, .status-section {
  margin-bottom: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.upload-section h2, .status-section h2 {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  color: #ffd700;
}

input[type="file"] {
  margin-right: 1rem;
  padding: 0.8rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
}

button {
  padding: 1rem 2rem;
  border-radius: 12px;
  border: none;
  background: linear-gradient(45deg, #ff6b6b, #ffd700);
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
}

.results {
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid rgba(76, 175, 80, 0.5);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.results h3 {
  margin: 0 0 1rem 0;
  color: #4caf50;
}

.download-buttons {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
  flex-wrap: wrap;
}

.download-btn {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  background: linear-gradient(45deg, #4caf50, #45a049);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
}

.analyze-suggestion {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 8px;
  text-align: center;
}

.analyze-btn {
  background: linear-gradient(45deg, #ffd700, #ff8c00);
  margin-top: 0.5rem;
}

.error-message {
  background: rgba(244, 67, 54, 0.2);
  border: 1px solid rgba(244, 67, 54, 0.5);
  color: #ff5722;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

progress {
  width: 80%;
  height: 20px;
  margin-right: 1rem;
  border-radius: 10px;
  appearance: none;
}

progress::-webkit-progress-bar {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}

progress::-webkit-progress-value {
  background: linear-gradient(45deg, #4caf50, #45a049);
  border-radius: 10px;
}

/* Responsive design */
@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }
  
  header h1 {
    font-size: 2rem;
  }
  
  .tab-navigation {
    flex-direction: column;
    align-items: center;
  }
  
  .tab-button {
    width: 200px;
  }
  
  .download-buttons {
    flex-direction: column;
  }
}
</style>