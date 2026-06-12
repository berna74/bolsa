<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const groups = ref([])
const searchTerm = ref('')
const selectedCity = ref('all')

function rubroSlug(rubro) {
  return rubro
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

function formatRubroLabel(rubro) {
  const value = (rubro || '').trim()
  if (!value) {
    return ''
  }

  if (/os$/i.test(value)) {
    return `${value}/as`
  }

  if (/as$/i.test(value)) {
    return `${value}/os`
  }

  if (/o$/i.test(value)) {
    return `${value.slice(0, -1)}os/as`
  }

  if (/a$/i.test(value)) {
    return `${value.slice(0, -1)}as/os`
  }

  if (/s$/i.test(value)) {
    return value
  }

  if (/[aeiouaeiou]$/i.test(value)) {
    return `${value}s`
  }

  return `${value}es`
}

const currentGroup = computed(() => {
  return groups.value.find((group) => rubroSlug(group.rubro) === route.params.slug)
})

const availableCities = computed(() => {
  const cities = new Set()
  for (const worker of currentGroup.value?.workers || []) {
    const city = (worker.city || '').trim()
    if (city) {
      cities.add(city)
    }
  }
  return [...cities].sort((a, b) => a.localeCompare(b, 'es'))
})

const filteredWorkers = computed(() => {
  if (!currentGroup.value) {
    return []
  }

  let workers = currentGroup.value.workers

  if (selectedCity.value !== 'all') {
    workers = workers.filter((worker) => (worker.city || '').trim() === selectedCity.value)
  }

  const term = searchTerm.value.trim().toLowerCase()
  if (!term) {
    return workers
  }

  return workers.filter((worker) => worker.full_name.toLowerCase().includes(term))
})

function sanitizePhone(phone) {
  return (phone || '').replace(/[^\d+]/g, '')
}

function whatsappLink(phone, name) {
  const cleanPhone = sanitizePhone(phone)
  if (!cleanPhone) {
    return ''
  }
  const message = encodeURIComponent(`Hola ${name}, vi tu perfil en ConTodoGusto y me gustaría contactarte.`)
  return `https://wa.me/${cleanPhone}?text=${message}`
}

function emailLink(email, name) {
  if (!email) {
    return ''
  }
  const subject = encodeURIComponent('Contacto laboral desde ConTodoGusto')
  const body = encodeURIComponent(`Hola ${name}, vi tu perfil y me gustaría conversar sobre una oportunidad laboral.`)
  return `mailto:${email}?subject=${subject}&body=${body}`
}

async function fetchWorkersByRole() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/public/workers-by-role/')
    groups.value = data
  } catch {
    error.value = 'No se pudo cargar la información del rubro.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchWorkersByRole)
</script>

<template>
  <section class="panel detail-panel">
    <p v-if="loading">Cargando rubro...</p>
    <p v-else-if="error" class="error-text">{{ error }}</p>

    <template v-else-if="currentGroup">
      <div class="detail-header">
        <router-link class="secondary-btn" to="/">Volver al inicio</router-link>
        <h2>{{ formatRubroLabel(currentGroup.rubro) }}</h2>
        <p>{{ currentGroup.workers.length }} trabajadores publicados</p>
      </div>

      <div class="home-filters">
        <label class="search-label">
          Buscar trabajador en este rubro
          <input v-model="searchTerm" type="search" placeholder="Ej: Maria Gomez" />
          <small class="field-hint">Ejemplo de búsqueda dentro del rubro.</small>
        </label>
        <label class="search-label">
          Filtrar por ciudad
          <select v-model="selectedCity">
            <option value="all">Todas las ciudades</option>
            <option v-for="city in availableCities" :key="city" :value="city">
              {{ city }}
            </option>
          </select>
        </label>
      </div>

      <p v-if="!filteredWorkers.length" class="empty-state">No hay resultados para esa búsqueda.</p>

      <div class="role-grid">
        <article v-for="worker in filteredWorkers" :key="worker.id" class="role-card">
          <div class="worker-row">
            <img
              v-if="worker.personal_photo_url"
              :src="worker.personal_photo_url"
              :alt="`Foto de ${worker.full_name}`"
              class="worker-photo"
            />
            <div v-else class="worker-photo worker-photo-placeholder" aria-hidden="true">
              {{ worker.full_name.charAt(0).toUpperCase() }}
            </div>
            <div class="worker-meta">
              <router-link class="worker-link" :to="`/trabajador/${worker.id}`">
                <strong>{{ worker.full_name }}</strong>
              </router-link>
              <span>{{ worker.city || 'Ciudad no indicada' }}</span>
              <span>{{ worker.years_experience }} años de experiencia</span>
              <span v-if="worker.availability">Disponibilidad: {{ worker.availability }}</span>
              <div class="worker-actions">
                <a
                  v-if="whatsappLink(worker.phone, worker.full_name)"
                  :href="whatsappLink(worker.phone, worker.full_name)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="contact-btn"
                  aria-label="Contactar por WhatsApp"
                  title="WhatsApp"
                >
                  <svg class="btn-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M12 3a8.5 8.5 0 00-7.302 12.87L4 21l5.305-1.659A8.5 8.5 0 1012 3z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M9.2 9.8c.2-.4.5-.4.7-.4h.6c.2 0 .4.1.5.3l.5 1.1c.1.2 0 .4-.1.5l-.4.6c.5.9 1.2 1.5 2 2l.6-.4c.2-.1.4-.2.6-.1l1.1.5c.2.1.3.3.3.5v.6c0 .2 0 .5-.4.7-.7.3-1.5.3-2.2 0-2-.8-3.6-2.4-4.4-4.4-.3-.7-.3-1.5 0-2.2z"
                      fill="currentColor"
                    />
                  </svg>
                </a>
                <a
                  v-if="emailLink(worker.email, worker.full_name)"
                  :href="emailLink(worker.email, worker.full_name)"
                  class="contact-btn"
                  aria-label="Contactar por Email"
                  title="Email"
                >
                  <svg class="btn-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <path
                      d="M4 6h16v12H4z"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M4 7l8 6 8-6"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </article>
      </div>
    </template>

    <template v-else>
      <h2>Rubro no encontrado</h2>
      <p>Este rubro no existe o no tiene trabajadores cargados en este momento.</p>
      <router-link class="secondary-btn" to="/">Volver al inicio</router-link>
    </template>
  </section>
</template>
