<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';

const selectedFile = ref(null);
const task_id = ref('');
const taskStatus = ref({});
const isProcessing = ref(false);
const errorMessage = ref('');
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
      <h1>Video Person Counter</h1>
      <p>Sube un video para contar las personas que entran en zonas predefinidas.</p>
    </header>
    
    <div class="upload-section">
      <input type="file" @change="handleFileChange" accept="video/*" :disabled="isProcessing" />
      <button @click="startProcessing" :disabled="isProcessing">
        {{ isProcessing ? 'Procesando...' : 'Iniciar Análisis' }}
      </button>
    </div>

    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <div v-if="task_id" class="status-section">
      <h2>Estado del Procesamiento</h2>
      <p><strong>Task ID:</strong> {{ task_id }}</p>
      <p><strong>Estado:</strong> {{ taskStatus.status || 'iniciando...' }}</p>

      <div v-if="taskStatus.status === 'processing'">
        <progress :value="taskStatus.progress" :max="taskStatus.total_frames"></progress>
        <span>{{ progressPercentage }}%</span>
        <p>Procesando frame {{ taskStatus.progress }} de {{ taskStatus.total_frames }}</p>
      </div>

      <div v-if="taskStatus.status === 'completed'" class="results">
        <h3>¡Procesamiento Completo!</h3>
        <p>Descarga tus resultados:</p>
        <a :href="`${API_URL}${taskStatus.results.video_url}`" download>Descargar Video Procesado (MP4)</a>
        <br>
        <a :href="`${API_URL}${taskStatus.results.csv_url}`" download>Descargar Datos (CSV)</a>
      </div>
      
      <div v-if="taskStatus.status === 'failed'" class="error-message">
        <h3>Error en el procesamiento</h3>
        <p>{{ taskStatus.error }}</p>
      </div>
    </div>
  </main>
</template>

<style>
:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  background-color: #242424;
  color: rgba(255, 255, 255, 0.87);
}
.container {
  max-width: 720px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #444;
  border-radius: 8px;
}
.upload-section, .status-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #2f2f2f;
  border-radius: 8px;
}
button {
  margin-left: 1rem;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  border: 1px solid transparent;
  cursor: pointer;
}
button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
.results a {
  display: inline-block;
  margin-top: 0.5rem;
  color: #646cff;
}
.error-message {
  color: #ff6666;
  margin-top: 1rem;
}
progress {
  width: 90%;
  margin-right: 10px;
}
</style>